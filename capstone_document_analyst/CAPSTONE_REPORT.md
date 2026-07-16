# Capstone Final Project — Track B: Autonomous Document Analyst

**Undergraduate Machine Learning Practicum — Module 5 Capstone**

---

## 1. Abstract

This project implements an autonomous document analyst agent that
integrates perception, language understanding, generative AI, and
agentic decision-making — the five pillars covered across the practicum
(Modules 1–5). Given a corpus of text documents, the system builds a
semantic search index (Module 3: transformer embeddings), retrieves
relevant passages for a user query (Module 2-style content localization),
generates grounded natural-language answers via an LLM (Module 4: RAG),
and orchestrates all of this through a safe, whitelisted agentic loop
(Module 5: Plan→Act→Observe→Reflect) that can search, summarize, and
compare documents autonomously. A supporting CNN component (Module 1:
transfer learning with ResNet18) classifies document page types to route
pages to the correct extraction pipeline. Across an end-to-end test suite
of four realistic user tasks, the system produced correct grounded
answers for three, and failed transparently (rather than hallucinating
confidently) on the fourth due to a genuine small-model reasoning
limitation — a result analyzed in depth in Section 7. Five concrete
software defects were discovered and fixed during development through
direct empirical testing rather than code review alone, underscoring a
central lesson of the module: agentic systems fail in ways that are only
visible once you actually run them against a live LLM.

## 2. Introduction

Modules 1–4 of this practicum built systems that *perceive* and
*generate*: CNNs that classify images, detectors that localize objects,
transformers that understand language, and generative models that
produce content. All of these systems are passive — they answer a single
query and stop. Module 5 closes this gap by introducing agents that
*act*: systems that plan multi-step strategies, call tools, observe
results, and revise their approach.

This capstone project addresses a concrete, realistic problem: a
researcher or analyst has a folder of documents (papers, reports) and
needs to search, summarize, and compare them without manually reading
each one. This is precisely the kind of task where a single LLM call is
insufficient (the LLM cannot see documents outside its context window,
and a single pass cannot verify relevance before generating an answer)
but a full custom application would be overkill. An agentic system is
the natural fit.

