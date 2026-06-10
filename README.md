# ai-system-design-patterns

A working catalogue of design patterns for production AI systems. Each pattern is written the same way: the problem it solves, the architecture, when to use it (and when not to), the trade-offs you accept, and the failure points seen in practice.

The aim is the level *between* a blog-post diagram and a vendor reference architecture - enough detail to make a real design decision, short enough to read before a design review.

## Patterns

| Pattern | Family | Status |
|---|---|---|
| [RAG System Architecture](rag-system-architecture.md) | `rag-systems/` | Stable, production-proven |
| [Multi-Agent Workflow Architecture](multi-agent-workflow-architecture.md) | `agent-systems/` | Maturing - use with restraint |
| [AI Evaluation Pipeline](ai-evaluation-pipeline.md) | `ai-observability/` + `prompt-pipelines/` | Stable - the difference between a demo and a product |

## Format

Every pattern follows the same six sections:

1. **Problem** - what breaks without this pattern
2. **Architecture** - the components and how they connect
3. **When to use it** - and the cheaper alternative that often suffices
4. **Trade-offs** - what you pay for what you get
5. **Failure points** - where these systems actually break in production
6. **Related patterns** - what to read next

## Planned

- Prompt pipeline versioning and rollout (`prompt-pipelines/`)
- Guardrails and output validation layers (`ai-safety/`)
- Semantic caching for LLM serving (`ai-cost/`)
