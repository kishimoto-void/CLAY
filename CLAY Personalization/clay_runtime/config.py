from __future__ import annotations
import json
from pathlib import Path
from typing import Any

MAX_CONFIG_BYTES = 1_000_000
MAX_DEPTH = 48

class ConfigError(ValueError):
    pass

def _pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ConfigError(f"duplicate JSON key: {k}")
        out[k] = v
    return out

def _depth(raw: str, limit: int = MAX_DEPTH):
    depth = 0
    quoted = escaped = False
    for i, ch in enumerate(raw):
        if quoted:
            if escaped: escaped = False
            elif ch == "\\\\": escaped = True
            elif ch == '"': quoted = False
        elif ch == '"': quoted = True
        elif ch in "[{":
            depth += 1
            if depth > limit: raise ConfigError(f"JSON depth exceeds {limit} at {i}")
        elif ch in "]}": depth -= 1

def load_config(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    raw = p.read_bytes()
    if len(raw) > MAX_CONFIG_BYTES: raise ConfigError("config exceeds byte limit")
    text = raw.decode("utf-8")
    _depth(text)
    try: obj = json.loads(text, object_pairs_hook=_pairs)
    except (UnicodeError, json.JSONDecodeError) as e: raise ConfigError(str(e)) from e
    if not isinstance(obj, dict): raise ConfigError("config root must be an object")
    if obj.get("schema") != "clay-personalization/control/v0.4.3":
        raise ConfigError("unsupported CLAY control schema")
    dials = obj.get("dials", {}).get("defaults", {})
    if not isinstance(dials, dict) or not dials: raise ConfigError("missing dial defaults")
    for key, value in dials.items():
        if not isinstance(key, str) or isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
            raise ConfigError(f"invalid dial default: {key}")
    return obj
