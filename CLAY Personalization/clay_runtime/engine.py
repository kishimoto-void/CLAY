from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from .config import load_config
from .render import render_adapter_context
from .validation import validate_envelope

@dataclass(frozen=True)
class RuntimeResult:
    status: str
    errors: tuple[str, ...]
    effective_dials: Mapping[str, int] | None = None
    adapter_context: str | None = None

class ClayRuntime:
    """Deterministic envelope-to-adapter pipeline; no natural-language inference."""
    def __init__(self, config_path: str | Path | None = None):
        base = Path(__file__).resolve().parents[1]
        self.config_path = Path(config_path) if config_path else base / "config" / "clay_personalization.json"
        self.config = load_config(self.config_path)

    def prepare(self, envelope: Any) -> RuntimeResult:
        errors = validate_envelope(envelope)
        if errors:
            return RuntimeResult("INVALID", tuple(errors))
        if envelope["readiness"] != "READY":
            return RuntimeResult(envelope["readiness"], ())
        mode = envelope.get("task_mode", "chat")
        domain = {"work": "development", "verify": "general", "design": "development",
                  "research": "learning", "chat": "general"}.get(mode, "general")
        dials = dict(self.config["dials"]["defaults"])
        overlays = self.config.get("task_overlays", {})
        overlay = overlays.get(domain, overlays.get("general", {}))
        if overlay.get("enabled", False):
            dials.update(overlay.get("dial_overrides", {}))
        context = render_adapter_context(envelope, dials)
        return RuntimeResult("PREPARED", (), dials, context)
