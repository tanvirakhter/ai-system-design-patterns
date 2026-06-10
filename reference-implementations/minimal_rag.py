"""Reference implementation for ../rag-system-architecture.md - illustrative, not production code.

Demonstrates the pattern's moving parts on a 6-document corpus: chunking with
structural boundaries, hybrid retrieval (TF-IDF as the dense proxy, keyword
overlap as the sparse/BM25 proxy), top-k selection, and context assembly with
citations under a token budget. Generation is a mock: the point where a real
system calls an LLM is marked, and everything up to that boundary is real.

Run: python minimal_rag.py "how are refunds handled for damaged items"
"""

from __future__ import annotations

import math
import re
import sys
from collections import Counter

CORPUS = {
    "returns-policy.md": (
        "## Returns\nItems may be returned within 30 days of delivery for a full refund. "
        "Items must be unused and in original packaging.\n"
        "## Damaged items\nIf an item arrives damaged, photograph the damage and contact "
        "support within 7 days. Damaged items are refunded in full including original "
        "shipping; no return postage is required."
    ),
    "shipping.md": (
        "## Delivery times\nStandard delivery takes 3-5 working days. Express delivery is "
        "next working day for orders placed before 2pm.\n"
        "## Tracking\nEvery order receives a tracking code by email at dispatch."
    ),
    "warranty.md": (
        "## Warranty cover\nAll electronics carry a 24-month warranty against manufacturing "
        "defects. Warranty claims require proof of purchase. Accidental damage is not "
        "covered by warranty; see the returns policy for transit damage."
    ),
}

TOKEN_BUDGET = 120  # context window slice reserved for retrieved chunks (words, as a proxy)
TOP_K = 3


def chunk(corpus: dict[str, str]) -> list[dict]:
    """Split on structural boundaries (headings), the doc's first recommendation."""
    chunks = []
    for doc, text in corpus.items():
        for section in re.split(r"(?=## )", text):
            if section.strip():
                heading = section.splitlines()[0].lstrip("# ").strip()
                chunks.append({"doc": doc, "heading": heading, "text": section.strip()})
    return chunks


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def tfidf_score(query: str, chunks: list[dict]) -> list[float]:
    """Dense-retrieval stand-in: cosine over TF-IDF vectors, computed directly."""
    docs = [_tokens(c["text"]) for c in chunks]
    df = Counter(t for d in docs for t in set(d))
    n = len(docs)

    def vec(tokens: list[str]) -> dict[str, float]:
        tf = Counter(tokens)
        return {t: (tf[t] / len(tokens)) * math.log(n / df[t]) for t in tf if t in df and df[t] < n}

    q = vec(_tokens(query))
    scores = []
    for d in docs:
        v = vec(d)
        dot = sum(q[t] * v.get(t, 0.0) for t in q)
        norm = math.sqrt(sum(x * x for x in q.values())) * math.sqrt(sum(x * x for x in v.values()))
        scores.append(dot / norm if norm else 0.0)
    return scores


def keyword_score(query: str, chunks: list[dict]) -> list[float]:
    """Sparse stand-in: exact-term overlap, the thing dense retrieval misses."""
    q = set(_tokens(query))
    return [len(q & set(_tokens(c["text"]))) / len(q) for c in chunks]


def hybrid_retrieve(query: str, chunks: list[dict], k: int = TOP_K) -> list[tuple[float, dict]]:
    dense = tfidf_score(query, chunks)
    sparse = keyword_score(query, chunks)
    fused = [(0.6 * d + 0.4 * s, c) for d, s, c in zip(dense, sparse, chunks)]
    return sorted(fused, key=lambda x: -x[0])[:k]


def assemble_context(ranked: list[tuple[float, dict]], budget: int = TOKEN_BUDGET) -> str:
    """Best chunks first, cited, cut at the budget - the grounding boundary."""
    parts, used = [], 0
    for score, c in ranked:
        size = len(_tokens(c["text"]))
        if used + size > budget:
            break
        parts.append(f"[{c['doc']} - {c['heading']}]\n{c['text']}")
        used += size
    return "\n\n".join(parts)


def mock_generate(query: str, context: str) -> str:
    # A real system sends `context` + `query` to an LLM here, instructed to
    # answer only from the context and cite sources. The mock makes the
    # boundary visible without an API dependency.
    return (
        "(mock generation) Answer the question strictly from the context above, "
        "citing the bracketed sources. Anything not present in the context must "
        "be declared unanswerable."
    )


def main() -> None:
    query = " ".join(sys.argv[1:]) or "how are refunds handled for damaged items"
    chunks = chunk(CORPUS)
    ranked = hybrid_retrieve(query, chunks)

    print(f"Query: {query}\n\nRetrieved (hybrid score, top {TOP_K} of {len(chunks)} chunks):")
    for score, c in ranked:
        print(f"  {score:.3f}  {c['doc']} - {c['heading']}")

    context = assemble_context(ranked)
    print(f"\nAssembled context ({len(_tokens(context))}/{TOKEN_BUDGET} token budget):\n")
    print(context)
    print(f"\n{mock_generate(query, context)}")


if __name__ == "__main__":
    main()
