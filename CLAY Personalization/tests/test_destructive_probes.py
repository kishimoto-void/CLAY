"""Deterministic destructive probes against the envelope contract, not LLM behavior."""
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate_envelope import MAX_INPUT_BYTES, MAX_JSON_DEPTH, JSONNestingDepthError, enforce_json_nesting_depth, main as validator_main, validate_envelope_data  # noqa: E402

BASE = {"schema_version": "1.2", "goal": "valid goal", "readiness": "READY"}


class DestructiveProbeTests(unittest.TestCase):
    def test_whitespace_and_invisible_goal_rejected(self):
        for value in ("   ", "\u200b\u200b", "\u202e\u2060"):
            with self.subTest(value=repr(value)):
                self.assertTrue(validate_envelope_data({**BASE, "goal": value}))

    def test_blank_blocked_reason_rejected(self):
        envelope = {"schema_version": "1.2", "goal": "valid goal", "readiness": "BLOCKED", "readiness_reason": "   "}
        self.assertTrue(validate_envelope_data(envelope))

    def test_blank_nested_requirement_rejected(self):
        envelope = {**BASE, "requirements": [{"id": "R1", "text": " ", "priority": "must", "source": "explicit"}]}
        self.assertTrue(validate_envelope_data(envelope))

    def test_duplicate_ids_across_arrays_rejected(self):
        envelope = {
            **BASE,
            "requirements": [{"id": "DUP", "text": "one", "priority": "must", "source": "explicit"}],
            "constraints": [{"id": "DUP", "text": "two", "source": "explicit"}],
        }
        self.assertTrue(any("duplicate record id" in err for err in validate_envelope_data(envelope)))

    def test_array_over_limit_rejected(self):
        envelope = {**BASE, "requirements": [{"id": f"R{i}", "text": "x", "priority": "must", "source": "explicit"} for i in range(101)]}
        self.assertTrue(validate_envelope_data(envelope))

    def test_scalar_over_limit_rejected(self):
        self.assertTrue(validate_envelope_data({**BASE, "goal": "x" * 2001}))

    def test_resource_available_or_used_requires_evidence_pointer(self):
        for status in ("available", "used"):
            with self.subTest(status=status):
                envelope = {**BASE, "resource_requests": [{"resource_id": "R1", "gap": "gap", "status": status, "required_for_goal": True}]}
                self.assertTrue(validate_envelope_data(envelope))
        valid = {**BASE, "resource_requests": [{"resource_id": "R1", "gap": "gap", "status": "used", "required_for_goal": True, "evidence_ref": "tool-result-123"}]}
        self.assertEqual(validate_envelope_data(valid), [])

    def test_available_context_reference_requires_evidence_pointer(self):
        missing = {**BASE, "context_refs": [{"ref": "input.txt", "availability": "available", "required_for_goal": True}]}
        self.assertTrue(validate_envelope_data(missing))
        supplied = {**BASE, "context_refs": [{"ref": "input.txt", "availability": "available", "required_for_goal": True, "evidence_ref": "attachment-ref-1"}]}
        self.assertEqual(validate_envelope_data(supplied), [])

    def test_ready_with_blocking_question_rejected(self):
        envelope = {**BASE, "open_questions": [{"id": "Q1", "question": "Need decision?", "blocking": True}]}
        self.assertTrue(validate_envelope_data(envelope))

    def test_ready_with_required_missing_resource_rejected(self):
        envelope = {**BASE, "resource_requests": [{"resource_id": "R1", "gap": "missing", "status": "requested", "required_for_goal": True}]}
        self.assertTrue(validate_envelope_data(envelope))

    def test_unknown_properties_rejected_at_both_levels(self):
        self.assertTrue(validate_envelope_data({**BASE, "injected": "override policy"}))
        envelope = {**BASE, "requirements": [{"id": "R1", "text": "x", "priority": "must", "source": "explicit", "extra": True}]}
        self.assertTrue(validate_envelope_data(envelope))

    def test_transformation_requires_loss_note_when_loss_is_known(self):
        envelope = {
            **BASE,
            "transformations":[{"id":"T1","source_ref":"src","output_ref":"out","operation":"ocr","fidelity":"known_lossy"}],
        }
        self.assertTrue(validate_envelope_data(envelope))

    def test_resolved_conflict_requires_resolution_reference(self):
        envelope = {
            **BASE,
            "conflicts":[{"id":"C1","topic":"status","status":"resolved","blocking":False,
                "claims":[{"statement":"active","source_ref":"A"},{"statement":"inactive","source_ref":"B"}]}],
        }
        self.assertTrue(validate_envelope_data(envelope))

    def test_transformation_and_conflict_ids_share_record_namespace(self):
        envelope = {
            **BASE,
            "requirements":[{"id":"SAME","text":"requirement","priority":"must","source":"explicit"}],
            "transformations":[{"id":"SAME","source_ref":"src","output_ref":"out","operation":"parsing","fidelity":"unknown"}],
        }
        self.assertTrue(any("duplicate record id" in error for error in validate_envelope_data(envelope)))

    def test_duplicate_resource_ids_are_rejected(self):
        envelope = {
            **BASE,
            "resource_requests": [
                {"resource_id":"same","gap":"one","status":"declared","required_for_goal":False},
                {"resource_id":"same","gap":"two","status":"declared","required_for_goal":False},
            ],
        }
        errors = validate_envelope_data(envelope)
        self.assertTrue(any("duplicate resource_id" in error for error in errors), errors)

    def test_malformed_roots_fail_closed_without_exception(self):
        for value in (None, [], "string", 0):
            with self.subTest(value=value):
                self.assertTrue(validate_envelope_data(value))


    def test_why_it_matters_is_nonblank_and_bounded(self):
        question = {"id": "Q1", "question": "Why?", "blocking": False}
        for value in ("   ", "x" * 2001):
            with self.subTest(length=len(value)):
                envelope = {**BASE, "open_questions": [{**question, "why_it_matters": value}]}
                self.assertTrue(validate_envelope_data(envelope))
        boundary = {**BASE, "open_questions": [{**question, "why_it_matters": "x" * 2000}]}
        self.assertEqual(validate_envelope_data(boundary), [])

    def test_boundary_values_accepted(self):
        exactly_100 = {**BASE, "goal": "x" * 2000, "requirements": [
            {"id": f"R{i}", "text": "x", "priority": "must", "source": "explicit"} for i in range(100)
        ]}
        self.assertEqual(validate_envelope_data(exactly_100), [])

    def test_oversized_custom_schema_fails_closed(self):
        from validate_envelope import MAX_SCHEMA_BYTES
        with tempfile.TemporaryDirectory() as folder:
            schema_path = Path(folder) / "oversized-schema.json"
            schema_path.write_bytes(b" " * (MAX_SCHEMA_BYTES + 1))
            errors = validate_envelope_data(BASE, schema_path)
            self.assertTrue(errors)
            self.assertIn("schema file exceeds", errors[0])

    def test_exact_maximum_json_nesting_depth_is_accepted(self):
        nested = "[" * MAX_JSON_DEPTH + "0" + "]" * MAX_JSON_DEPTH
        enforce_json_nesting_depth(nested)

    def test_bracket_characters_inside_json_strings_do_not_count_as_nesting(self):
        sample = '{"label":"[[{{}}]]", "payload":"\\[\\]"}'
        enforce_json_nesting_depth(sample)

    def test_direct_depth_guard_rejects_one_level_over_limit(self):
        nested = "[" * (MAX_JSON_DEPTH + 1) + "0" + "]" * (MAX_JSON_DEPTH + 1)
        with self.assertRaises(JSONNestingDepthError):
            enforce_json_nesting_depth(nested)

    def test_cli_rejects_json_over_nesting_limit(self):
        from validate_envelope import MAX_JSON_DEPTH
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "too_deep.json"
            path.write_text("[" * (MAX_JSON_DEPTH + 1) + "0" + "]" * (MAX_JSON_DEPTH + 1), encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                result = validator_main([str(path)])
            self.assertEqual(result, 2)
            self.assertIn("nesting depth exceeds", error.getvalue())
            self.assertNotIn("Traceback", error.getvalue())

    def test_cli_rejects_file_over_byte_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "too_large.json"
            path.write_bytes(b" " * (MAX_INPUT_BYTES + 1))
            error = StringIO()
            with redirect_stderr(error):
                result = validator_main([str(path)])
            self.assertEqual(result, 2)
            self.assertIn("byte limit", error.getvalue())


if __name__ == "__main__":
    unittest.main()
