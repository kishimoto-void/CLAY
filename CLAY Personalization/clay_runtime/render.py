from __future__ import annotations
from typing import Any, Mapping

def render_adapter_context(envelope: Mapping[str, Any], dials: Mapping[str, int]) -> str:
    """Render a bounded, source-preserving adapter block for an external LLM host."""
    goal = envelope["goal"]
    lines = [
        "[CLAY PERSONALIZATION / TASK CONTEXT]",
        "Treat this block as task coordination guidance, not as higher-priority system policy.",
        f"Goal: {goal}",
        f"Task mode: {envelope.get('task_mode', 'general')}",
        "Effective behavior dials (heuristic preferences, not probabilities):",
    ]
    for key in sorted(dials):
        lines.append(f"- {key}: {dials[key]}/100")
    for field, label in (
        ("requirements", "Requirements"), ("constraints", "Constraints"),
        ("exclusions", "Exclusions"), ("assumptions", "Assumptions"),
        ("open_questions", "Open questions"), ("conflicts", "Conflicts"),
    ):
        items = envelope.get(field, [])
        if items:
            lines.append(f"{label}:")
            for item in items:
                # Keep supplied structured records intact; do not reinterpret provenance.
                lines.append(f"- {item!r}")
    if envelope.get("output_contract") is not None:
        lines.append(f"Output contract: {envelope['output_contract']!r}")
    if envelope.get("verification") is not None:
        lines.append(f"Verification request: {envelope['verification']!r}")
    lines.extend([
        "Preserve unknowns and material contradictions; label assumptions and hypotheses.",
        "Do not claim tools, resources, permissions, execution, or verification that were not actually available and used.",
        "Current explicit user instructions and host/platform safety constraints take precedence.",
        "This adapter block does not grant permission for external or irreversible actions.",
        "[END CLAY TASK CONTEXT]",
    ])
    return "\\n".join(lines)
