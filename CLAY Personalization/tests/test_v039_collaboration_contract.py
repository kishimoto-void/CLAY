"""Static contract tests; these do not test live LLM behavior."""
import json
import unittest
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    Draft202012Validator = None

ROOT = Path(__file__).resolve().parents[1]

class V039CollaborationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads((ROOT / "config/top_mold_chatgpt.json").read_text(encoding="utf-8"))

    def test_version_and_complementarity_boundaries(self):
        self.assertEqual(self.config["version"], "0.4.3")
        model = self.config["collaboration_model"]
        self.assertFalse(model["fixed_conversational_leader"])
        self.assertTrue(model["separate_contribution_from_authority"])
        self.assertTrue(model["human_real_world_decision_rights_and_accountability_preserved"])
        self.assertTrue(model["negotiation"]["proposal_is_not_consent"])

    def test_answer_first_does_not_force_questions(self):
        flow = self.config["conversation_flow"]
        self.assertTrue(flow["question_policy"]["answer_before_optional_question"])
        self.assertFalse(flow["question_policy"]["question_is_mandatory"])
        self.assertTrue(flow["interaction_model"]["negotiation_is_distinct_from_exploratory_dialogue"])

    def test_evidence_model_rejects_naive_counting(self):
        evidence = self.config["evidence_evaluation"]
        self.assertFalse(evidence["naive_axis_count_scoring_allowed"])
        self.assertFalse(evidence["confidence_state_is_calibrated_probability"])
        self.assertTrue(evidence["independence_grouping_required_when_sources_may_share_origin"])
        self.assertTrue(evidence["subjective_preference_handling"].startswith("first_person_report"))
        self.assertTrue(evidence["self_assessment_handling"].startswith("retain_as_self_perception"))

    def test_performance_objective_is_utilization_not_model_intelligence(self):
        perf = self.config["performance_utilization"]
        self.assertEqual(perf["objective"], "increase_useful_utilization_not_base_model_capability")
        self.assertFalse(perf["claims_base_model_intelligence_increase"])
        self.assertTrue(perf["must_measure_improvement"])
        self.assertFalse(perf["package_tests_prove_live_model_improvement"])

    def test_synthetic_evidence_example_matches_schema(self):
        schema = json.loads((ROOT / "schemas/evidence_bundle.schema.json").read_text(encoding="utf-8"))
        example = json.loads((ROOT / "examples/evidence_evaluation.example.json").read_text(encoding="utf-8"))
        if Draft202012Validator is not None:
            Draft202012Validator.check_schema(schema)
            errors = sorted(Draft202012Validator(schema).iter_errors(example), key=lambda e: list(e.path))
            self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])
        else:
            self.assertEqual(example["schema_version"], "top-mold/evidence-bundle/v0.1")
        ids = [item["evidence_id"] for item in example["evidence"]]
        self.assertEqual(len(ids), len(set(ids)))
        import copy
        malformed = copy.deepcopy(example)
        malformed["assessment"]["numeric_probability"] = 0.8
        with self.assertRaises(Exception):
            Draft202012Validator(schema).validate(malformed)
        calibrated_shape = copy.deepcopy(example)
        calibrated_shape["assessment"]["numeric_probability"] = 0.8
        calibrated_shape["assessment"]["probability_basis"] = "Synthetic illustrative calibration note; not an empirical claim."
        Draft202012Validator(schema).validate(calibrated_shape)

    def test_required_guidance_files_are_present_and_have_boundaries(self):
        for name in ("HUMAN_LLM_CO_EVOLUTION.md", "RECIPROCAL_EVIDENCE_EVALUATION.md", "PERFORMANCE_UTILIZATION.md"):
            self.assertTrue((ROOT / name).is_file())
        evidence_doc = (ROOT / "RECIPROCAL_EVIDENCE_EVALUATION.md").read_text(encoding="utf-8")
        self.assertIn("Do not count ten derivative reports", evidence_doc)
        self.assertIn("do **not** prove universal", evidence_doc)
        util_doc = (ROOT / "PERFORMANCE_UTILIZATION.md").read_text(encoding="utf-8")
        self.assertIn("does not add model parameters", util_doc)
        self.assertIn("Track errors and regressions", util_doc)

if __name__ == "__main__":
    unittest.main()
