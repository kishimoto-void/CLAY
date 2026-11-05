"""Deterministic coexistence-contract checks; not live user-impact tests."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

class CoexistenceContractTests(unittest.TestCase):
    def test_config_declares_non_imposition_and_honest_influence_limit(self):
        cfg = load("config/clay_personalization.json")
        c = cfg["coexistence"]
        self.assertEqual(cfg["version"], "0.4.3")
        self.assertFalse(c["fixed_assistant_personality_imposed"])
        self.assertFalse(c["ideal_user_thinking_style_prescribed"])
        self.assertFalse(c["coercive_persuasion_to_cp_worldview_allowed"])
        self.assertTrue(c["evidence_based_disagreement_allowed"])
        self.assertFalse(c["zero_cognitive_influence_guaranteed"])
        self.assertFalse(c["user_modification_may_override_safety_or_host_constraints"])

    def test_legacy_config_remains_equal_to_canonical(self):
        self.assertEqual(load("config/clay_personalization.json"), load("config/top_mold_chatgpt.json"))

    def test_contract_distinguishes_disagreement_from_imposition(self):
        text = (ROOT / "COEXISTENCE_AND_NON_IMPOSITION.md").read_text(encoding="utf-8")
        for phrase in ("adapts the system to work with the user", "Disagreement is not cognitive imposition", "MUST NOT", "explicit user confirmation", "zero influence", "may narrow or revoke"):
            self.assertIn(phrase, text)

    def test_common_core_includes_coexistence_invariant(self):
        text = (ROOT / "COMMON_CORE.md").read_text(encoding="utf-8")
        self.assertIn("2.9 Coexistence without cognitive imposition", text)
        self.assertIn("COEXISTENCE_AND_NON_IMPOSITION.md", text)

    def test_spec_makes_contract_normative_and_preserves_safety(self):
        text = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        self.assertIn("## 25. Coexistence without cognitive imposition", text)
        self.assertIn("non-delegable Safety Plane", text)
        self.assertIn("explicit user request", text)

    def test_llm_readme_places_contract_in_reading_order(self):
        text = (ROOT / "LLM_README.md").read_text(encoding="utf-8")
        self.assertIn("COEXISTENCE_AND_NON_IMPOSITION.md", text)
        self.assertIn("do not pressure the user", text)

    def test_synthetic_cases_are_unique_and_cover_critical_boundaries(self):
        doc = load("tests/coexistence_cases.json")
        self.assertEqual(doc["status"], "proposed_synthetic_vectors_not_live_llm_results")
        ids = [x["id"] for x in doc["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 12)
        required = {"COEX-002", "COEX-003", "COEX-005", "COEX-010", "COEX-011", "COEX-012"}
        self.assertTrue(required.issubset(set(ids)))
        for case in doc["cases"]:
            self.assertTrue(case["input"].strip())
            self.assertTrue(case["expect"].strip())
            self.assertTrue(case["must_not"].strip())

    def test_conformity_is_not_treated_as_success_metric(self):
        text = (ROOT / "COEXISTENCE_AND_NON_IMPOSITION.md").read_text(encoding="utf-8")
        self.assertIn("Never treat increased agreement with CP", text)
        self.assertIn("not the target", (ROOT / "EVALUATION_PROTOCOL.md").read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
