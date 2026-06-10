"""Reference implementation for ../multi-agent-workflow-architecture.md - illustrative, not production code.

Demonstrates the pattern's load-bearing rules in ~100 lines:
  - the orchestrator plans and routes; it does not do the work,
  - workers receive a context slice, not the full history,
  - state lives outside the agents in an inspectable store,
  - every loop has a budget,
  - the one irreversible action goes through a gate.

The "LLM" is a deterministic mock behind the same one-method interface a real
provider would implement.

Run: python minimal_agent_workflow.py
"""

from __future__ import annotations

from typing import Protocol

MAX_STEPS = 10  # hard budget: an agent system without limits is an incident waiting


class Provider(Protocol):
    def complete(self, role: str, task: str, context: str) -> str: ...


class MockProvider:
    """Deterministic stand-in keyed on role, so the orchestration is testable offline."""

    def complete(self, role: str, task: str, context: str) -> str:
        if role == "planner":
            return "1. research\n2. draft\n3. review"
        if role == "research":
            return f"NOTES: three sources gathered on '{task}'; one conflict flagged."
        if role == "draft":
            return f"DRAFT v{context.count('REVIEW:') + 1}: summary of '{task}' using the notes."
        if role == "review":
            # Approve only a revised draft, forcing one trip round the loop.
            return "REVIEW: approved" if "v2" in context else "REVIEW: revise - address the flagged conflict"
        raise ValueError(f"unknown role: {role}")


def run(task: str, provider: Provider) -> dict:
    # State lives here, outside any agent: inspectable, survivable, debuggable.
    state: dict = {"task": task, "artifacts": {}, "log": [], "steps": 0}

    def call(role: str, context: str) -> str:
        state["steps"] += 1
        if state["steps"] > MAX_STEPS:
            raise RuntimeError("step budget exceeded - refusing to loop further")
        out = provider.complete(role, task, context)
        state["log"].append((state["steps"], role))
        return out

    # Orchestrator: plans and routes. The plan is data, not prose it acts on itself.
    plan = [step.split(". ", 1)[1] for step in call("planner", "").splitlines()]

    notes = call("research", "")  # context slice: the task only
    state["artifacts"]["notes"] = notes

    draft = call("draft", notes)  # context slice: the notes, not the whole history
    state["artifacts"]["draft"] = draft

    while True:
        verdict = call("review", draft)
        state["artifacts"]["review"] = verdict
        if "approved" in verdict:
            break
        draft = call("draft", f"{notes}\n{verdict}")  # slice: notes + verdict only
        state["artifacts"]["draft"] = draft

    # Gate before the irreversible side effect. A real system replaces this
    # with human approval or strict validation - the point is that publish()
    # is unreachable without passing it.
    if gate(state):
        publish(state["artifacts"]["draft"])
        state["published"] = True

    state["plan"] = plan
    return state


def gate(state: dict) -> bool:
    return "approved" in state["artifacts"].get("review", "")


def publish(draft: str) -> None:
    print(f"PUBLISH (gated side effect): {draft}")


def main() -> None:
    state = run("quarterly incident summary", MockProvider())
    print(f"\nPlan: {state['plan']}")
    print(f"Steps used: {state['steps']}/{MAX_STEPS}")
    print("Trace:", " -> ".join(role for _, role in state["log"]))


if __name__ == "__main__":
    main()
