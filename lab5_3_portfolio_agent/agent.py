"""Lab 5.3 - Safe tool-calling agent (Plan -> Act -> Observe -> Reflect loop).

Uses a whitelisted tool registry so the agent can never touch anything
outside what is explicitly allowed. Works with any LLM that can be prompted
to reply with strict JSON (tool call or final answer).

Set GROQ_API_KEY to use Groq's free-tier API, or wire up a local model by
replacing `call_llm`.
"""
import json
import math
import os
import subprocess
import time


def _git_status(repo_path="."):
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        return "Not a git repository"
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "status", "--short", "--branch"],
            capture_output=True, text=True, timeout=3,
        )
        return result.stdout.strip() or "Clean working tree"
    except Exception as e:
        return f"git error: {type(e).__name__}: {e}"


def _read_readme(repo_path="."):
    for name in ("README.md", "readme.md", "README.MD", "Readme.md"):
        candidate = os.path.join(repo_path, name)
        if os.path.exists(candidate):
            return open(candidate).read()[:800]
    return "No README found in this directory"


TOOLS = {
    "calculator": lambda expr: str(eval(
        expr, {"__builtins__": {}},
        {"sqrt": math.sqrt, "pi": math.pi, "log": math.log})),

    "read_file": lambda path: open(path).read()[:500]
    if os.path.exists(path) else "File not found",

    "list_dir": lambda path: str(os.listdir(path))
    if os.path.isdir(path) else "Not a directory",

    "word_count": lambda path: str(len(open(path).read().split()))
    if os.path.exists(path) else "File not found",

    # Two custom tools added for this lab
    "line_count": lambda path: str(len(open(path).readlines()))
    if os.path.exists(path) else "File not found",

    "unit_convert_km_to_miles": lambda km: str(float(km) * 0.621371),

    # Portfolio Extension tools: let the agent navigate a git repo
    "git_status": _git_status,
    "read_readme": _read_readme,
}

# Exact argument name for each tool, so the LLM never has to guess.
TOOL_SIGNATURES = {
    "calculator": {"expr": "a Python math expression, e.g. 'sqrt(144) + 10'"},
    "read_file": {"path": "file path to read"},
    "list_dir": {"path": "directory path to list"},
    "word_count": {"path": "file path whose words will be counted"},
    "line_count": {"path": "file path whose lines will be counted"},
    "unit_convert_km_to_miles": {"km": "distance in kilometres (number)"},
    "git_status": {"repo_path": "path to a git repo, e.g. '.'"},
    "read_readme": {"repo_path": "path to a directory containing a README, e.g. '.'"},
}

_tool_docs = "\n".join(
    f'- "{name}": args = {sig}' for name, sig in TOOL_SIGNATURES.items()
)

SYSTEM_PROMPT = f"""You are a helpful agent that solves tasks step by step.

Available tools and their EXACT argument names:
{_tool_docs}

Rules:
- Reply with ONLY a single JSON object, nothing else (no explanation, no markdown fences).
- To call a tool: {{"tool": "<name>", "args": {{"<exact_arg_name>": <value>}}}}
- To finish: {{"final_answer": "<answer>"}}
- Once a tool result gives you enough information to answer, immediately reply
  with final_answer instead of calling more tools.
- If a tool is not in the list above, do not call it — explain why you cannot
  complete that part of the task in your final_answer instead.
"""


def call_llm(history, model="llama-3.1-8b-instant"):
    """Calls Groq's OpenAI-compatible chat API. Requires GROQ_API_KEY."""
    import urllib.request

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set GROQ_API_KEY to run this agent against a real LLM "
            "(https://console.groq.com/keys)."
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0,
    }).encode()

    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Groq's Cloudflare front-end rejects requests with no User-Agent.
            "User-Agent": "Mozilla/5.0 (compatible; lab5-agent/1.0)",
        },
    )
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


def run_agent(llm_fn, task, max_steps=8, timeout_per_tool=3.0, verbose=True):
    history = [{"role": "user", "content": task}]
    for step in range(max_steps):
        response = llm_fn(history)
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            return f"LLM returned invalid JSON at step {step}: {response}"

        if "final_answer" in parsed:
            return parsed["final_answer"]

        tool_name = parsed.get("tool")
        tool_args = parsed.get("args", {})
        if tool_name not in TOOLS:
            result = f"Error: tool '{tool_name}' is not in the whitelist."
        else:
            try:
                start = time.time()
                result = TOOLS[tool_name](**tool_args)
                elapsed = time.time() - start
                if elapsed > timeout_per_tool:
                    result = f"Timeout: tool took {elapsed:.1f}s > {timeout_per_tool}s"
            except Exception as e:
                result = f"Tool error: {type(e).__name__}: {e}"

        history.append({"role": "assistant", "content": response})
        history.append({"role": "user", "content": f"[tool result] {result}"})
        if verbose:
            print(f"[Step {step + 1}] Tool: {tool_name} | Result: {str(result)[:80]}")

    return "Max steps reached without final answer."


if __name__ == "__main__":
    tasks = [
        "What is sqrt(144) + 10?",
        "List the files in the current directory.",
        "Read agent.py and tell me how many words it contains.",
    ]
    for t in tasks:
        print(f"\n=== TASK: {t} ===")
        print(run_agent(call_llm, t))
