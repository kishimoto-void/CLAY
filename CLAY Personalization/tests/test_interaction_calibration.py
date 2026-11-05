"""Static traceability tests for the v0.4.3 interaction-calibration addendum.

These tests validate the declared contract and test-vector coverage only. They do
not invoke an LLM or claim live behavioral conformance.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read_text(name):
    return (ROOT / name).read_text(encoding="utf-8")

def read_json(name):
    return json.loads(read_text(name))

class InteractionCalibrationTests(unittest.TestCase):
    def test_new_vectors_are_unique_and_nonempty(self):
        doc = read_json("tests/interaction_calibration_cases.json")
        self.assertEqual(doc["status"], "synthetic_model_level_test_vectors_not_live_llm_results")
        ids = [case["id"] for case in doc["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 12)
        for case in doc["cases"]:
            self.assertTrue(case["input"].strip())
            self.assertTrue(case["expect"])

    def test_tentative_options_are_not_closed_by_default(self):
        cfg = read_json("config/clay_personalization.json")["conversation_flow"]["exploration"]
        self.assertTrue(cfg["user_provided_candidate_options_are_not_assumed_exhaustive"])
        self.assertTrue(cfg["consider_material_alternatives_when_the_user_is_exploring_or_uncertain"])
        self.assertTrue(cfg["when_expanding_offer_only_a_small_relevant_set"])
        self.assertTrue(cfg["honor_explicitly_bounded_comparison_scope"])

    def test_initiative_and_verification_are_independent(self):
        cfg = read_json("config/clay_personalization.json")["conversation_flow"]["verification"]
        self.assertTrue(cfg["initiative_and_verification_are_orthogonal"])
        self.assertTrue(cfg["work_context_prioritizes_provenance_assumptions_reproducibility_and_checked_status"])
        self.assertTrue(cfg["work_label_alone_does_not_require_exhaustive_formalism"])
        self.assertTrue(cfg["casual_tone_does_not_lower_material_fact_or_safety_requirements"])

    def test_legacy_config_matches_canonical(self):
        a = read_json("config/clay_personalization.json")
        b = read_json("config/top_mold_chatgpt.json")
        self.assertEqual(a, b)

    def test_common_core_does_not_embed_person_specific_values(self):
        cfg = read_json("config/clay_personalization.json")
        boundary = cfg["package_data_boundary"]
        self.assertFalse(boundary["contains_individual_profile_records"])
        self.assertFalse(boundary["contains_person_specific_preferences"])
        self.assertFalse(cfg["implementation_boundary"]["personal_data_store_included"])
        self.assertTrue(cfg["gamma_profile_bridge"]["personal_data_allowed_in_profile"] is False)

    def test_contract_documents_explain_new_boundaries(self):
        flow = read_text("CONVERSATION_FLOW.md")
        spec = read_text("SPEC.md")
        self.assertIn("Tentative options are starting points", flow)
        self.assertIn("Initiative and verification are independent dimensions", flow)
        self.assertIn("User-supplied candidate options are not automatically exhaustive", spec)
        self.assertIn("behavior-profile layer", spec)

    def test_anti_overexpansion_and_explicit_scope_are_both_present(self):
        flow = read_text("CONVERSATION_FLOW.md")
        self.assertIn("Do not respond with an exhaustive catalog", flow)
        self.assertIn("honor explicitly bounded comparisons", flow.lower())
        self.assertIn("material risk", flow)

    def test_vectors_cover_critical_independent_dimensions(self):
        doc = read_json("tests/interaction_calibration_cases.json")
        ids = {case["id"] for case in doc["cases"]}
        required = {
            "TENTATIVE-OPTIONS-NOT-CLOSED", "BOUNDED-COMPARISON", "WORK-EVIDENCE-FIRST",
            "WORK-NO-AUTO-FORMALISM", "CASUAL-TONE-RIGOR", "LOW-INITIATIVE-HIGH-RIGOR",
            "SESSION-LOCK-OVERRIDE", "ONE-OFF-NOT-PROFILE", "HOLD-PURCHASE", "SAFETY-CHAT-CUE"
        }
        self.assertTrue(required.issubset(ids))

if __name__ == "__main__":
    unittest.main()
