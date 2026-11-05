import copy
import json
from pathlib import Path
import sys
import unittest
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from safety_plane.topology import PROTECTED_SAFETY_MODULES, validate_topology

EXAMPLE = ROOT / "examples/index_states/control_topology.example.json"


class SafetyTopologyTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def assert_invalid_code(self, config, code):
        codes = {v.code for v in validate_topology(config)}
        self.assertIn(code, codes)

    def test_index_and_topology_examples_match_json_schemas(self):
        fixtures = [
            ("schemas/control_topology.schema.json", "examples/index_states/control_topology.example.json"),
            ("schemas/gamma_index_snapshot.schema.json", "examples/index_states/gamma_index_snapshot.example.json"),
            ("schemas/delta_event.schema.json", "examples/index_states/delta_pending_change.example.json"),
        ]
        for schema_path, example_path in fixtures:
            with self.subTest(schema=schema_path):
                schema = json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
                example = json.loads((ROOT / example_path).read_text(encoding="utf-8"))
                Draft202012Validator.check_schema(schema)
                errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(example))
                self.assertEqual(errors, [], [error.message for error in errors])

    def test_reference_topology_passes(self):
        self.assertEqual(validate_topology(self.config), [])

    def test_all_protected_modules_are_present_and_cross_cutting(self):
        self.assertTrue(PROTECTED_SAFETY_MODULES.issubset(
            set(self.config["control_flow"]["cross_cutting_safety_plane"])))

    def test_risk_boundary_cannot_be_put_after_delta(self):
        mutated = copy.deepcopy(self.config)
        mutated["control_flow"]["sequential_pipeline"].append("risk_boundary_engine")
        mutated["control_flow"]["cross_cutting_safety_plane"].remove("risk_boundary_engine")
        self.assert_invalid_code(mutated, "SAFETY_IN_SEQUENTIAL_PIPELINE")

    def test_recovery_path_cannot_depend_on_delta(self):
        mutated = copy.deepcopy(self.config)
        mutated["dependencies"]["recovery_path_engine"].append("delta_index")
        self.assert_invalid_code(mutated, "SAFETY_DEPENDS_ON_OPTIONAL_INDEX_OR_PROFILE")

    def test_transitive_delta_dependency_is_rejected(self):
        mutated = copy.deepcopy(self.config)
        mutated["dependencies"]["host_capability_registry"] = ["delta_index"]
        self.assert_invalid_code(mutated, "TRANSITIVE_SAFETY_DEPENDENCY_FORBIDDEN")

    def test_safety_module_cannot_be_disabled(self):
        mutated = copy.deepcopy(self.config)
        mutated["modules"]["hard_safety_override"]["enabled"] = False
        self.assert_invalid_code(mutated, "SAFETY_MODULE_DISABLED")

    def test_delta_cannot_authorize_or_mutate(self):
        mutated = copy.deepcopy(self.config)
        mutated["modules"]["delta_index"]["can_authorize"] = True
        self.assert_invalid_code(mutated, "DELTA_AUTHORITY_ESCALATION")

    def test_delta_role_must_remain_observer_only(self):
        mutated = copy.deepcopy(self.config)
        mutated["modules"]["delta_index"]["role"] = "POLICY_AUTHORITY"
        self.assert_invalid_code(mutated, "DELTA_ROLE_ESCALATION")

    def test_missing_gamma_index_is_rejected(self):
        mutated = copy.deepcopy(self.config)
        del mutated["modules"]["gamma_index"]
        self.assert_invalid_code(mutated, "MISSING_INDEX_MODULE")

    def test_missing_recovery_path_is_rejected(self):
        mutated = copy.deepcopy(self.config)
        del mutated["modules"]["recovery_path_engine"]
        self.assert_invalid_code(mutated, "MISSING_PROTECTED_MODULE")

    def test_safety_cannot_depend_on_personalization_overlay(self):
        mutated = copy.deepcopy(self.config)
        mutated["dependencies"]["risk_boundary_engine"].append("personalization_overlay")
        self.assert_invalid_code(mutated, "SAFETY_DEPENDS_ON_OPTIONAL_INDEX_OR_PROFILE")


if __name__ == "__main__":
    unittest.main()
