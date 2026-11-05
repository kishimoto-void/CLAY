#!/usr/bin/env python3
"""Validate a Gamma Index task-profile import packet and produce a plan-only report.

This tool validates local structure, canonical content digest, ID consistency,
and Top Mold version compatibility. It does not connect to Gamma Index,
authenticate a source, enforce permissions, load a profile, or activate it.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover - user-facing CLI condition
    Draft202012Validator = None
    FormatChecker = None

ROOT = Path(__file__).resolve().parents[1]
PACKET_SCHEMA = ROOT / "schemas" / "gamma_import_packet.schema.json"
PROFILE_SCHEMA = ROOT / "schemas" / "task_profile.schema.json"
MAX_INPUT_BYTES = 2_000_000
MAX_SCHEMA_BYTES = 500_000
MAX_JSON_DEPTH = 64
VERSION_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


class DuplicateJSONKeyError(ValueError):
    pass


class JSONNestingDepthError(ValueError):
    pass


def reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def enforce_json_depth(raw: str, limit: int = MAX_JSON_DEPTH) -> None:
    depth = 0
    in_string = False
    escaped = False
    for pos, char in enumerate(raw):
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
            if depth > limit:
                raise JSONNestingDepthError(f"JSON nesting exceeds {limit} at offset {pos}")
        elif char in "]}":
            depth -= 1
            if depth < 0:
                raise ValueError(f"unexpected closing bracket at offset {pos}")
    if in_string or depth != 0:
        raise ValueError("unterminated JSON string or unbalanced container")


def _load_schema(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if len(raw) > MAX_SCHEMA_BYTES:
        raise ValueError(f"schema exceeds {MAX_SCHEMA_BYTES} bytes: {path.name}")
    text = raw.decode("utf-8")
    enforce_json_depth(text)
    schema = json.loads(text, object_pairs_hook=reject_duplicate_json_keys)
    Draft202012Validator.check_schema(schema)
    return schema


def _schema_errors(data: Any, schema: dict[str, Any], label: str) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(data),
        key=lambda e: (list(map(str, e.absolute_path)), e.message),
    )
    return [
        f"{label} schema at {'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}"
        for e in errors
    ]


def canonical_profile_digest(profile: dict[str, Any]) -> str:
    canonical = json.dumps(
        profile,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def validate_task_profile(profile: Any) -> list[str]:
    """Validate an isolated task profile against the packaged profile schema."""
    if Draft202012Validator is None:
        return ["missing dependency: install requirements-dev.txt (jsonschema>=4.21,<5)"]
    try:
        schema = _load_schema(PROFILE_SCHEMA)
    except Exception as exc:
        return [f"could not load profile schema: {type(exc).__name__}: {exc}"]
    return _schema_errors(profile, schema, "profile")


def compose_candidate_overlay(
    base_config: dict[str, Any],
    profile: dict[str, Any],
    requested_task_mode: str,
    built_in_overlay: dict[str, Any] | None = None,
    task_local_overlay: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose a preview without changing config, loading resources, or activating it.

    Order: base defaults -> built-in task overlay -> Gamma profile -> task-local overlay.
    Verification requirements and additive constraints are monotonic unions; later
    layers cannot remove earlier requirements. Other supported preference fields
    use last-applicable-layer precedence.
    """
    profile_errors = validate_task_profile(profile)
    if profile_errors:
        raise ValueError("invalid task profile: " + "; ".join(profile_errors))

    allowed_modes = profile["scope"]["task_modes"]
    if requested_task_mode not in allowed_modes:
        raise ValueError("requested task mode is outside the profile scope")

    defaults = base_config.get("dials", {}).get("defaults")
    if not isinstance(defaults, dict) or not defaults:
        raise ValueError("base config is missing dials.defaults")
    known_dials = set(defaults)
    for name, value in defaults.items():
        if not isinstance(name, str) or type(value) is not int or not 0 <= value <= 100:
            raise ValueError("base config contains an invalid dial")

    layers = [
        ("built_in_task_overlay", built_in_overlay or {}),
        ("gamma_task_profile", profile.get("overlay", {})),
        ("current_task_overlay", task_local_overlay or {}),
    ]
    allowed_layer_keys = {
        "task_mode", "dial_overrides", "output_contract", "workflow_steps",
        "verification_requirements", "additive_constraints"
    }
    allowed_output_keys = {"format", "sections", "citations_required", "tests_required_when_code_changes"}

    candidate: dict[str, Any] = {
        "candidate_status": "COMPOSED_NOT_ACTIVATED",
        "profile_id": profile["profile_id"],
        "profile_version": profile["profile_version"],
        "activation_scope": "current_task_session",
        "task_mode": requested_task_mode,
        "dials": dict(defaults),
        "output_contract": {},
        "workflow_steps": [],
        "verification_requirements": [],
        "additive_constraints": [],
        "applied_layers": ["global_defaults"],
        "activation_status": "NOT_ACTIVATED",
    }

    for layer_name, layer in layers:
        if not isinstance(layer, dict):
            raise ValueError(f"{layer_name} must be an object")
        unknown = set(layer) - allowed_layer_keys
        if unknown:
            raise ValueError(f"{layer_name} contains unsupported keys: {sorted(unknown)}")
        layer_mode = layer.get("task_mode")
        if layer_mode is not None and layer_mode not in allowed_modes:
            raise ValueError(f"{layer_name}.task_mode is outside the profile scope")
        # The explicit current request remains authoritative; layer task_mode is
        # validated as scope metadata, never used to silently change the mode.
        dial_overrides = layer.get("dial_overrides", {})
        if not isinstance(dial_overrides, dict):
            raise ValueError(f"{layer_name}.dial_overrides must be an object")
        for name, value in dial_overrides.items():
            if name not in known_dials or type(value) is not int or not 0 <= value <= 100:
                raise ValueError(f"{layer_name} contains an invalid dial override: {name!r}")
            candidate["dials"][name] = value

        output_contract = layer.get("output_contract", {})
        if not isinstance(output_contract, dict) or set(output_contract) - allowed_output_keys:
            raise ValueError(f"{layer_name}.output_contract contains unsupported fields")
        if "format" in output_contract and output_contract["format"] not in {"markdown", "json", "table", "code", "document", "other"}:
            raise ValueError(f"{layer_name}.output_contract.format is invalid")
        if "sections" in output_contract and (
            not isinstance(output_contract["sections"], list)
            or len(output_contract["sections"]) > 20
            or any(not isinstance(v, str) or not v.strip() for v in output_contract["sections"])
        ):
            raise ValueError(f"{layer_name}.output_contract.sections must be a bounded array of nonblank strings")
        for boolean_field in ("citations_required", "tests_required_when_code_changes"):
            if boolean_field in output_contract and type(output_contract[boolean_field]) is not bool:
                raise ValueError(f"{layer_name}.output_contract.{boolean_field} must be boolean")
        candidate["output_contract"].update(output_contract)

        if "workflow_steps" in layer:
            steps = layer["workflow_steps"]
            if not isinstance(steps, list) or len(steps) > 20:
                raise ValueError(f"{layer_name}.workflow_steps must be an array of at most 20 items")
            seen_step_ids: set[str] = set()
            for step in steps:
                if not isinstance(step, dict) or set(step) - {"step_id", "objective", "required_inputs", "expected_outputs"}:
                    raise ValueError(f"{layer_name}.workflow_steps contains an invalid step object")
                step_id = step.get("step_id")
                objective = step.get("objective")
                if not isinstance(step_id, str) or not re.fullmatch(r"^[a-z0-9][a-z0-9_-]{1,31}$", step_id):
                    raise ValueError(f"{layer_name}.workflow_steps contains an invalid step_id")
                if step_id in seen_step_ids:
                    raise ValueError(f"{layer_name}.workflow_steps contains duplicate step_id: {step_id}")
                seen_step_ids.add(step_id)
                if not isinstance(objective, str) or not objective.strip():
                    raise ValueError(f"{layer_name}.workflow_steps[{step_id}].objective must be nonblank")
                for list_field in ("required_inputs", "expected_outputs"):
                    values = step.get(list_field, [])
                    if not isinstance(values, list) or len(values) > 20 or any(not isinstance(v, str) or not v.strip() for v in values):
                        raise ValueError(f"{layer_name}.workflow_steps[{step_id}].{list_field} is invalid")
            candidate["workflow_steps"] = [dict(step) for step in steps]

        for field in ("verification_requirements", "additive_constraints"):
            values = layer.get(field, [])
            if not isinstance(values, list) or len(values) > 30 or any(not isinstance(value, str) or not value.strip() for value in values):
                raise ValueError(f"{layer_name}.{field} must contain at most 30 nonblank strings")
            for value in values:
                if value not in candidate[field]:
                    candidate[field].append(value)
        candidate["applied_layers"].append(layer_name)

    return candidate


