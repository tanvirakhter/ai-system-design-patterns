# Reference implementations

One minimal, runnable script per pattern. Each demonstrates the pattern's load-bearing
mechanics in around a hundred lines of standard-library Python - no API keys, no
external services, deterministic output. Where a real system would call a model, the
boundary is marked with a mock so the architecture stays visible.

| Pattern | Script | What it actually runs |
|---|---|---|
| [RAG System Architecture](../rag-system-architecture.md) | `minimal_rag.py` | Structural chunking, hybrid retrieval (TF-IDF + keyword overlap), context assembly with citations under a token budget |
| [Multi-Agent Workflow Architecture](../multi-agent-workflow-architecture.md) | `minimal_agent_workflow.py` | Orchestrator/worker split, context slices, external state, step budget, gated side effect |
| [AI Evaluation Pipeline](../ai-evaluation-pipeline.md) | `minimal_eval_pipeline.py` | Deterministic checks, per-category aggregation, regression gate (non-zero exit on regression) |

```bash
python minimal_rag.py "how are refunds handled for damaged items"
python minimal_agent_workflow.py
python minimal_eval_pipeline.py   # exit code 1 if any category regresses below baseline
```

Deliberately omitted, because they are deployment concerns the docs cover in prose:
real embedding models and vector stores, async execution, retries and tracing, judge
models, and anything requiring credentials. These scripts are the skeleton the
trade-off tables in each doc are arguing about.
