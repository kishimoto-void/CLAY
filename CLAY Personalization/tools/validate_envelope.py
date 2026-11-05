#!/usr/bin/env python3
"""Validate a Top Mold request envelope (schema + cross-field invariants).

This helper validates data contracts only. It is not an LLM runtime, prompt
injection detector, permission system, or factuality verifier.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by CLI users without dependency
    Draft202012Validator = None

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "schemas" / "request_envelope.schema.json"
MAX_INPUT_BYTES = 2_000_000  # Bound CLI input before JSON parsing.
MAX_SCHEMA_BYTES = 500_000  # Bound externally supplied schema files.
MAX_JSON_DEPTH = 64  # Reject deeply nested input before invoking the JSON decoder.
ID_LISTS = ("requirements", "constraints", "exclusions", "assumptions", "open_questions", "transformations", "conflicts")


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object contains a repeated key."""


class JSONNestingDepthError(ValueError):
    """Raised when JSON structure exceeds the configured nesting limit."""


def enforce_json_nesting_depth(text: str, max_depth: int = MAX_JSON_DEPTH) -> None:
    """Count JSON containers while ignoring braces/brackets inside strings."""
    depth = 0
    in_string = False
    escaped = False
    for position, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "[{":
            depth += 1
            if depth > max_depth:
                raise JSONNestingDepthError(
                    f"JSON nesting depth exceeds {max_depth} at character {position}"
                )
        elif char in "]}":
            depth -= 1


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Build an object while rejecting ambiguous repeated member names."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def validate_envelope_data(data: Any, schema_path: Path | str = DEFAULT_SCHEMA) -> list[str]:
    """Return schema and semantic errors without crashing on malformed roots."""
    if Draft202012Validator is None:
        return ["missing dependency: install requirements-dev.txt (jsonschema>=4.21,<5)"]
    try:
        schema_raw = Path(schema_path).read_bytes()
        if len(schema_raw) > MAX_SCHEMA_BYTES:
            raise ValueError(f"schema file exceeds {MAX_SCHEMA_BYTES} byte limit")
        schema_text = schema_raw.decode("utf-8")
        enforce_json_nesting_depth(schema_text)
        schema = json.loads(
            schema_text,
            object_pairs_hook=reject_duplicate_json_keys,
        )
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
    except Exception as exc:  # Invalid schema files must fail closed for library callers too.
        return [f"could not load valid schema: {type(exc).__name__}: {exc}"]
    try:
        schema_errors = sorted(validator.iter_errors(data), key=lambda e: (list(map(str, e.absolute_path)), e.message))
    except Exception as exc:  # schema or hostile data should fail closed, not crash caller
        return [f"validation failed safely: {type(exc).__name__}: {exc}"]
    errors = [f"schema at {format_path(e.absolute_path)}: {e.message}" for e in schema_errors]
    if not isinstance(data, dict):
        return errors
    # JSON Schema cannot directly enforce uniqueness of a selected property across
    # several independent arrays, so enforce it explicitly here.
    seen: dict[str, str] = {}
    for list_name in ID_LISTS:
        records = data.get(list_name, [])
        if not isinstance(records, list):
            continue  # schema error already covers this
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            item_id = record.get("id")
            if not isinstance(item_id, str) or not item_id:
                continue
            location = f"{list_name}[{index}].id"
            if item_id in seen:
                errors.append(f"semantic: duplicate record id {item_id!r} at {location}; first used at {seen[item_id]}")
            else:
                seen[item_id] = location
    resource_seen: dict[str, str] = {}
    resource_requests = data.get("resource_requests", [])
    if isinstance(resource_requests, list):
        for index, record in enumerate(resource_requests):
            if not isinstance(record, dict):
                continue
            resource_id = record.get("resource_id")
            if not isinstance(resource_id, str) or not resource_id:
                continue
            location = f"resource_requests[{index}].resource_id"
            if resource_id in resource_seen:
                errors.append(
                    f"semantic: duplicate resource_id {resource_id!r} at {location}; "
                    f"first used at {resource_seen[resource_id]}"
                )
            else:
                resource_seen[resource_id] = location
    return errors


def format_path(path) -> str:
    return ".".join(str(part) for part in path) or "$"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope", help="path to request-envelope JSON")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="path to schema (default: package schema)")
    args = parser.parse_args(argv)
    try:
        # Read at most MAX_INPUT_BYTES + 1 so a very large file is rejected before
        # allocating/parsing its full contents.
        with Path(args.envelope).open("rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            print(f"INPUT ERROR: file exceeds {MAX_INPUT_BYTES} byte limit", file=sys.stderr)
            return 2
        decoded = raw.decode("utf-8")
        enforce_json_nesting_depth(decoded)
        data = json.loads(decoded, object_pairs_hook=reject_duplicate_json_keys)
    except (OSError, UnicodeDecodeError, ValueError, RecursionError) as exc:
        print(f"INPUT ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    errors = validate_envelope_data(data, args.schema)
    if errors:
        print(f"INVALID ({len(errors)} issue(s))")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID: schema and semantic checks passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