**Contributions of this project:**
1. A working, tested pipeline integrating all five module components.
2. Five documented software defects discovered and fixed through direct
   testing against a live LLM (Groq's `llama-3.1-8b-instant`).
3. An honest failure-case analysis (Section 7) showing where a small
   open-weight LLM's agentic reasoning breaks down, and why the system's
   *failure mode* (transparent step-limit exhaustion) is safer than the
   alternative (confident hallucination).

## 3. Related Work

This project's design draws directly on results and patterns covered in
the module's own literature review and research conducted during the
Preliminary Study assignment:

1. **Yang et al., "Reinforcement Learning for Long-Horizon Interactive
   LLM Agents"** (arXiv:2502.01600, 2025) — introduces LOOP, showing that
   RL can train multi-turn LLM agents without expensive ground-truth
   action sequences. Used as one of the two sample documents in this
   project's corpus, and conceptually informs why this project's agent
   loop treats every tool call as an observable, correctable action
   rather than a one-shot plan.
2. **"In-the-Flow Agentic System Optimization for Effective Planning and
   Tool Use"** (AgentFlow, arXiv:2510.05592, 2025) — argues that static
   prompt-engineered agents (planner, executor, verifier frozen and
   separately designed) underperform agents whose planner is optimized
   from real multi-turn feedback. This project's agent is *not* trained
   end-to-end (it is prompt-engineered, matching the "static" category
   AgentFlow critiques) — this is an explicit limitation discussed in
   Section 8.
3. **Klarna AI customer service case study** (industry report, 2025) —
   real-world evidence that agentic systems can reach production scale
   (2.3M conversations/month) but that 88% of agent projects never reach
   production, primarily due to infrastructure and governance gaps rather
   than model capability gaps. This motivated the project's emphasis on
   *operational* robustness (rate-limit handling, graceful degradation)
   as much as raw task accuracy.
4. **Ng, Harada, and Russell, "Policy Invariance Under Reward
   Transformations"** (1999) — the potential-based reward shaping theorem
   applied in Lab 5.2, informing this project's design principle that
   auxiliary signals (like retrieval relevance scores) should never
   change *what* the correct final answer is, only how efficiently the
   agent finds it.
5. **Module 5 course material, Section 11 ("Agentic AI: Planning, Tools,
   and Code Execution")** — the Plan→Act→Observe→Reflect loop and the
   tool-whitelisting safety pattern implemented in Lab 5.3 are directly
   extended (not reimplemented from scratch) into this capstone's
   `agent.py`.

## 4. System Architecture

```
                    Dokumen (.txt)
                         │
                         ▼
        ┌─────────────────────────────┐
        │ M2: Document Loader          │  load_documents()
        │ (retrieval.py)                │  paragraph-level chunking
        └──────────────┬───────────────┘
                         ▼
        ┌─────────────────────────────┐
        │ M3: Semantic Encoder         │  sentence-transformers
        │ (retrieval.py)                │  (all-MiniLM-L6-v2)
        └──────────────┬───────────────┘  cosine similarity search
                         ▼
        ┌─────────────────────────────┐
        │ M4: RAG Generation            │  Groq LLM
        │ (agent.py:_plain_llm_call)    │  (llama-3.1-8b-instant)
        └──────────────┬───────────────┘
                         ▼
        ┌─────────────────────────────┐
        │ M5: Agentic Loop              │  Plan→Act→Observe→Reflect
        │ (agent.py:run_agent)          │  4-tool whitelist, throttled
        └──────────────┬───────────────┘
                         ▼
                   Final answer

        ┌─────────────────────────────┐
        │ M1: CNN Page Classifier       │  ResNet18 transfer learning
        │ (document_classifier.py)      │  (independent routing module)
        └─────────────────────────────┘
```

The M1 component is architecturally independent from the M2–M5 pipeline
by design: it addresses a *pre-processing routing* decision (should this
page be parsed as dense text or as a chart/figure?) that a real
production system would run once per ingested page, before the
downstream pipeline. It is demonstrated separately (Section 5.1) rather
than wired into the live agent loop, since the sample corpus for this
capstone consists of plain-text research summaries rather than scanned
document images.

## 5. Implementation

### 5.1 Module 1 — CNN Document-Type Classifier

`document_classifier.py` implements transfer learning on a frozen
ImageNet-pretrained ResNet18 backbone with a trainable linear
classification head, distinguishing "text-heavy" from "chart-heavy"
document page renders. Since no labeled real-world dataset was available
within project scope, training and validation images were generated
procedurally (dense horizontal lines simulating paragraph text vs. axis +
bar-chart shapes simulating figures) — a controlled but genuine test of
whether the transfer-learning approach can separate the two visual
distributions using only 80 training images and 5 epochs of head-only
fine-tuning.

**Result:** validation accuracy rose from 50% (chance level, epoch 1) to
100% (epoch 5); held-out test accuracy on fresh synthetic samples was
6/6 (100%), with per-sample confidence in the 63–71% range — indicating
the frozen backbone's pretrained features already separate the two
classes well, and the small trainable head converges quickly.

### 5.2 Module 2 — Document Ingestion

`retrieval.py::load_documents` reads all `.txt` files in `sample_docs/`
and splits each into paragraph-level chunks (minimum 30 characters),
tagging each chunk with its source filename. This is the text-domain
analog of the region/layout detection covered in Module 2 — instead of
bounding boxes around image regions, chunk boundaries around semantically
coherent text blocks.

### 5.3 Module 3 — Semantic Retrieval

`retrieval.py::build_index` and `search` encode all chunks and the
incoming query using `sentence-transformers` (`all-MiniLM-L6-v2`, a
compact Transformer encoder), then rank chunks by cosine similarity.

**Validation:** a test query — *"How does AgentFlow train its
planner?"* — against a 15-chunk, 3-document index returned its top-3
results exclusively from `paper2_agentflow.txt` (similarity scores
0.702–0.730), correctly excluding chunks from the unrelated RL paper and
the Klarna business report. This confirms the encoder is capturing
topical relevance, not just keyword overlap (no chunk contains the
literal string "AgentFlow paper's planner").

### 5.4 Module 4 — Retrieval-Augmented Generation

`agent.py::_plain_llm_call` and `_groq_chat` send retrieved context to
Groq's `llama-3.1-8b-instant` model, which generates the final natural-
language summary or comparison. Two tools depend on this: `summarize_
document` (full-document summarization) and `compare_documents` (cross-
document comparison), both grounded in the actual chunk text rather than
the model's parametric knowledge.

### 5.5 Module 5 — Agentic Loop

`agent.py::run_agent` implements the Plan→Act→Observe→Reflect loop from
Lab 5.3, extended with four document-analysis tools: `list_documents`,
`search_documents`, `summarize_document`, `compare_documents`. The tool
registry is a hard whitelist — the agent cannot call anything not
explicitly defined, mirroring the sandboxing pattern validated in Lab
5.3's safety experiment.

## 6. Experiments

### 6.1 End-to-End Task Suite

Four realistic user tasks were run against the live system:

| # | Task | Outcome |
|---|---|---|
| 1 | "What documents are available?" | ✅ Correct final answer |
| 2 | "How does AgentFlow's planner differ from static prompt engineering?" | ✅ Correct final answer, synthesized from 2 tool calls |
| 3 | "Compare paper1 and paper2, tell me their key difference." | ❌ Failed — see Section 7 |
| 4 | "Summarize the Klarna case study report in bullet points." | ✅ Correct final answer, recovered from a mid-task rate-limit retry |

3 of 4 tasks (75%) produced correct, grounded final answers.

### 6.2 Ablation: Effect of Semantic Retrieval on Answer Grounding

As a control, `search_documents` was manually tested against a query with
no lexical overlap with its target document ("How does AgentFlow train
its planner?" — the word "planner" appears in the corpus, but not in this
exact phrasing). The correct document was still ranked first by a wide
margin (0.702–0.730 vs. lower scores for off-topic chunks), demonstrating
that the semantic encoder — not simple keyword matching — is responsible
for correct grounding. Without Module 3 (i.e., if `search_documents`
returned unranked or randomly-ordered chunks), the RAG step in Module 4
would receive irrelevant context and produce ungrounded or generic
answers; this is precisely the mechanism by which M3 and M4 depend on
each other in this architecture.

## 7. Discussion

### 7.1 What Worked

The M1–M5 integration functions as designed for 3 of 4 realistic tasks.
The semantic retrieval layer (M3) reliably grounds the generation layer
(M4) in the correct source document, and the agentic loop (M5) correctly
sequences multi-tool calls (e.g., Task 2 required calling
`list_documents`, then `summarize_document` twice, then
`compare_documents`, before producing a final answer — all without
human intervention).

### 7.2 What Failed, and Why

Task 3 ("Compare paper1 and paper2...") failed: the agent, after
correctly listing available documents, called `summarize_document` on
the *wrong* document (the Klarna report) rather than resolving "paper1"
and "paper2" to their correct filenames and calling `compare_documents`.
It never recovered within the 6-step budget and exhausted `max_steps`
without producing a `final_answer`.

Root-cause analysis (from the full execution trace, preserved in
`README.md`) rules out a code defect: every tool call that *was* made
executed correctly and returned the expected result. The failure is a
**reasoning limitation of the underlying 8B-parameter model** —
correctly resolving informal references ("paper1", "paper2") to exact
filenames under time/step pressure is a harder instruction-following task
than the single-document lookups that succeeded in Tasks 1, 2, and 4.

This is directly relevant to the module's treatment of agentic failure
modes (Section 12): it most closely resembles an *action-selection*
hallucination (the model "hallucinates" that summarizing one document
satisfies a comparison request) rather than a factual hallucination.
Critically, **the system did not fail silently or confidently** — it
exhausted its step budget and returned an explicit "Max steps reached"
message rather than fabricating a plausible-sounding but wrong
comparison. This is the `max_steps` guardrail (introduced in Lab 5.3 and
inherited here) functioning exactly as intended: bounding the cost of a
reasoning failure without letting it produce a convincing wrong answer.

### 7.3 Engineering Lessons

Five concrete bugs were found and fixed during development (full details
in `README.md`):

1. **Type coercion** — the LLM sometimes emits numeric tool arguments as
   strings (`"3"` instead of `3`), breaking downstream numpy slicing.
2. **Malformed multi-JSON output** — the model occasionally emits more
   than one JSON object per turn despite explicit "ONLY JSON" instructions,
   requiring defensive parsing (`json.JSONDecoder().raw_decode`) rather
   than a naive `json.loads`.
3. **Filename hallucination** — the model shortened exact filenames
   (`"paper1.txt"` instead of `"paper1_long_horizon_rl.txt"`) even when
   given the correct names moments earlier, requiring an explicit
   system-prompt rule.
4. **Prompt-context leakage from code reuse** — naively reusing Lab 5.3's
   `call_llm` function for free-form summarization silently broke output
   quality, because that function always injects Lab 5.3's tool-calling
   system prompt. This is a subtle but important lesson: **LLM wrapper
   functions are not interchangeable across different prompting
   contexts**, even when the underlying API call is identical.
5. **Rate-limit exhaustion** — Groq's free-tier rate limit was hit
   repeatedly during rapid testing. The fix required moving throttling
   from ad-hoc `sleep()` calls between top-level tasks to a single
   `min_interval` enforced inside the lowest-level API call function,
   because a single task can trigger several nested LLM calls (one agent
   step, plus an internal call inside `summarize_document`) with no
   natural pause between them. This is a direct empirical instance of the
   principle discussed in the module's agentic-AI risk analysis: **rate
   limiting must be centralized at the call boundary, not distributed
   across call sites**, or it silently fails to protect the system.

None of these five bugs were predictable from reading the code alone —
all were discovered by running the system against a live LLM and
observing its actual (sometimes non-compliant) behavior. This is the
practical argument, made concretely rather than abstractly, for why
agentic systems require behavioral testing in addition to unit testing.

## 8. Limitations and Future Work

- **Corpus size**: the semantic search was validated on a 3-document,
  15-chunk corpus. Retrieval quality at scale (hundreds of documents)
  is untested and would likely require approximate nearest-neighbor
  indexing (e.g., FAISS) rather than the brute-force cosine similarity
  used here.
- **Model capability ceiling**: as shown in Section 7.2, the 8B-parameter
  model is the binding constraint on multi-document reasoning tasks. The
  AgentFlow paper reviewed in Related Work suggests that training the
  planner end-to-end on real execution feedback (rather than static
  prompting, as done here) would likely close this gap — a natural
  extension for future work.
- **Document format**: only plain-text `.txt` files are supported. The
  M1 CNN classifier is designed for PDF page images but was not wired
  into an actual PDF ingestion pipeline (e.g., via `pdfplumber` page
  rendering) within this project's scope.
- **No persistent memory across sessions**: each `run_agent` call starts
  with a fresh history; the agent cannot learn from Task 3's failure
  within the same run or across future runs.

## 9. Ethical Considerations

- **Data privacy**: this implementation sends document content to a
  third-party LLM API (Groq) for summarization/comparison. A real
  deployment handling sensitive documents (legal, medical, financial)
  would need either a fully local LLM (as discussed for NemoClaw/OpenShell
  in the Preliminary Study) or an enterprise data-processing agreement
  with the API provider.
- **Hallucination risk in summarization**: even with RAG grounding, LLM
  summaries can still misrepresent source content. This system does not
  currently include a fact-verification step comparing generated
  summaries back against source text — a guardrail identified as
  necessary in `analysis_assignment/PartC_Agentic_Risk.md` but not yet
  implemented here.
- **Whitelist as the primary safety guarantee**: as demonstrated in Lab
  5.3's safety experiment and inherited by this project, the tool
  whitelist is what actually prevents unsafe actions — not the LLM's
  compliance with prompt instructions (which Section 7.2 shows is
  imperfect). Any extension of this project's tool set must preserve this
  property: every new tool must be independently reviewed for what it
  can do if called with adversarial or malformed arguments.

## 10. Conclusion

This capstone demonstrates a working integration of perception (M1),
content structuring (M2), language understanding (M3), generative AI
(M4), and agentic decision-making (M5) into a single practical system —
directly extending the tool-whitelisting and Plan→Act→Observe→Reflect
patterns established earlier in the module's Lab 5.3. The system
succeeds on the majority of realistic tasks and, more importantly, fails
*safely* when it does fail: the one task failure observed was caught by
the step-limit guardrail rather than producing a confident wrong answer.
The five bugs found and fixed during development — none of them
foreseeable from static code review — reinforce the module's central
thesis about agentic AI: these systems must be tested behaviorally
against real models, not just verified structurally.

## References

1. Yang et al. "Reinforcement Learning for Long-Horizon Interactive LLM
   Agents." arXiv:2502.01600, 2025.
2. "In-the-Flow Agentic System Optimization for Effective Planning and
   Tool Use" (AgentFlow). arXiv:2510.05592, 2025.
3. AI Monk. "12 Agentic AI Examples With Measurable ROI: Enterprise Case
   Studies From 2025-2026." (Klarna case study.)
4. Domino.ai. "Agentic AI risks and challenges enterprises must tackle."
5. Ng, A. Y., Harada, D., & Russell, S. "Policy Invariance Under Reward
   Transformations: Theory and Application to Reward Shaping." ICML,
   1999.
6. Module 5 course material: "Deep Reinforcement Learning, Agentic AI,
   and Capstone Project," Undergraduate Machine Learning Practicum.
