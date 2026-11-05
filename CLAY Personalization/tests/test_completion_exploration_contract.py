import json
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator, FormatChecker
except Exception:  # pragma: no cover
    Draft202012Validator = None
    FormatChecker = None

ROOT = Path(__file__).resolve().parents[1]


class CompletionExplorationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config/clay_personalization.json").read_text(encoding="utf-8"))
        cls.schema = json.loads((ROOT / "schemas/iteration_checkpoint.schema.json").read_text(encoding="utf-8"))
        cls.example = json.loads((ROOT / "examples/iteration_checkpoint.example.json").read_text(encoding="utf-8"))
        cls.cases = json.loads((ROOT / "tests/iteration_checkpoint_cases.json").read_text(encoding="utf-8"))

    def test_config_version_and_contract_reference(self):
        self.assertEqual(self.config["version"], "0.4.3")
        self.assertEqual(self.config["schema"], "clay-personalization/control/v0.4.3")
        self.assertEqual(self.config["iteration_model"]["contract_ref"], "../COMPLETION_AND_CONTINUING_EXPLORATION.md")

    def test_contract_is_in_llm_reading_order(self):
        readme = (ROOT / "LLM_README.md").read_text(encoding="utf-8")
        self.assertIn("COMPLETION_AND_CONTINUING_EXPLORATION.md", readme)

    def test_scope_completion_is_separate_from_project_state(self):
        self.assertTrue(self.config["iteration_model"]["scope_complete_does_not_mean_project_final"])
        self.assertEqual(self.example["deliverable_state"], "COMPLETE_FOR_SCOPE")
        self.assertEqual(self.example["project_state"], "OPEN")

    def test_checkpoint_schema_validates_example(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")
        validator = Draft202012Validator(self.schema, format_checker=FormatChecker())
        self.assertEqual(list(validator.iter_errors(self.example)), [])

    def test_complete_for_scope_rejects_unmet_criteria(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")
        invalid = json.loads(json.dumps(self.example))
        invalid["acceptance_criteria"][0]["state"] = "NOT_MET"
        validator = Draft202012Validator(self.schema, format_checker=FormatChecker())
        self.assertTrue(list(validator.iter_errors(invalid)))

    def test_closed_project_cannot_plan_continuation(self):
        if Draft202012Validator is None:
            self.skipTest("jsonschema is unavailable")
        invalid = json.loads(json.dumps(self.example))
        invalid["project_state"] = "CLOSED"
        validator = Draft202012Validator(self.schema, format_checker=FormatChecker())
        self.assertTrue(list(validator.iter_errors(invalid)))

    def test_proposed_direction_is_not_implicit_consent(self):
        self.assertEqual(self.example["next_step"]["decision_status"], "PROPOSED")
        self.assertTrue(self.example["next_step"]["scope_change_requires_confirmation"])

    def test_success_patterns_require_reproduction_conditions_and_evidence(self):
        pattern = self.example["effective_patterns"][0]
        self.assertTrue(pattern["replication_conditions"])
        self.assertTrue(pattern["evidence_refs"])
        self.assertTrue(pattern["limits"])

    def test_failure_lessons_are_testable(self):
        failure = self.example["failure_prevention"][0]
        self.assertTrue(failure["prevention_or_detection"])
        self.assertTrue(failure["verification"])
        self.assertTrue(failure["evidence_refs"])
        self.assertIn(failure["cause_status"], {"OBSERVED_FACTOR", "SUPPORTED_INFERENCE", "HYPOTHESIS", "UNKNOWN"})

    def test_formal_review_is_not_mandatory_for_every_turn(self):
        self.assertFalse(self.config["iteration_model"]["formal_review_for_every_task"])
        self.assertIn("NOT_NEEDED", self.schema["properties"]["review_status"]["enum"])
        self.assertIn("USER_DECLINED", self.schema["properties"]["review_status"]["enum"])

    def test_next_step_can_pause_close_or_do_nothing(self):
        modes = self.schema["properties"]["next_step"]["properties"]["mode"]["enum"]
        self.assertTrue({"PAUSE", "CLOSE", "NONE"}.issubset(set(modes)))

    def test_synthetic_case_ids_are_unique_and_cover_key_boundaries(self):
        cases = self.cases["cases"]
        ids = [case["id"] for case in cases]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(cases), 17)
        joined = " ".join(case["scenario"] + " " + case["expect"] for case in cases)
        for phrase in ("successful method", "failure recurs", "declines", "scope", "pause", "previous version"):
            self.assertIn(phrase, joined)
        self.assertEqual(self.cases["status"], "proposed_synthetic_vectors_not_live_llm_results")

    def test_reflexive_agreement_and_disagreement_are_both_disallowed(self):
        coexistence = self.config["coexistence"]
        self.assertFalse(coexistence["reflexive_agreement_allowed"])
        self.assertFalse(coexistence["reflexive_disagreement_allowed"])
        self.assertTrue(coexistence["informed_permitted_personal_choice_should_be_respected"])

    def test_longitudinal_evaluation_tracks_multiple_dimensions(self):
        model = self.config["iteration_model"]
        self.assertTrue(model["longitudinal_multi_axis_evaluation"])
        self.assertTrue(model["single_average_may_hide_material_regression"])

    def test_package_does_not_claim_live_runtime_or_persistence(self):
        self.assertFalse(self.config["implementation_boundary"]["iteration_checkpoint_runtime_included"])
        self.assertFalse(self.config["implementation_boundary"]["iteration_checkpoint_persistence_included"])

    def test_exploration_has_value_without_forced_enthusiasm(self):
        model = self.config["iteration_model"]
        self.assertTrue(model["exploration_has_intrinsic_value"])
        self.assertTrue(model["curiosity_is_user_led_not_forced"])
        contract = (ROOT / "COMPLETION_AND_CONTINUING_EXPLORATION.md").read_text(encoding="utf-8")
        self.assertIn("Do not give up on completion; do not become attached to completion as the final form.", contract)
        self.assertIn("force an upbeat or playful tone", contract)

    def test_gradual_mutual_understanding_does_not_require_convergence(self):
        self.assertTrue(self.config["iteration_model"]["mutual_understanding_may_be_gradual_without_required_convergence"])
        self.assertTrue(self.config["coexistence"]["mutual_adjustment_is_gradual"])
        self.assertTrue(self.config["coexistence"]["convergence_is_not_a_success_metric"])


if __name__ == "__main__":
    unittest.main()
