#!/usr/bin/env python3
"""Validate a Request Envelope and render deterministic CLAY adapter context."""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from clay_runtime import ClayRuntime
from tools.validate_envelope import (MAX_INPUT_BYTES, enforce_json_nesting_depth,
                                      reject_duplicate_json_keys)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("envelope", help="JSON Request Envelope")
    ap.add_argument("--config", default=str(ROOT / "config" / "clay_personalization.json"))
    args = ap.parse_args()
    try:
        raw = Path(args.envelope).read_bytes()
        if len(raw) > MAX_INPUT_BYTES: raise ValueError("input exceeds byte limit")
        decoded = raw.decode("utf-8")
        enforce_json_nesting_depth(decoded)
        data = json.loads(decoded, object_pairs_hook=reject_duplicate_json_keys)
        result = ClayRuntime(args.config).prepare(data)
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    if result.status == "INVALID":
        print(json.dumps({"status": result.status, "errors": result.errors}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"status": result.status, "effective_dials": result.effective_dials}, ensure_ascii=False, indent=2))
    if result.adapter_context: print("\n" + result.adapter_context)
    return 0
if __name__ == "__main__": raise SystemExit(main())
