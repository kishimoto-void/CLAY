"""Deterministic tests for the Gamma task-profile bridge; not live Gamma tests."""
from __future__ import annotations
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_gamma_profile import (  # noqa: E402
    MAX_INPUT_BYTES,
    build_import_plan,
    canonical_profile_digest,
    compose_candidate_overlay,
    load_packet,
)


def example_packet():
    return json.loads((ROOT / "examples/gamma_profile_import_packet.example.json").read_text(encoding="utf-8"))


def refresh_digest(packet):
    packet["integrity"]["profile_sha256"] = canonical_profile_digest(packet["profile"])
    return packet


class GammaProfileBridgeTests(unittest.TestCase):
    def test_clay_version_cli_alias(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_gamma_profile.py"),
             str(ROOT / "examples/gamma_profile_import_packet.example.json"), "--clay-version", "0.4.1", "--json"],
            capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("VALIDATED_HOST_CHECKS_REQUIRED", proc.stdout)

    def test_cli_defaults_to_current_clay_version(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools/validate_gamma_profile.py"),
             str(ROOT / "examples/gamma_profile_import_packet.example.json"), "--json"],
            capture_output=True, text=True, timeout=15
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["clay_version"], "0.4.3")

    def test_synthetic_work_packet_is_validated_but_not_activated(self):
        plan = build_import_plan(example_packet(), "0.3.5")
        self.assertEqual(plan["status"], "VALIDATED_HOST_CHECKS_REQUIRED")
        self.assertEqual(plan["profile_id"], "work.general")
        self.assertEqual(plan["clay_version"], "0.3.5")
        self.assertEqual(plan["execution_status"], "NOT_INVOKED")
        self.assertEqual(plan["activation_status"], "NOT_ACTIVATED")
        self.assertFalse(plan["host_check_claims_authenticated_by_this_tool"])
        self.assertFalse(plan["trusted_host_checks_supplied_out_of_band"])
        self.assertTrue(plan["host_checks_required"])
        self.assertFalse(plan["host_activation_required"])

    def test_plan_contains_composed_preview_without_activation(self):
        plan = build_import_plan(example_packet(), "0.3.5")
        preview = plan["candidate_overlay_preview"]
        self.assertEqual(preview["candidate_status"], "COMPOSED_NOT_ACTIVATED")
        self.assertEqual(preview["task_mode"], "work")
        self.assertEqual(preview["dials"]["proactiveness"], 25)
        self.assertEqual(preview["dials"]["verification_strictness"], 90)
        self.assertEqual(preview["output_contract"]["format"], "markdown")
        self.assertEqual(preview["activation_status"], "NOT_ACTIVATED")
        self.assertEqual(plan["activation_status"], "NOT_ACTIVATED")

    def test_overlay_precedence_and_monotonic_constraints(self):
        packet = example_packet()
        profile = packet["profile"]
        base = json.loads((ROOT / "config/top_mold_chatgpt.json").read_text(encoding="utf-8"))
        built_in = {"dial_overrides": {"proactiveness": 30}, "verification_requirements": ["built-in check"]}
        task_local = {
            "dial_overrides": {"proactiveness": 10},
            "output_contract": {"format": "json"},
            "verification_requirements": ["task-local check"],
            "additive_constraints": ["task-local constraint"],
        }
        preview = compose_candidate_overlay(base, profile, "work", built_in, task_local)
        self.assertEqual(preview["dials"]["proactiveness"], 10)
        self.assertEqual(preview["output_contract"]["format"], "json")
        self.assertIn("built-in check", preview["verification_requirements"])
        self.assertIn("task-local check", preview["verification_requirements"])
        self.assertIn("task-local constraint", preview["additive_constraints"])
        self.assertEqual(preview["task_mode"], "work")
        self.assertEqual(preview["applied_layers"], ["global_defaults", "built_in_task_overlay", "gamma_task_profile", "current_task_overlay"])

    def test_composition_does_not_mutate_inputs(self):
        packet = example_packet()
        profile = packet["profile"]
        base = json.loads((ROOT / "config/top_mold_chatgpt.json").read_text(encoding="utf-8"))
        before_base, before_profile = copy.deepcopy(base), copy.deepcopy(profile)
        compose_candidate_overlay(base, profile, "work")
        self.assertEqual(base, before_base)
        self.assertEqual(profile, before_profile)

    def test_composition_rejects_unknown_authority_field(self):
        packet = example_packet()
        profile = copy.deepcopy(packet["profile"])
        profile["overlay"]["permission_overrides"] = {"external_actions": True}
        with self.assertRaisesRegex(ValueError, "invalid task profile"):
            compose_candidate_overlay({}, profile, "work")

    def test_current_task_mode_cannot_be_silently_changed_by_profile(self):
        packet = example_packet()
        profile = packet["profile"]
        base = json.loads((ROOT / "config/top_mold_chatgpt.json").read_text(encoding="utf-8"))
        preview = compose_candidate_overlay(base, profile, "verify")
        self.assertEqual(preview["task_mode"], "verify")

    def test_task_local_layer_is_validated_before_composition(self):
        packet = example_packet()
        profile = packet["profile"]
        base = json.loads((ROOT / "config/top_mold_chatgpt.json").read_text(encoding="utf-8"))
        with self.assertRaisesRegex(ValueError, "unsupported keys"):
            compose_candidate_overlay(base, profile, "work", task_local_overlay={"safety_override": False})

    def test_task_local_workflow_step_ids_must_be_unique(self):
        packet = example_packet()
        profile = packet["profile"]
        base = json.loads((ROOT / "config/top_mold_chatgpt.json").read_text(encoding="utf-8"))
        step = {"step_id": "review", "objective": "Review the result."}
        with self.assertRaisesRegex(ValueError, "duplicate step_id"):
            compose_candidate_overlay(base, profile, "work", task_local_overlay={"workflow_steps": [step, step]})

    def test_host_assertions_do_not_become_authenticated_facts(self):
        packet = example_packet()
        packet["host_checks"] = {
            "source_authentication": "verified_by_host",
            "resource_access": "confirmed_by_host",
            "permission": "approved_by_host",
            "required_capabilities": "satisfied_by_host",
            "evidence_ref": "synthetic-host-result-001",
        }
        plan = build_import_plan(packet, "0.3.5")
        self.assertEqual(plan["status"], "VALIDATED_HOST_CHECKS_REQUIRED")
        self.assertFalse(plan["host_check_claims_authenticated_by_this_tool"])
        self.assertFalse(plan["trusted_host_checks_supplied_out_of_band"])
        self.assertEqual(plan["activation_status"], "NOT_ACTIVATED")
        self.assertFalse(plan["host_activation_required"])
        self.assertTrue(plan["host_checks_required"])

    def test_out_of_band_host_decisions_can_complete_plan_gates(self):
        plan = build_import_plan(example_packet(), "0.3.5", trusted_host_checks={
            "evidence_ref": "host-check-trace-001",
            "source_authentication": "verified_by_host",
            "resource_access": "confirmed_by_host",
            "permission": "approved_by_host",
            "required_capabilities": "satisfied_by_host",
        })
        self.assertEqual(plan["status"], "VALIDATED_HOST_ACTIVATION_REQUIRED")
        self.assertTrue(plan["trusted_host_checks_supplied_out_of_band"])
        self.assertTrue(plan["host_activation_required"])
        self.assertEqual(plan["activation_status"], "NOT_ACTIVATED")
        self.assertEqual(plan["trusted_host_evidence_ref"], "host-check-trace-001")
        self.assertFalse(plan["host_check_claims_authenticated_by_this_tool"])

    def test_non_object_out_of_band_host_decision_fails_closed(self):
        plan = build_import_plan(example_packet(), "0.3.5", trusted_host_checks=["verified_by_host"])
        self.assertEqual(plan["status"], "HOST_CHECK_INPUT_INVALID")
        self.assertFalse(plan["host_activation_required"])

    def test_out_of_band_host_decision_requires_evidence_reference(self):
        plan = build_import_plan(example_packet(), "0.3.5", trusted_host_checks={
            "source_authentication": "verified_by_host",
            "resource_access": "confirmed_by_host",
            "permission": "approved_by_host",
            "required_capabilities": "satisfied_by_host",
        })
        self.assertEqual(plan["status"], "HOST_CHECK_INPUT_INVALID")
        self.assertFalse(plan["host_activation_required"])

    def test_invalid_out_of_band_host_decision_fails_closed(self):
        plan = build_import_plan(example_packet(), "0.3.5", trusted_host_checks={
            "evidence_ref": "host-check-trace-001",
            "source_authentication": "yes_trust_me",
            "resource_access": "confirmed_by_host",
            "permission": "approved_by_host",
            "required_capabilities": "satisfied_by_host",
        })
        self.assertEqual(plan["status"], "HOST_CHECK_INPUT_INVALID")
        self.assertFalse(plan["host_activation_required"])

    def test_digest_mismatch_rejected(self):
        packet = example_packet()
        packet["profile"]["purpose"] += " tampered"
        plan = build_import_plan(packet, "0.3.5")
        self.assertEqual(plan["status"], "INVALID_OR_INCOMPATIBLE")
        self.assertTrue(any("profile_sha256" in item for item in plan["errors"]))

    def test_requested_profile_id_must_match_returned_profile(self):
        packet = example_packet()
        packet["request"]["requested_profile_id"] = "work.specialist"
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("requested_profile_id" in item for item in plan["errors"]))

    def test_requested_profile_version_must_match_returned_version(self):
        packet = example_packet()
        packet["request"]["requested_profile_version"] = "2.0.0"
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("requested_profile_version" in item for item in plan["errors"]))

    def test_incompatible_top_mold_version_rejected(self):
        plan = build_import_plan(example_packet(), "1.0.0")
        self.assertEqual(plan["status"], "INVALID_OR_INCOMPATIBLE")
        self.assertTrue(any("outside supported range" in item for item in plan["errors"]))

    def test_requested_task_mode_must_be_in_profile_scope(self):
        packet = example_packet()
        packet["request"]["requested_task_mode"] = "chat"
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("outside the profile's allowed task_modes" in item for item in plan["errors"]))

    def test_required_capability_missing_blocks_activation(self):
        packet = example_packet()
        packet["host_checks"]["required_capabilities"] = "missing"
        plan = build_import_plan(packet, "0.3.5", trusted_host_checks={
            "evidence_ref": "host-check-trace-001",
            "source_authentication": "verified_by_host",
            "resource_access": "confirmed_by_host",
            "permission": "approved_by_host",
            "required_capabilities": "missing",
        })
        self.assertEqual(plan["status"], "VALIDATED_REQUIRED_CAPABILITY_MISSING")
        self.assertFalse(plan["host_activation_required"])
        self.assertEqual(plan["activation_status"], "NOT_ACTIVATED")

    def test_denied_permission_blocks_activation(self):
        packet = example_packet()
        packet["host_checks"]["permission"] = "denied"
        plan = build_import_plan(packet, "0.3.5", trusted_host_checks={
            "evidence_ref": "host-check-trace-001",
            "source_authentication": "verified_by_host",
            "resource_access": "confirmed_by_host",
            "permission": "denied",
            "required_capabilities": "satisfied_by_host",
        })
        self.assertEqual(plan["status"], "VALIDATED_HOST_CHECK_FAILED")
        self.assertFalse(plan["host_activation_required"])

    def test_failed_source_authentication_blocks_activation(self):
        packet = example_packet()
        packet["host_checks"]["source_authentication"] = "failed"
        plan = build_import_plan(packet, "0.3.5", trusted_host_checks={
            "evidence_ref": "host-check-trace-001",
            "source_authentication": "failed",
            "resource_access": "confirmed_by_host",
            "permission": "approved_by_host",
            "required_capabilities": "satisfied_by_host",
        })
        self.assertEqual(plan["status"], "VALIDATED_HOST_CHECK_FAILED")
        self.assertFalse(plan["host_activation_required"])

    def test_unavailable_required_resource_blocks_before_stage(self):
        packet = example_packet()
        packet["host_checks"]["resource_access"] = "unavailable"
        plan = build_import_plan(packet, "0.3.5", trusted_host_checks={
            "evidence_ref": "host-check-trace-001",
            "source_authentication": "verified_by_host",
            "resource_access": "unavailable",
            "permission": "approved_by_host",
            "required_capabilities": "satisfied_by_host",
        })
        self.assertEqual(plan["status"], "VALIDATED_HOST_CHECK_FAILED")
        self.assertFalse(plan["host_activation_required"])

    def test_host_policy_does_not_silently_activate_profile(self):
        packet = example_packet()
        packet["request"]["selection_source"] = "host_policy"
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("explicit user request" in item for item in plan["errors"]))

    def test_inspect_only_does_not_request_activation(self):
        packet = example_packet()
        packet["request"]["activation_intent"] = "inspect_only"
        plan = build_import_plan(packet, "0.3.5")
        self.assertEqual(plan["status"], "VALIDATED_INSPECTION_ONLY")
        self.assertFalse(plan["host_activation_required"])
        self.assertEqual(plan["activation_status"], "NOT_ACTIVATED")

    def test_profile_cannot_add_authority_or_permission_override_fields(self):
        packet = example_packet()
        packet["profile"]["overlay"]["permission_overrides"] = {"network": "allow"}
        refresh_digest(packet)
        plan = build_import_plan(packet, "0.3.5")
        self.assertEqual(plan["status"], "INVALID_OR_INCOMPATIBLE")
        self.assertTrue(any("permission_overrides" in item for item in plan["errors"]))

    def test_profile_kind_is_task_domain_only(self):
        packet = example_packet()
        packet["profile"]["profile_kind"] = "personal"
        refresh_digest(packet)
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("task_domain" in item for item in plan["errors"]))

    def test_profiles_must_be_current_task_session_only(self):
        packet = example_packet()
        packet["profile"]["scope"]["session_only"] = False
        refresh_digest(packet)
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("True was expected" in item for item in plan["errors"]))

    def test_top_mold_compatibility_range_must_be_ordered(self):
        packet = example_packet()
        packet["profile"]["compatibility"] = {
            "top_mold_min_version": "0.3.9",
            "top_mold_max_version": "0.3.4",
        }
        refresh_digest(packet)
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("minimum version is greater" in item for item in plan["errors"]))

    def test_profile_extra_fields_rejected(self):
        packet = example_packet()
        packet["profile"]["run_shell_command"] = "echo unsafe"
        refresh_digest(packet)
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("run_shell_command" in item for item in plan["errors"]))

    def test_unknown_dial_rejected(self):
        packet = example_packet()
        packet["profile"]["overlay"]["dial_overrides"]["trust_everything"] = 100
        refresh_digest(packet)
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("trust_everything" in item for item in plan["errors"]))

    def test_retrieval_failure_rejected(self):
        packet = example_packet()
        packet["retrieval"]["retrieval_status"] = "unavailable"
        plan = build_import_plan(packet, "0.3.5")
        self.assertTrue(any("retrieval_status='received'" in item for item in plan["errors"]))

    def test_duplicate_json_keys_rejected_by_loader(self):
        raw = '{"schema_version":"x","schema_version":"y"}'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.json"
            path.write_text(raw, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_packet(path)

    def test_excessively_large_input_rejected_before_parse(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "large.json"
            path.write_bytes(b" " * (MAX_INPUT_BYTES + 1))
            with self.assertRaises(ValueError):
                load_packet(path)

    def test_profile_example_contains_no_personal_data(self):
        profile = example_packet()["profile"]
        self.assertEqual(profile["profile_kind"], "task_domain")
        self.assertFalse(profile["scope"]["contains_personal_data"])
        self.assertTrue(profile["scope"]["session_only"])

    def test_only_single_gamma_profile_contract_is_declared(self):
        config = json.loads((ROOT / "config/top_mold_chatgpt.json").read_text(encoding="utf-8"))
        bridge = config["gamma_profile_bridge"]
        self.assertFalse(bridge["multiple_gamma_profiles_active_per_task"])
        self.assertFalse(bridge["auto_activation"])
        self.assertEqual(bridge["activation_scope"], "current_task_session_only")
        self.assertEqual(bridge["selection_mode"], "explicit_user_request_only")


if __name__ == "__main__":
    unittest.main()
