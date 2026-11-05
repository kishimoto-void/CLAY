#!/usr/bin/env python3
"""Validate CLAY module manifests/results. This does not load or execute modules."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_INPUT_BYTES = 1_000_000
MAX_JSON_DEPTH = 48


def _no_duplicate_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _depth(value, level=0):
    if level > MAX_JSON_DEPTH:
        raise ValueError(f"JSON nesting exceeds {MAX_JSON_DEPTH}")
    if isinstance(value, dict):
        for key, item in value.items():
            _depth(key, level + 1)
            _depth(item, level + 1)
    elif isinstance(value, list):
        for item in value:
            _depth(item, level + 1)


def load_json(path: Path):
    data = path.read_bytes()
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    obj = json.loads(data.decode("utf-8"), object_pairs_hook=_no_duplicate_pairs)
    _depth(obj)
    if not isinstance(obj, dict):
        raise ValueError("top-level JSON value must be an object")
    return obj


def _schema_for(kind: str):
    if kind == "manifest":
        return ROOT / "schemas/module_manifest.schema.json"
    if kind == "result":
        return ROOT / "schemas/module_result.schema.json"
    raise ValueError("kind must be manifest or result")


def semantic_errors(obj, kind: str):
    errors = []
    if kind == "manifest":
        caps = obj.get("capabilities", [])
        cap_ids = [
            c.get("capability_id") for c in caps
            if isinstance(c, dict) and isinstance(c.get("capability_id"), str)
        ] if isinstance(caps, list) else []
        if len(cap_ids) != len(set(cap_ids)):
            errors.append("capability_id values must be unique")
        for field in ("out_of_scope", "implementation_modes", "verification_requirements"):
            vals = obj.get(field, [])
            if isinstance(vals, list):
                comparable = [v for v in vals if isinstance(v, (str, int, float, bool))]
                if len(comparable) != len(set(comparable)):
                    errors.append(f"{field} values must be unique")
        behavior = obj.get("behavior_profile") if isinstance(obj.get("behavior_profile"), dict) else {}
        authority = obj.get("authority") if isinstance(obj.get("authority"), dict) else {}
        data_handling = obj.get("data_handling") if isinstance(obj.get("data_handling"), dict) else {}
        if behavior.get("separate_from_capability") is not True:
            errors.append("behavior profile must remain separate from module capability")
        if authority.get("may_modify_common_core") is not False:
            errors.append("module cannot modify Common Core")
        if authority.get("may_disable_safety_plane") is not False:
            errors.append("module cannot disable Safety Plane")
        if authority.get("may_grant_permissions") is not False:
            errors.append("module cannot grant permissions")
        if data_handling.get("persistent_personal_data") is not False:
            errors.append("persistent personal data is outside this package contract")
    elif kind == "result":
        status = obj.get("status")
        # JSON Schema reports malformed status types. Keep semantic checks
        # defensive so adversarial values produce validation errors, not crashes.
        if not isinstance(status, str):
            status = None
        blockers = obj.get("blockers", [])
        blocker_items = [b for b in blockers if isinstance(b, dict)] if isinstance(blockers, list) else []
        blocker_codes = {b.get("code") for b in blocker_items if isinstance(b.get("code"), str)}
        if status in {"BLOCKED", "UNSUPPORTED", "FAILED", "CLARIFICATION_REQUIRED"} and not blocker_items:
            errors.append(f"{status} requires at least one typed blocker")
        if status == "COMPLETED" and blockers:
            errors.append("COMPLETED cannot contain blocking items")
        if status == "COMPLETED" and obj.get("next_action") != "NONE":
            errors.append("COMPLETED requires next_action=NONE")
        verification = obj.get("verification") if isinstance(obj.get("verification"), dict) else {}
        if status == "FAILED" and verification.get("status") == "PASSED":
            errors.append("FAILED cannot report overall verification PASSED")
        if status == "FAILED" and blocker_items and not blocker_codes.intersection({"EXECUTION_ERROR", "VERIFICATION_FAILED", "TIMEOUT", "DEPENDENCY_FAILED", "UNKNOWN_FAILURE"}):
            errors.append("FAILED should identify an attempted execution/dependency/verification failure, not only a prerequisite block")
        if status == "UNSUPPORTED" and blocker_items and "UNSUPPORTED_OPERATION" not in blocker_codes:
            errors.append("UNSUPPORTED requires an UNSUPPORTED_OPERATION blocker")
        if status == "CLARIFICATION_REQUIRED" and blocker_items and not blocker_codes.intersection({"INPUT_MISSING", "CONFLICT_UNRESOLVED"}):
            errors.append("CLARIFICATION_REQUIRED requires INPUT_MISSING or CONFLICT_UNRESOLVED")
    return errors


def validate(path: Path, kind: str):
    try:
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise RuntimeError("jsonschema is required; install requirements-dev.txt") from exc
    obj = load_json(path)
    schema = load_json(_schema_for(kind))
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(obj), key=lambda e: (list(map(str, e.path)), e.message))
    messages = [f"schema {list(e.path)}: {e.message}" for e in errors]
    messages.extend(semantic_errors(obj, kind))
    return messages


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--kind", choices=("manifest", "result"))
    args = parser.parse_args(argv)
    try:
        obj = load_json(args.file)
        kind = args.kind
        if kind is None:
            version = obj.get("schema_version")
            if version == "clay/module-manifest/v1":
                kind = "manifest"
            elif version == "clay/module-result/v1":
                kind = "result"
            else:
                raise ValueError("cannot infer kind from schema_version; use --kind")
        errors = validate(args.file, kind)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"INVALID: {error}")
        return 1
    print(f"VALID: {kind} contract passed ({args.file})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