def parse_version(value: str) -> tuple[int, int, int] | None:
    if not isinstance(value, str) or not VERSION_RE.fullmatch(value):
        return None
    return tuple(int(part) for part in value.split("."))  # type: ignore[return-value]


def build_import_plan(
    packet: Any,
    top_mold_version: str = "0.4.3",
    trusted_host_checks: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Return a validation/activation plan; never performs activation.

    Host-check values embedded in ``packet`` are untrusted declarations. Only a
    trusted in-process adapter may pass its independently obtained decisions via
    ``trusted_host_checks``. This helper still does not authenticate that caller.
    """
    if Draft202012Validator is None:
        return {
            "status": "VALIDATOR_UNAVAILABLE",
            "errors": ["missing dependency: install requirements-dev.txt (jsonschema>=4.21,<5)"],
            "execution_status": "NOT_INVOKED",
            "activation_status": "NOT_ACTIVATED",
        }

    try:
        packet_schema = _load_schema(PACKET_SCHEMA)
        profile_schema = _load_schema(PROFILE_SCHEMA)
    except Exception as exc:
        return {
            "status": "SCHEMA_LOAD_FAILED",
            "errors": [f"{type(exc).__name__}: {exc}"],
            "execution_status": "NOT_INVOKED",
            "activation_status": "NOT_ACTIVATED",
        }

    errors: list[str] = []
    if not isinstance(packet, dict):
        errors.append("packet root must be an object")
        return {
            "status": "INVALID",
            "errors": errors,
            "execution_status": "NOT_INVOKED",
            "activation_status": "NOT_ACTIVATED",
        }

    errors.extend(_schema_errors(packet, packet_schema, "packet"))
    profile = packet.get("profile")
    if isinstance(profile, dict):
        errors.extend(_schema_errors(profile, profile_schema, "profile"))

    request = packet.get("request") if isinstance(packet.get("request"), dict) else {}
    retrieval = packet.get("retrieval") if isinstance(packet.get("retrieval"), dict) else {}
    integrity = packet.get("integrity") if isinstance(packet.get("integrity"), dict) else {}
    host = packet.get("host_checks") if isinstance(packet.get("host_checks"), dict) else {}

    if isinstance(profile, dict):
        if request.get("requested_profile_id") != profile.get("profile_id"):
            errors.append("semantic: requested_profile_id does not match returned profile_id")
        allowed_modes = profile.get("scope", {}).get("task_modes", []) if isinstance(profile.get("scope"), dict) else []
        if request.get("requested_task_mode") not in allowed_modes:
            errors.append("scope: requested_task_mode is outside the profile's allowed task_modes")
        overlay_mode = profile.get("overlay", {}).get("task_mode") if isinstance(profile.get("overlay"), dict) else None
        if overlay_mode is not None and overlay_mode not in allowed_modes:
            errors.append("scope: overlay.task_mode is outside the profile's allowed task_modes")
        requested_version = request.get("requested_profile_version")
        if requested_version is not None and requested_version != profile.get("profile_version"):
            errors.append("semantic: requested_profile_version does not match returned profile_version")
        if retrieval.get("retrieval_status") != "received":
            errors.append("semantic: activation packet requires retrieval_status='received'")
        digest = integrity.get("profile_sha256")
        if isinstance(digest, str):
            try:
                actual_digest = canonical_profile_digest(profile)
                if not hmac.compare_digest(digest, actual_digest):
                    errors.append("integrity: profile_sha256 does not match canonical profile content")
            except (TypeError, ValueError) as exc:
                errors.append(f"integrity: profile cannot be canonicalized: {type(exc).__name__}: {exc}")

        current = parse_version(top_mold_version)
        minimum = parse_version(profile.get("compatibility", {}).get("top_mold_min_version", "")) if isinstance(profile.get("compatibility"), dict) else None
        maximum = parse_version(profile.get("compatibility", {}).get("top_mold_max_version", "")) if isinstance(profile.get("compatibility"), dict) else None
        if current is None:
            errors.append("compatibility: invalid CLAY version; expected x.y.z")
        elif minimum is None or maximum is None:
            errors.append("compatibility: invalid profile compatibility range")
        elif minimum > maximum:
            errors.append("compatibility: minimum version is greater than maximum version")
        elif not (minimum <= current <= maximum):
            errors.append(
                f"compatibility: CLAY {top_mold_version} is outside supported range "
                f"{profile['compatibility']['top_mold_min_version']}..{profile['compatibility']['top_mold_max_version']}"
            )

    if request.get("selection_source") != "explicit_user_request":
        errors.append("activation: task profile activation requires an explicit user request in this skeleton")
    if request.get("activation_scope") != "current_task_session":
        errors.append("activation: profile scope must be current_task_session")

    if errors:
        return {
            "status": "INVALID_OR_INCOMPATIBLE",
            "errors": errors,
            "profile_id": profile.get("profile_id") if isinstance(profile, dict) else None,
            "execution_status": "NOT_INVOKED",
            "activation_status": "NOT_ACTIVATED",
            "note": "No profile was loaded or activated.",
        }

    try:
        base_config = json.loads((ROOT / "config" / "top_mold_chatgpt.json").read_text(encoding="utf-8"))
        built_in = base_config.get("task_overlays", {}).get("general", {})
        candidate_preview = compose_candidate_overlay(
            base_config=base_config,
            profile=profile,
            requested_task_mode=request.get("requested_task_mode"),
            built_in_overlay={"dial_overrides": built_in.get("dial_overrides", {})},
            task_local_overlay={},
        )
    except Exception as exc:
        return {
            "status": "CANDIDATE_COMPOSITION_FAILED",
            "errors": [f"{type(exc).__name__}: {exc}"],
            "profile_id": profile.get("profile_id") if isinstance(profile, dict) else None,
            "execution_status": "NOT_INVOKED",
            "activation_status": "NOT_ACTIVATED",
            "note": "No profile was loaded or activated.",
        }

    host_gate = {
        "source_authentication": "not_checked",
        "resource_access": "not_checked",
        "permission": "not_checked",
        "required_capabilities": "not_checked",
    }
    trusted_host_checks_supplied = trusted_host_checks is not None
    host_check_input_errors: list[str] = []
    if trusted_host_checks is not None:
        if not isinstance(trusted_host_checks, dict):
            host_check_input_errors.append("trusted_host_checks must be an object supplied by the trusted host adapter")
        else:
            allowed_host_fields = set(host_gate) | {"evidence_ref"}
            unknown_host_fields = set(trusted_host_checks) - allowed_host_fields
            if unknown_host_fields:
                host_check_input_errors.append(f"unknown trusted-host-check fields: {sorted(unknown_host_fields)}")
            evidence_ref = trusted_host_checks.get("evidence_ref")
            if not isinstance(evidence_ref, str) or not evidence_ref.strip() or len(evidence_ref) > 512:
                host_check_input_errors.append("trusted_host_checks.evidence_ref must be a nonblank reference of at most 512 characters")
            for name in host_gate:
                value = trusted_host_checks.get(name)
                if value not in {
                    "source_authentication": {"not_checked", "verified_by_host", "unverified", "failed"},
                    "resource_access": {"not_checked", "confirmed_by_host", "unavailable", "failed"},
                    "permission": {"not_checked", "approved_by_host", "not_required_by_host", "pending", "denied"},
                    "required_capabilities": {"not_checked", "satisfied_by_host", "missing"},
                }[name]:
                    host_check_input_errors.append(f"invalid trusted-host-check status for {name}")
                else:
                    host_gate[name] = value
    required_capabilities = profile.get("required_capabilities", []) if isinstance(profile, dict) else []
    capability_check_failed = bool(required_capabilities) and host_gate["required_capabilities"] == "missing"
    capability_check_complete = not required_capabilities or host_gate["required_capabilities"] == "satisfied_by_host"
    host_gate_failed = bool(host_check_input_errors) or (
        host_gate["source_authentication"] == "failed"
        or host_gate["resource_access"] in {"unavailable", "failed"}
        or host_gate["permission"] == "denied"
        or capability_check_failed
    )
    host_gate_complete = (
        trusted_host_checks_supplied
        and not host_check_input_errors
        and host_gate["source_authentication"] == "verified_by_host"
        and host_gate["resource_access"] == "confirmed_by_host"
        and host_gate["permission"] in {"approved_by_host", "not_required_by_host"}
        and capability_check_complete
    )
    intent = request.get("activation_intent")
    if intent == "inspect_only":
        status = "VALIDATED_INSPECTION_ONLY"
    elif host_check_input_errors:
        status = "HOST_CHECK_INPUT_INVALID"
    elif capability_check_failed:
        status = "VALIDATED_REQUIRED_CAPABILITY_MISSING"
    elif host_gate_failed:
        status = "VALIDATED_HOST_CHECK_FAILED"
    elif not host_gate_complete:
        status = "VALIDATED_HOST_CHECKS_REQUIRED"
    else:
        status = "VALIDATED_HOST_ACTIVATION_REQUIRED"

    return {
        "status": status,
        "errors": host_check_input_errors,
        "profile_id": profile.get("profile_id"),
        "profile_version": profile.get("profile_version"),
        "clay_version": top_mold_version,
        "top_mold_version": top_mold_version,  # legacy result-field alias
        "activation_scope": "current_task_session",
        "candidate_overlay_preview": candidate_preview,
        "host_checks_as_declared_in_packet": {
            "source_authentication": host.get("source_authentication", "not_checked"),
            "resource_access": host.get("resource_access", "not_checked"),
            "permission": host.get("permission", "not_checked"),
            "required_capabilities": host.get("required_capabilities", "not_checked"),
        },
        "trusted_host_checks_used_for_planning": host_gate if trusted_host_checks_supplied and not host_check_input_errors else None,
        "trusted_host_evidence_ref": trusted_host_checks.get("evidence_ref") if isinstance(trusted_host_checks, dict) else None,
        "trusted_host_checks_supplied_out_of_band": trusted_host_checks_supplied,
        "host_check_claims_authenticated_by_this_tool": False,
        "activation_plan": [
            "Host resolves the exact Gamma resource reference and confirms current availability.",
            "Host authenticates the Gamma source through its trusted adapter; the JSON packet alone is not proof.",
            "Host checks the user approval/permission scope for this task session.",
            "Host confirms every declared required capability is actually available; labels in the profile are not proof.",
            "CLAY stages the profile as a non-authoritative task overlay.",
            "Compose: CLAY base defaults -> built-in task overlay -> selected Gamma overlay -> current task-local instructions.",
            "Reject any attempt to change authority, permissions, safety gates, or host capabilities.",
            "Commit the active overlay atomically; on failure retain the previous active overlay.",
            "Emit PROFILE_ACTIVATED with profile ID/version/digest to Delta only after host confirms activation."
        ],
        "delta_events": [
            "PROFILE_CANDIDATE_RECEIVED",
            "PROFILE_VALIDATED",
            "PROFILE_REJECTED",
            "PROFILE_ACTIVATED (host-confirmed only)",
            "PROFILE_ACTIVATION_FAILED",
            "PROFILE_UPDATE_AVAILABLE",
            "PROFILE_DEACTIVATED"
        ],
        "execution_status": "NOT_INVOKED",
        "activation_status": "NOT_ACTIVATED",
        "host_checks_required": (intent == "activate_after_validation" and not host_gate_complete and not host_gate_failed),
        "host_activation_required": (intent == "activate_after_validation" and host_gate_complete and not host_gate_failed),
        "limits": [
            "This helper does not connect to Gamma Index or authenticate its source.",
            "It does not load, persist, merge, or activate profiles.",
            "Host-check fields in the packet are untrusted declarations; out-of-band host decisions are trusted only by the integrating caller, not authenticated by this helper.",
            "Structural validation and a matching digest do not establish source authenticity or factual correctness."
        ]
    }


def load_packet(path: Path) -> Any:
    with path.open("rb") as handle:
        raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    text = raw.decode("utf-8")
    enforce_json_depth(text)
    return json.loads(text, object_pairs_hook=reject_duplicate_json_keys)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", help="Gamma import packet JSON")
    parser.add_argument("--clay-version", "--top-mold-version", dest="top_mold_version", default="0.4.3", help="target CLAY version (legacy --top-mold-version alias; default: 0.4.3)")
    parser.add_argument("--json", action="store_true", help="emit the complete plan as JSON")
    args = parser.parse_args(argv)
    try:
        packet = load_packet(Path(args.packet))
    except (OSError, UnicodeDecodeError, ValueError, RecursionError) as exc:
        print(f"INPUT ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    plan = build_import_plan(packet, args.top_mold_version)
    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(f"STATUS: {plan['status']}")
        if plan.get("profile_id"):
            print(f"PROFILE: {plan['profile_id']}@{plan.get('profile_version', '?')}")
        for error in plan.get("errors", []):
            print(f"- {error}")
        print(f"EXECUTION: {plan['execution_status']}")
        print(f"ACTIVATION: {plan['activation_status']}")
        print("NOTE: This is a validation/plan-only helper; no Gamma request or activation occurred.")
    return 0 if plan["status"].startswith("VALIDATED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
