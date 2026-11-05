"""Deterministic outcome-learning contract checks; not live LLM behavior tests."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class OutcomeLearningContractTests(unittest.TestCase):
    def setUp(self):
        self.schema = load("schemas/outcome_review.schema.json")
        Draft202012Validator.check_schema(self.schema)
        self.validator = Draft202012Validator(self.schema)

    def test_failure_and_success_examples_validate(self):
        for rel in ("examples/outcome_review.failure.example.json", "examples/outcome_review.success.example.json"):
            with self.subTest(example=rel):
                self.assertEqual([], list(self.validator.iter_errors(load(rel))))

    def test_one_off_behavior_profile_change_requires_confirmation(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["adaptation"] = {"target_layer":"BEHAVIOR_PROFILE_PROPOSAL","scope":"PENDING_USER_CONFIRMATION","change":"Always use shorter answers.","approval_required":True,"applied":False}
        self.assertEqual([], list(self.validator.iter_errors(obj)))

    def test_behavior_profile_proposal_cannot_be_applied_before_confirmation(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["adaptation"] = {"target_layer":"BEHAVIOR_PROFILE_PROPOSAL","scope":"PENDING_USER_CONFIRMATION","change":"Always use shorter answers.","approval_required":True,"applied":True}
        self.assertTrue(list(self.validator.iter_errors(obj)))

    def test_behavior_profile_proposal_cannot_bypass_approval(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["adaptation"] = {"target_layer":"BEHAVIOR_PROFILE_PROPOSAL","scope":"PENDING_USER_CONFIRMATION","change":"Always use shorter answers.","approval_required":False,"applied":False}
        self.assertTrue(list(self.validator.iter_errors(obj)))

    def test_unknown_cause_is_a_valid_explicit_state(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["contributing_factors"] = [{"factor_id":"unknown","description":"Available evidence does not establish a cause.","epistemic_status":"UNKNOWN","locus":"UNCLASSIFIED","evidence_refs":[]}]
        self.assertEqual([], list(self.validator.iter_errors(obj)))

    def test_aborted_attempt_cannot_be_promoted_to_general_candidate_lesson(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["outcome"] = "ABORTED"
        obj["learnings"][0]["scope"] = "GENERAL_CANDIDATE"
        self.assertTrue(list(self.validator.iter_errors(obj)))

    def test_none_adaptation_must_not_smuggle_a_change(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["adaptation"] = {"target_layer":"NONE","scope":"NONE","change":"Persist this preference.","approval_required":False,"applied":False}
        self.assertTrue(list(self.validator.iter_errors(obj)))

    def test_success_is_not_required_to_produce_a_profile_change(self):
        obj = load("examples/outcome_review.success.example.json")
        self.assertNotEqual("BEHAVIOR_PROFILE_PROPOSAL", obj["adaptation"]["target_layer"])
        self.assertEqual([], list(self.validator.iter_errors(obj)))

    def test_unrecognized_outcome_is_rejected(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["outcome"] = "BAD"
        self.assertTrue(list(self.validator.iter_errors(obj)))

    def test_unknown_success_criterion_is_preserved(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["success_criteria"][0]["state"] = "UNKNOWN"
        self.assertEqual([], list(self.validator.iter_errors(obj)))

    def test_causal_status_must_not_use_untyped_certainty(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["contributing_factors"][0]["epistemic_status"] = "ROOT_CAUSE"
        self.assertTrue(list(self.validator.iter_errors(obj)))

    def test_record_rejects_unexpected_fields(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["hidden_reasoning"] = "must not be captured"
        self.assertTrue(list(self.validator.iter_errors(obj)))

    def test_synthetic_vectors_are_unique_and_cover_key_boundaries(self):
        doc = load("tests/outcome_learning_cases.json")
        self.assertEqual("proposed_synthetic_vectors_not_live_llm_results", doc["status"])
        ids = [case["id"] for case in doc["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 18)
        self.assertTrue({"OL-001", "OL-002", "OL-005", "OL-007", "OL-009", "OL-011", "OL-012", "OL-013", "OL-017", "OL-018"}.issubset(set(ids)))

    def test_llm_entry_point_declares_read_order_and_outcome_cycle(self):
        text = (ROOT / "LLM_README.md").read_text(encoding="utf-8")
        for phrase in ("OUTCOME_LEARNING.md", "GOAL -> PREPARATION / ASSUMPTIONS", "Do not promise success", "explicit user confirmation", "hidden chain-of-thought"):
            self.assertIn(phrase, text)

    def test_outcome_and_process_quality_are_independent(self):
        text = (ROOT / "OUTCOME_LEARNING.md").read_text(encoding="utf-8")
        for phrase in ("Outcome quality", "Process quality", "A good process can still lose", "A weak process can occasionally win", "single score"):
            self.assertIn(phrase, text)

    def test_llm_owns_review_of_its_controllable_choices(self):
        text = (ROOT / "LLM_README.md").read_text(encoding="utf-8")
        self.assertIn("Inspect the LLM's own controllable choices first", text)
        self.assertIn("Do not make the user perform the model's postmortem", text)

    def test_schema_requires_a_separate_process_review(self):
        obj = load("examples/outcome_review.failure.example.json")
        del obj["process_review"]
        self.assertTrue(list(self.validator.iter_errors(obj)))

    def test_failed_outcome_can_have_a_sound_process(self):
        obj = load("examples/outcome_review.failure.example.json")
        obj["process_review"] = {"assessment":"SOUND","observations":[{"area":"PREPARATION","assessment":"EFFECTIVE","description":"Preparation met the stated constraints.","evidence_refs":[]}]}
        self.assertEqual([], list(self.validator.iter_errors(obj)))

    def test_successful_outcome_can_have_a_weak_process(self):
        obj = load("examples/outcome_review.success.example.json")
        obj["process_review"] = {"assessment":"WEAK","observations":[{"area":"VERIFICATION","assessment":"GAP","description":"The result happened to meet the target, but the required verification was skipped.","evidence_refs":[]}]}
        self.assertEqual([], list(self.validator.iter_errors(obj)))

    def test_core_and_recovery_contracts_reference_outcome_learning(self):
        core = (ROOT / "COMMON_CORE.md").read_text(encoding="utf-8")
        recovery = (ROOT / "FAILURE_RECOVERY.md").read_text(encoding="utf-8")
        self.assertIn("OUTCOME_LEARNING.md", core)
        self.assertIn("OUTCOME_LEARNING.md", recovery)


if __name__ == "__main__":
    unittest.main()
