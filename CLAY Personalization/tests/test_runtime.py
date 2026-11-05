import unittest
from pathlib import Path
from clay_runtime import ClayRuntime
from clay_runtime.config import load_config, ConfigError

ROOT = Path(__file__).resolve().parents[1]

def ready_envelope():
    return {
        "schema_version": "1.2",
        "goal": "Produce a testable implementation plan",
        "readiness": "READY",
        "task_mode": "work",
        "requirements": [],
        "constraints": [],
        "exclusions": [],
        "context_refs": [],
        "assumptions": [],
        "open_questions": [],
        "resource_requests": [],
        "output_contract": [],
        "verification": [],
        "readiness_reason": "All required inputs supplied",
        "note": "synthetic test",
        "transformations": [],
        "conflicts": []
    }

class RuntimeTests(unittest.TestCase):
    def test_ready_envelope_prepares(self):
        result = ClayRuntime().prepare(ready_envelope())
        self.assertEqual(result.status, "PREPARED")
        self.assertFalse(result.errors)
        self.assertIn("Goal: Produce a testable implementation plan", result.adapter_context)
        self.assertEqual(result.effective_dials["proactiveness"], 20)

    def test_not_ready_is_not_rendered(self):
        env = ready_envelope()
        env["readiness"] = "CLARIFICATION_REQUIRED"
        env["open_questions"] = [{"id":"q1","question":"Need one detail","blocking":True}]
        result = ClayRuntime().prepare(env)
        self.assertEqual(result.status, "CLARIFICATION_REQUIRED")
        self.assertIsNone(result.adapter_context)

    def test_invalid_envelope_fails_closed(self):
        result = ClayRuntime().prepare({"goal": "x", "readiness": "READY"})
        self.assertEqual(result.status, "INVALID")
        self.assertTrue(result.errors)

    def test_config_duplicate_keys_rejected(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json") as f:
            f.write('{"schema":"clay-personalization/control/v0.4.3","schema":"x"}')
            f.flush()
            with self.assertRaises(ConfigError):
                load_config(f.name)

if __name__ == "__main__":
    unittest.main()
