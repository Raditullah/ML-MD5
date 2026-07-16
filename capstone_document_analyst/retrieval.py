"""Capstone Track B (M3 + M4) - Semantic retrieval + RAG generation.

M3 (Transformer / language understanding): sentence-transformers encodes
document chunks and queries into dense embeddings for semantic search.

M4 (Generative AI): retrieved chunks are fed as context to an LLM (Groq)
which generates a grounded answer.
"""
import glob
import os

import numpy as np
from sentence_transformers import SentenceTransformer

DOCS_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def load_documents(docs_dir=DOCS_DIR):
    """Loads all .txt files, chunked by paragraph."""
    chunks = []
    for path in sorted(glob.glob(os.path.join(docs_dir, "*.txt"))):
        text = open(path).read()
        doc_name = os.path.basename(path)
        for para in text.split("\n\n"):
            para = para.strip()
            if len(para) > 30:
                chunks.append({"doc": doc_name, "text": para})
    return chunks


def build_index(docs_dir=DOCS_DIR):
    chunks = load_documents(docs_dir)
    model = get_model()
    embeddings = model.encode([c["text"] for c in chunks], convert_to_numpy=True)
    return chunks, embeddings


def search(query, chunks, embeddings, top_k=3):
    model = get_model()
    query_emb = model.encode([query], convert_to_numpy=True)[0]

    # Cosine similarity
    norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_emb)
    sims = (embeddings @ query_emb) / np.clip(norms, 1e-8, None)

    top_idx = np.argsort(-sims)[:top_k]
    return [
        {"doc": chunks[i]["doc"], "text": chunks[i]["text"], "score": float(sims[i])}
        for i in top_idx
    ]


if __name__ == "__main__":
    print("Building semantic index over sample_docs/...")
    chunks, embeddings = build_index()
    print(f"Indexed {len(chunks)} chunks from "
          f"{len(set(c['doc'] for c in chunks))} documents.\n")

    query = "How does AgentFlow train its planner?"
    print(f"Query: {query}\n")
    results = search(query, chunks, embeddings, top_k=3)
    for r in results:
        print(f"[{r['score']:.3f}] {r['doc']}")
        print(f"  {r['text'][:150]}...")
        print()
