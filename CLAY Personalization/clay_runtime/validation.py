from __future__ import annotations
from pathlib import Path
from typing import Any
from tools.validate_envelope import validate_envelope_data

_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA = _ROOT / "schemas" / "request_envelope.schema.json"

def validate_envelope(data: Any) -> list[str]:
    """Validate the canonical Request Envelope schema and cross-field invariants."""
    return validate_envelope_data(data, _SCHEMA)
