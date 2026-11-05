#!/usr/bin/env python3
"""Validate protected placement of the Gamma/Delta and safety control planes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from safety_plane.topology import validate_topology


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=str(ROOT / "examples/index_states/control_topology.example.json"))
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.path).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"status": "INVALID_INPUT", "error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=2))
        return 2
    errors = validate_topology(config)
    report = {"status": "PASS" if not errors else "FAIL",
              "violation_count": len(errors),
              "violations": [e.as_dict() for e in errors],
              "execution_status": "NOT_INVOKED"}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
