"""Structural checks for the ChatGPT conversation-flow adapter; not live LLM tests."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

class ConversationFlowContractTests(unittest.TestCase):
    def test_version_and_flow_defaults(self):
        config = load_json("config/top_mold_chatgpt.json")
        self.assertEqual(config["version"], "0.4.3")
        flow = config["conversation_flow"]
        self.assertTrue(flow["enabled"])
        self.assertEqual(flow["policy"], "answer_first_progressive_formalization")
        self.assertEqual(flow["interaction_posture"]["default"], "natural_conversation")
        self.assertTrue(flow["interaction_posture"]["separate_from_task_mode"])

    def test_progression_is_soft_and_non_linear(self):
        flow = load_json("config/top_mold_chatgpt.json")["conversation_flow"]
        progression = flow["progression"]
        self.assertEqual(len(progression["stages"]), 6)
        self.assertIn("non_linear", progression["semantics"])
        self.assertTrue(progression["may_skip_or_revisit_stages"])
        self.assertTrue(progression["must_not_force_completion_of_all_stages"])
        self.assertTrue(progression["explicit_user_direction_overrides_inferred_progression"])

    def test_no_projectization_and_question_spam(self):
        flow = load_json("config/top_mold_chatgpt.json")["conversation_flow"]
        posture = flow["interaction_posture"]
        self.assertTrue(posture["do_not_turn_every_chat_into_a_project"])
        self.assertEqual(posture["maximum_unsolicited_follow_up_suggestions"], 1)
        self.assertTrue(posture["ask_only_one_focused_question_when_a_blocker_materially_changes_the_result"])
        self.assertIn("over_structuring_every_turn", flow["anti_patterns"])

    def test_hypotheses_are_not_automatically_endorsed(self):
        flow = load_json("config/top_mold_chatgpt.json")["conversation_flow"]
        exploration = flow["exploration"]
        self.assertTrue(exploration["reflect_the_users_hypothesis_without_automatically_endorsing_it"])
        self.assertTrue(exploration["introduce_competing_explanations_when_material"])
        self.assertTrue(exploration["keep_hypotheses_labeled_until_supported"])
        self.assertIn("reflexive_agreement_or_unearned_praise", flow["anti_patterns"])

    def test_conformance_vectors_are_synthetic_and_cover_flow(self):
        doc = load_json("tests/conversation_flow_cases.json")
        self.assertEqual(doc["status"], "proposed_model_level_test_vectors_not_live_llm_results")
        ids = [case["id"] for case in doc["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        required = {
            "CHAT-NATURAL-001", "EXPLORE-HYPOTHESIS-001", "DECOMPOSE-CAUSAL-001",
            "TEST-EXPLICIT-001", "CASUAL-CUE-001", "RIGOR-CUE-001",
            "NO-REFLEXIVE-AGREEMENT-001", "TOPIC-SWITCH-001",
            "NO-PROJECTIZATION-001", "ONE-QUESTION-001",
            "PHASE-NONLINEAR-001", "PROPOSAL-VS-EXECUTION-001",
            "RECIPROCAL-DIALOGUE-001", "OPTIONAL-FOLLOW-UP-001", "NO-FIXED-LEADER-001",
            "NEGOTIATION-SEPARATE-001", "PERSONALIZATION-NATURAL-001"
        }
        self.assertTrue(required.issubset(set(ids)))
        for case in doc["cases"]:
            self.assertTrue(case["input"].strip())
            self.assertTrue(case["expect"])

    def test_protocol_document_is_referenced(self):
        top = (ROOT / "TOP_MOLD_CHATGPT.md").read_text(encoding="utf-8")
        adapter = (ROOT / "CHATGPT_ADAPTER.md").read_text(encoding="utf-8")
        spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
        self.assertIn("CONVERSATION_FLOW.md", top)
        self.assertIn("CONVERSATION_FLOW.md", adapter)
        self.assertIn("soft, non-linear", spec)

if __name__ == "__main__":
    unittest.main()
