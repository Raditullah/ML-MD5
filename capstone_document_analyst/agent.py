"""Capstone Track B - Autonomous Document Analyst (M5: agentic loop).

Follows the same safe whitelist + Plan->Act->Observe->Reflect loop
architecture as the Lab 5.3 agent, backed by the M3 (semantic retrieval) +
M4 (RAG generation) pipeline in retrieval.py.
"""
import json
import os
import time
import urllib.error
import urllib.request

from retrieval import build_index, search, load_documents

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_last_call_time = 0.0


def _groq_chat(messages, model="llama-3.1-8b-instant", max_retries=6, min_interval=2.0):
    """Calls Groq's chat completions API with a minimum spacing between
    requests plus exponential backoff on 429 (rate limit) responses -- a
    concrete guardrail against the 'runaway API cost / rate limiting'
    failure mode discussed in analysis_assignment/PartC_Agentic_Risk.md.

    Throttling lives here (not at the call sites) so every code path that
    talks to Groq -- agent steps, summarize_document, compare_documents --
    is protected uniformly, since a single agent step can trigger a tool
    that itself makes another LLM call."""
    global _last_call_time
    elapsed = time.time() - _last_call_time
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)

    api_key = os.environ.get("GROQ_API_KEY")
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        GROQ_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; capstone-agent/1.0)",
        },
    )
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req) as resp:
                content = json.loads(resp.read())["choices"][0]["message"]["content"]
            _last_call_time = time.time()
            return content
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"  (rate limited, retrying in {wait}s...)")
                time.sleep(wait)
                continue
            raise


def _plain_llm_call(prompt, model="llama-3.1-8b-instant"):
    """Generic free-form LLM call (no tool-calling system prompt) for
    summarization/comparison, where we want natural language output."""
    return _groq_chat([{"role": "user", "content": prompt}], model=model)

print("Building document index...")
_CHUNKS, _EMBEDDINGS = build_index()
print(f"Indexed {len(_CHUNKS)} chunks from "
      f"{len(set(c['doc'] for c in _CHUNKS))} documents.\n")


def _search_documents(query, top_k=3):
    results = search(query, _CHUNKS, _EMBEDDINGS, top_k=int(top_k))
    return json.dumps([
        {"doc": r["doc"], "excerpt": r["text"][:200], "relevance": round(r["score"], 3)}
        for r in results
    ])


def _summarize_document(doc_name):
    docs = load_documents()
    full_text = "\n".join(c["text"] for c in docs if c["doc"] == doc_name)
    if not full_text:
        return f"Document '{doc_name}' not found."
    prompt = f"Summarize this document in 3 bullet points:\n\n{full_text[:2000]}"
    return _plain_llm_call(prompt)


def _compare_documents(doc_a, doc_b):
    docs = load_documents()
    text_a = "\n".join(c["text"] for c in docs if c["doc"] == doc_a)[:1200]
    text_b = "\n".join(c["text"] for c in docs if c["doc"] == doc_b)[:1200]
    if not text_a or not text_b:
        return f"One or both documents not found: '{doc_a}', '{doc_b}'"
    prompt = (
        f"Compare these two documents in 2-3 sentences, focusing on their "
        f"key differences:\n\nDOCUMENT A ({doc_a}):\n{text_a}\n\n"
        f"DOCUMENT B ({doc_b}):\n{text_b}"
    )
    return _plain_llm_call(prompt)


def _list_documents():
    return str(sorted(set(c["doc"] for c in _CHUNKS)))


TOOLS = {
    "search_documents": _search_documents,
    "summarize_document": _summarize_document,
    "compare_documents": _compare_documents,
    "list_documents": _list_documents,
}

TOOL_SIGNATURES = {
    "search_documents": {"query": "semantic search query (string)", "top_k": "number of results, default 3 (optional)"},
    "summarize_document": {"doc_name": "exact filename, e.g. 'paper1_long_horizon_rl.txt'"},
    "compare_documents": {"doc_a": "exact filename of first document", "doc_b": "exact filename of second document"},
    "list_documents": {},
}

_tool_docs = "\n".join(f'- "{name}": args = {sig}' for name, sig in TOOL_SIGNATURES.items())

SYSTEM_PROMPT = f"""You are an autonomous document analyst agent.

Available tools and their EXACT argument names:
{_tool_docs}

Rules:
- Reply with EXACTLY ONE JSON object per turn and NOTHING else -- no
  explanation, no markdown fences, no second JSON object after the first.
- To call a tool: {{"tool": "<name>", "args": {{"<exact_arg_name>": <value>}}}}
- To finish: {{"final_answer": "<answer>"}}
- ALWAYS call list_documents FIRST if you have not already, and use the
  filenames EXACTLY as returned by it -- never guess or shorten a filename
  (e.g. do not write "paper1.txt" if the real name is
  "paper1_long_horizon_rl.txt").
- Use search_documents to find relevant excerpts before answering factual
  questions.
- Once you have enough information, immediately reply with final_answer.
"""


def run_agent(task, max_steps=6, verbose=True):
    history = [{"role": "user", "content": task}]

    for step in range(max_steps):
        response = _groq_chat([{"role": "system", "content": SYSTEM_PROMPT}] + history)
        try:
            # The model sometimes appends extra JSON objects or commentary
            # after the first one despite instructions; parse only the
            # first top-level {...} block.
            decoder = json.JSONDecoder()
            first_brace = response.index("{")
            parsed, _ = decoder.raw_decode(response, first_brace)
        except (json.JSONDecodeError, ValueError):
            return f"Invalid JSON at step {step}: {response}"

        if "final_answer" in parsed:
            return parsed["final_answer"]

        tool_name = parsed.get("tool")
        tool_args = parsed.get("args", {})
        if tool_name not in TOOLS:
            result = f"Error: tool '{tool_name}' not in whitelist."
        else:
            try:
                result = TOOLS[tool_name](**tool_args)
            except Exception as e:
                result = f"Tool error: {type(e).__name__}: {e}"

        history.append({"role": "assistant", "content": response})
        history.append({"role": "user", "content": f"[tool result] {result}"})
        if verbose:
            print(f"[Step {step + 1}] Tool: {tool_name} | Result: {str(result)[:100]}")

    return "Max steps reached without final answer."


if __name__ == "__main__":
    # No manual sleeps needed between tasks: _groq_chat enforces a minimum
    # interval between every Groq API call itself (see min_interval above).
    tasks = [
        "What documents are available?",
        "How does the AgentFlow paper's planner differ from static prompt engineering?",
        "Compare the two research papers (paper1 and paper2) and tell me their key difference.",
        "Summarize the Klarna case study report in bullet points.",
    ]
    for t in tasks:
        print(f"\n=== TASK: {t} ===")
        print(run_agent(t))
