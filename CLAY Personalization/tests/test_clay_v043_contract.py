"""Deterministic CLAY v0.4.3 contract tests; not live model behavior tests."""
from __future__ import annotations
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    Draft202012Validator = None

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_modules import semantic_errors  # noqa: E402


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class ClayV043ContractTests(unittest.TestCase):
    def test_config_names_cp_and_keeps_common_core_invariants(self):
        config = load("config/clay_personalization.json")
        self.assertEqual(config["version"], "0.4.3")
        self.assertEqual(config["schema"], "clay-personalization/control/v0.4.3")
        self.assertEqual(config["common_core"]["contract_version"], "1.1")
        self.assertFalse(config["common_core"]["module_can_override"])
        self.assertTrue(config["common_core"]["safety_plane_is_global_non_delegable"])
        self.assertFalse(config["module_system"]["topic_mention_alone_activates_module"])
        self.assertTrue(config["module_system"]["capability_separate_from_behavior_profile"])
        self.assertFalse(config["optional_multi_model"]["enabled_by_default"])
        self.assertTrue(config["outcome_learning"]["enabled_as_llm_behavior_contract"])
        self.assertFalse(config["outcome_learning"]["autonomous_learner_included"])
        self.assertTrue(config["outcome_learning"]["durable_behavior_profile_requires_explicit_user_confirmation"])
        self.assertTrue(config["outcome_learning"]["outcome_and_process_quality_are_independent"])
        self.assertTrue(config["outcome_learning"]["llm_reviews_own_controllable_choices_first"])
        self.assertTrue(config["outcome_learning"]["process_review_required_for_schema_records"])
        self.assertFalse(config["coexistence"]["fixed_assistant_personality_imposed"])
        self.assertFalse(config["coexistence"]["zero_cognitive_influence_guaranteed"])

    def test_legacy_config_is_byte_equivalent_json_to_canonical(self):
        self.assertEqual(load("config/clay_personalization.json"), load("config/top_mold_chatgpt.json"))

    def test_legacy_prompt_file_is_only_a_compatibility_alias(self):
        text = (ROOT / "TOP_MOLD_CHATGPT.md").read_text(encoding="utf-8")
        self.assertIn("CLAY_PERSONALIZATION.md", text)
        self.assertIn("not a separate control layer", text)

    def test_common_core_includes_constructive_limits(self):
        text = (ROOT / "COMMON_CORE.md").read_text(encoding="utf-8")
        for phrase in ("Hypothesis hold", "Hypothesis answer", "Constructive limit acknowledgement", "Not available here", "Impossible under stated constraints", "resume_condition", "OUTCOME_LEARNING.md", "COEXISTENCE_AND_NON_IMPOSITION.md"):
            self.assertIn(phrase, text)

    def test_module_schema_and_examples_validate(self):
        schema = load("schemas/module_manifest.schema.json")
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        for rel in (
            "examples/modules/code_specialist.example.json",
            "examples/modules/work_workflow.example.json",
            "examples/modules/multi_model_review.example.json",
        ):
            with self.subTest(example=rel):
                obj = load(rel)
                self.assertEqual([], list(validator.iter_errors(obj)))
                self.assertEqual([], semantic_errors(obj, "manifest"))

    def test_manifest_rejects_common_core_override(self):
        obj = load("examples/modules/code_specialist.example.json")
        obj["authority"]["may_modify_common_core"] = True
        schema = load("schemas/module_manifest.schema.json")
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(obj)))
        self.assertTrue(any("cannot modify Common Core" in e for e in semantic_errors(obj, "manifest")))

    def test_manifest_rejects_persona_capability_coupling(self):
        obj = load("examples/modules/code_specialist.example.json")
        obj["behavior_profile"]["separate_from_capability"] = False
        schema = load("schemas/module_manifest.schema.json")
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(obj)))

    def test_manifest_rejects_permission_and_safety_authority(self):
        schema = load("schemas/module_manifest.schema.json")
        base = load("examples/modules/code_specialist.example.json")
        for field in ("may_grant_permissions", "may_disable_safety_plane"):
            obj = copy.deepcopy(base)
            obj["authority"][field] = True
            with self.subTest(field=field):
                self.assertTrue(list(Draft202012Validator(schema).iter_errors(obj)))
                self.assertTrue(semantic_errors(obj, "manifest"))

    def test_result_schema_and_blocked_example_validate(self):
        schema = load("schemas/module_result.schema.json")
        Draft202012Validator.check_schema(schema)
        obj = load("examples/module_results/blocked_integration.example.json")
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(obj)))
        self.assertEqual([], semantic_errors(obj, "result"))

    def test_blocked_result_requires_blocker(self):
        obj = load("examples/module_results/blocked_integration.example.json")
        obj["blockers"] = []
        schema = load("schemas/module_result.schema.json")
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(obj)))
        self.assertTrue(semantic_errors(obj, "result"))

    def test_duplicate_capability_ids_are_rejected_even_when_descriptions_differ(self):
        obj = load("examples/modules/code_specialist.example.json")
        obj["capabilities"].append({"capability_id": "code.design", "description": "A different description."})
        self.assertTrue(semantic_errors(obj, "manifest"))

    def test_unsupported_requires_unsupported_operation_code(self):
        obj = load("examples/module_results/blocked_integration.example.json")
        obj["status"] = "UNSUPPORTED"
        obj["blockers"][0]["code"] = "CAPABILITY_UNAVAILABLE"
        self.assertTrue(semantic_errors(obj, "result"))

    def test_clarification_requires_input_or_conflict_blocker(self):
        obj = load("examples/module_results/blocked_integration.example.json")
        obj["status"] = "CLARIFICATION_REQUIRED"
        obj["blockers"][0]["code"] = "TIMEOUT"
        self.assertTrue(semantic_errors(obj, "result"))

    def test_failed_result_cannot_claim_verification_passed(self):
        obj = load("examples/module_results/blocked_integration.example.json")
        obj["status"] = "FAILED"
        obj["blockers"][0]["code"] = "EXECUTION_ERROR"
        obj["verification"]["status"] = "PASSED"
        self.assertTrue(semantic_errors(obj, "result"))

    def test_completed_result_cannot_have_blockers_or_next_action(self):
        obj = load("examples/module_results/blocked_integration.example.json")
        obj["status"] = "COMPLETED"
        obj["blockers"] = []
        obj["next_action"] = "REQUEST_INPUT"
        self.assertTrue(semantic_errors(obj, "result"))

    def test_module_conformance_cases_are_unique_and_cover_boundaries(self):
        doc = load("tests/module_conformance_cases.json")
        self.assertEqual(doc["status"], "proposed_synthetic_vectors_not_live_llm_results")
        ids = [x["id"] for x in doc["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        required = {"MOD-SELECT-001", "MOD-PERSONA-001", "MOD-LIMIT-001", "MOD-RETRY-002", "MOD-CONFLICT-001", "MOD-AUTHORITY-001", "MOD-MULTI-001"}
        self.assertTrue(required.issubset(set(ids)))

    def test_failure_cases_cover_retry_and_non_retry_classes(self):
        doc = load("tests/failure_recovery_cases.json")
        ids = [x["id"] for x in doc["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        by_code = {x["code"]: x for x in doc["cases"]}
        self.assertEqual(by_code["PERMISSION_DENIED"]["retryability"], "NEVER")
        self.assertEqual(by_code["POLICY_BLOCKED"]["retryability"], "NEVER")
        self.assertEqual(by_code["TIMEOUT"]["retryability"], "TRANSIENT_ONLY")

    def test_validator_cli_accepts_examples(self):
        for rel in (
            "examples/modules/code_specialist.example.json",
            "examples/modules/work_workflow.example.json",
            "examples/modules/multi_model_review.example.json",
            "examples/module_results/blocked_integration.example.json",
        ):
            proc = subprocess.run([sys.executable, str(ROOT / "tools/validate_modules.py"), str(ROOT / rel)], capture_output=True, text=True)
            with self.subTest(example=rel):
                self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("VALID:", proc.stdout)

    def test_validator_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "dup.json"
            path.write_text('{"schema_version":"clay/module-manifest/v1","schema_version":"clay/module-result/v1"}', encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "tools/validate_modules.py"), str(path)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("duplicate JSON key", proc.stderr)

    def test_validator_rejects_oversized_input(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "large.json"
            path.write_text("{" + " " * 1_000_001 + "}", encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "tools/validate_modules.py"), str(path)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 2)
            self.assertIn("exceeds", proc.stderr)

    def test_malformed_semantic_types_fail_validation_without_traceback(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "malformed-result.json"
            obj = load("examples/module_results/blocked_integration.example.json")
            obj["status"] = []
            path.write_text(json.dumps(obj), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "tools/validate_modules.py"), str(path), "--kind", "result"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("INVALID:", proc.stdout)
            self.assertNotIn("Traceback", proc.stderr)

    def test_malformed_capability_entries_fail_validation_without_traceback(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "malformed-manifest.json"
            obj = load("examples/modules/code_specialist.example.json")
            obj["capabilities"] = [["not-an-object"]]
            path.write_text(json.dumps(obj), encoding="utf-8")
            proc = subprocess.run([sys.executable, str(ROOT / "tools/validate_modules.py"), str(path), "--kind", "manifest"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 1)
            self.assertIn("INVALID:", proc.stdout)
            self.assertNotIn("Traceback", proc.stderr)

    def test_multi_model_contract_is_optional_not_majority_truth(self):
        text = (ROOT / "MULTI_MODEL_ORCHESTRATION.md").read_text(encoding="utf-8")
        self.assertIn("not a guarantee of improved quality", (ROOT / "MODULE_INTERFACE.md").read_text(encoding="utf-8"))
        self.assertIn("MUST NOT use raw vote counts as calibrated confidence", text)
        self.assertIn("Consensus among LLMs is not a safety case", text)

    def test_module_contract_declares_composite_fault_localization(self):
        text = (ROOT / "MODULE_INTERFACE.md").read_text(encoding="utf-8")
        self.assertIn("traceable internal component identifiers", text)
        self.assertIn("behavior profile", text.lower())
        self.assertIn("cannot weaken safety plane", text.lower())

if __name__ == "__main__":
    unittest.main()
