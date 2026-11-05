"""Deterministic package checks; these are not LLM-behavior tests."""
import json
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_envelope import MAX_INPUT_BYTES, MAX_JSON_DEPTH, MAX_SCHEMA_BYTES, main as validate_envelope_main, validate_envelope_data  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.4.3"
DIAL_KEYS = {
    "proactiveness", "initiative", "cross_domain_transfer", "generalization",
    "verification_strictness", "drift_allowance", "detail_structure", "concision",
    "human_control", "speculation_tolerance", "uncertainty_preservation",
    "contradiction_preservation", "transformation_fidelity",
}


def load_json(relative: str):
    with (ROOT / relative).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_envelope_contract(envelope):
    """Expose the shared schema + semantic validation behavior to package tests."""
    return validate_envelope_data(envelope)


class PackageStructureTests(unittest.TestCase):
    def test_gamma_delta_phase_contract_declares_revision_and_hold_boundaries(self):
        config = json.loads((ROOT / "config/top_mold_chatgpt.json").read_text(encoding="utf-8"))
        gamma = config["index_phase_contract"]["gamma"]
        delta = config["index_phase_contract"]["delta"]
        self.assertTrue(gamma["continuation_requires_prior_revision"])
        self.assertTrue(delta["reobservation_requires_new_observation_id"])
        self.assertFalse(delta["user_holds_auto_released"])
        self.assertFalse(delta["stale_base_holds_block_fresh_comparison"])
        self.assertEqual(set(delta["hold_source_values"]), {"SYSTEM_COMPETITION", "USER", "STALE_BASE"})

    def test_config_version_and_model_boundary(self):
        config = load_json("config/top_mold_chatgpt.json")
        self.assertEqual(config["version"], VERSION)
        self.assertEqual(config["schema"], "clay-personalization/control/v0.4.3")
        self.assertEqual(config["role"]["mold_intelligence"], "none")
        self.assertFalse(config["role"]["guarantees_performance_improvement"])
        for boundary_key in ("natural_language_parser_in_mold", "independent_reasoning_engine_in_mold", "permission_enforcement_included", "semantic_truth_verifier_included"):
            self.assertFalse(config["implementation_boundary"][boundary_key])
        self.assertEqual(config["session_controls"]["human_analysis_default"], "opt_in")

    def test_dial_defaults_exact_keys_and_range(self):
        config = load_json("config/top_mold_chatgpt.json")
        dials = config["dials"]["defaults"]
        self.assertEqual(set(dials), DIAL_KEYS)
        self.assertEqual(config["dials"]["scale_min"], 0)
        self.assertEqual(config["dials"]["scale_max"], 100)
        for name, value in dials.items():
            with self.subTest(dial=name):
                self.assertIs(type(value), int)  # bool is deliberately rejected
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 100)

    def test_task_overlays_use_explicit_known_dial_overrides(self):
        config = load_json("config/top_mold_chatgpt.json")
        self.assertIn("task_overlays_merge_policy", config)
        self.assertTrue(config["task_overlays"])
        for overlay_name, overlay in config["task_overlays"].items():
            self.assertIn("enabled", overlay, overlay_name)
            self.assertIn("dial_overrides", overlay, overlay_name)
            self.assertNotIn("depth", overlay, overlay_name)
            self.assertLessEqual(set(overlay["dial_overrides"]), DIAL_KEYS)
            for value in overlay["dial_overrides"].values():
                self.assertIs(type(value), int)
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 100)

    def test_readiness_contract_values_and_rules_defined(self):
        config = load_json("config/top_mold_chatgpt.json")
        self.assertEqual(set(config["request_envelope"]["readiness_values"]), {"READY", "CLARIFICATION_REQUIRED", "BLOCKED"})
        self.assertEqual(set(config["readiness_invariants"]), {"READY", "CLARIFICATION_REQUIRED", "BLOCKED"})
        schema = load_json("schemas/request_envelope.schema.json")
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(schema)
        self.assertEqual(schema["properties"]["readiness"]["enum"], ["READY", "CLARIFICATION_REQUIRED", "BLOCKED"])
        self.assertEqual(config["request_envelope"]["schema_version"], "1.2")
        self.assertEqual(set(config["request_envelope"]["required_fields"]), set(schema["required"]))
        self.assertEqual(set(config["request_envelope"]["optional_fields"]), set(schema["properties"]) - set(schema["required"]))

    def test_example_request_envelope_satisfies_core_invariants(self):
        envelope = load_json("examples/request_interpretation.example.json")
        self.assertEqual(validate_envelope_contract(envelope), [])

    def test_epistemic_integrity_example_is_valid(self):
        envelope = load_json("examples/epistemic_integrity.example.json")
        self.assertEqual(validate_envelope_contract(envelope), [])

    def test_readiness_validator_catches_inconsistent_states(self):
        ready_with_blocker = {
            "schema_version": "1.2", "goal": "test", "readiness": "READY",
            "open_questions": [{"id": "Q1", "question": "Need input?", "blocking": True}],
        }
        clarification_without_blocker = {"schema_version": "1.2", "goal": "test", "readiness": "CLARIFICATION_REQUIRED"}
        blocked_without_reason = {"schema_version": "1.2", "goal": "test", "readiness": "BLOCKED"}
        self.assertTrue(validate_envelope_contract(ready_with_blocker))
        self.assertTrue(validate_envelope_contract(clarification_without_blocker))
        self.assertTrue(validate_envelope_contract(blocked_without_reason))
        ready_with_missing_resource = {
            "schema_version": "1.2", "goal": "test", "readiness": "READY",
            "resource_requests": [{"resource_id": "r1", "gap": "missing input", "status": "requested", "required_for_goal": True}],
        }
        self.assertTrue(validate_envelope_contract(ready_with_missing_resource))
        ready_with_unknown_context = {
            "schema_version": "1.2", "goal": "test", "readiness": "READY",
            "context_refs": [{"ref": "file.md", "availability": "unknown", "required_for_goal": True}],
        }
        self.assertTrue(validate_envelope_contract(ready_with_unknown_context))
        ready_with_blocking_conflict = {
            "schema_version": "1.2", "goal": "test", "readiness": "READY",
            "conflicts": [{
                "id":"C1","topic":"status","status":"unresolved","blocking":True,
                "claims":[{"statement":"active","source_ref":"A"},{"statement":"inactive","source_ref":"B"}]
            }]
        }
        self.assertTrue(validate_envelope_contract(ready_with_blocking_conflict))
        clarification_with_conflict_only = {
            "schema_version": "1.2", "goal": "test", "readiness": "CLARIFICATION_REQUIRED",
            "conflicts": [{
                "id":"C1","topic":"status","status":"unresolved","blocking":True,
                "claims":[{"statement":"active","source_ref":"A"},{"statement":"inactive","source_ref":"B"}]
            }]
        }
        self.assertEqual(validate_envelope_contract(clarification_with_conflict_only), [])

    def test_package_excludes_person_specific_artifacts(self):
        config = load_json("config/top_mold_chatgpt.json")
        boundary = config["package_data_boundary"]
        for key in (
            "contains_individual_profile_records", "contains_person_specific_preferences",
            "contains_personal_resource_manifests", "contains_account_identifiers_or_credentials",
        ):
            self.assertFalse(boundary[key], key)
        self.assertTrue(boundary["examples_are_synthetic"])
        self.assertFalse((ROOT / "PERSONAL_DATA_CONTRACT.md").exists())
        self.assertFalse((ROOT / "config/personal_resource_manifest.example.json").exists())
        self.assertFalse(config.get("personal_data_policy"))
        self.assertNotIn("personalization_depth", config["dials"]["defaults"])
        self.assertNotIn("retention_preference", config["dials"]["defaults"])
        self.assertNotIn("user_agency", config["dials"]["defaults"])
        self.assertFalse(config["implementation_boundary"]["personal_data_store_included"])

    def test_epistemic_integrity_defaults_are_explicit(self):
        config = load_json("config/top_mold_chatgpt.json")
        rules = config["epistemic_integrity"]
        self.assertTrue(rules["unknowns_must_remain_explicit"])
        self.assertTrue(rules["contradictions_must_not_be_silently_resolved"])
        self.assertTrue(rules["transformations_must_be_treated_as_potentially_lossy"])
        self.assertTrue(rules["unsupported_generalization_is_disallowed"])
        for dial in ("uncertainty_preservation", "contradiction_preservation", "transformation_fidelity"):
            self.assertGreaterEqual(config["dials"]["defaults"][dial], 80)

    def test_conformance_ids_are_unique_and_cover_failure_modes(self):
        cases_doc = load_json("tests/conformance_cases.json")
        ids = [case["id"] for case in cases_doc["cases"]]
        self.assertEqual(len(ids), len(set(ids)), "conformance case IDs must be unique")
        required = {
            "NEGATION-001", "QUOTE-001", "RESOURCE-001", "PERMISSION-001", "TRUTH-001",
            "PRECEDENCE-001", "UNKNOWN-001", "SEMANTIC-PROJECTION-001", "GENERALIZATION-001",
            "CONTRADICTION-PRESERVATION-001", "TRANSFORMATION-LOSS-001", "GOAL-DRIFT-001",
            "PREMATURE-COMPLETION-001"
        }
        self.assertTrue(required.issubset(set(ids)))
        for case in cases_doc["cases"]:
            self.assertTrue(case["input"].strip())
            self.assertTrue(case["expect"])

    def test_gamma_profile_red_team_ids_and_scope_cases_are_unique(self):
        doc = load_json("tests/gamma_profile_cases.json")
        self.assertEqual(doc["status"], "proposed_test_vectors_not_live_gamma_results")
        ids = [case["id"] for case in doc["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        required = {
            "GAMMA-SELECT-001", "GAMMA-TOPIC-NOT-SELECT-001", "GAMMA-OVERRIDE-INJECTION-001",
            "GAMMA-SCHEMA-EXTRA-001", "GAMMA-DIGEST-001", "GAMMA-SCOPE-001",
            "GAMMA-CAPABILITY-001", "GAMMA-AUTH-001", "GAMMA-UPDATE-001", "GAMMA-MULTI-001"
        }
        self.assertTrue(required.issubset(set(ids)))
        for case in doc["cases"]:
            self.assertTrue(case["input"].strip())
            self.assertTrue(case["expect"].strip())

    def test_authority_precedence_is_explicit(self):
        config = load_json("config/top_mold_chatgpt.json")
        precedence = config["authority_precedence"]
        self.assertGreaterEqual(len(precedence), 6)
        self.assertEqual(precedence[0], "platform_system_safety_and_actual_host_constraints")
        self.assertEqual(precedence[1], "current_explicit_task_instructions")

    def test_core_docs_and_schema_exist(self):
        required = [
            "CLAY_PERSONALIZATION.md", "COMMON_CORE.md", "COEXISTENCE_AND_NON_IMPOSITION.md", "MODULE_INTERFACE.md", "FAILURE_RECOVERY.md", "OUTCOME_LEARNING.md", "LLM_README.md", "MULTI_MODEL_ORCHESTRATION.md", "TOP_MOLD_CHATGPT.md", "SPEC.md", "CHATGPT_ADAPTER.md", "CONVERSATION_FLOW.md", "RESOURCE_PROTOCOL.md", "GAMMA_BRIDGE.md",
            "DATA_BOUNDARY.md", "CHANGELOG.md", "EVALUATION_PROTOCOL.md", "REVIEW_NOTES.md",
            "schemas/request_envelope.schema.json", "schemas/outcome_review.schema.json", "schemas/task_profile.schema.json", "schemas/gamma_import_packet.schema.json", "schemas/module_manifest.schema.json", "schemas/module_result.schema.json", "tools/validate_modules.py",
            "examples/gamma_profile_import_packet.example.json", "examples/outcome_review.failure.example.json", "examples/outcome_review.success.example.json", "tests/outcome_learning_cases.json", "tests/test_outcome_learning.py", "tests/coexistence_cases.json", "tests/test_coexistence_contract.py", "interfaces/gamma_provider.py", "tools/validate_gamma_profile.py", "tests/test_conversation_flow.py", "HUMAN_LLM_CO_EVOLUTION.md", "RECIPROCAL_EVIDENCE_EVALUATION.md", "PERFORMANCE_UTILIZATION.md", "schemas/evidence_bundle.schema.json", "examples/evidence_evaluation.example.json"
        ]
        for relative in required:
            with self.subTest(file=relative):
                path = ROOT / relative
                self.assertTrue(path.is_file())
                self.assertGreater(path.stat().st_size, 0)

    def test_version_markers_are_current_in_primary_docs(self):
        for relative in ["README.md", "CLAY_PERSONALIZATION.md", "COMMON_CORE.md", "COEXISTENCE_AND_NON_IMPOSITION.md", "FAILURE_RECOVERY.md", "OUTCOME_LEARNING.md", "LLM_README.md", "COEXISTENCE_AND_NON_IMPOSITION.md", "SPEC.md", "START_HERE_JA.md", "CHANGELOG.md", "BUILD_MANIFEST.md", "VALIDATION_REPORT.md"]:

            content = (ROOT / relative).read_text(encoding="utf-8")
            with self.subTest(file=relative):
                self.assertIn(VERSION, content)

    def test_gamma_delta_safety_extensions_are_non_delegable(self):
        config = load_json("config/top_mold_chatgpt.json")
        ext = config["control_plane_extensions"]
        self.assertTrue(ext["gamma_index"]["enabled"])
        self.assertFalse(ext["gamma_index"]["activation_authority"])
        self.assertEqual(ext["delta_index"]["role"], "OBSERVER_ONLY_DIFF_AND_RECONCILIATION")
        for key in ("can_authorize", "can_activate", "can_mutate_active_profile", "can_disable_safety"):
            self.assertFalse(ext["delta_index"][key])
        safety = ext["safety_plane"]
        self.assertEqual(safety["scope"], "GLOBAL_NON_DELEGABLE")
        self.assertTrue(safety["cross_cutting"])
        self.assertFalse(safety["may_be_placed_downstream_of_delta"])
        self.assertEqual(set(safety["protected_modules"]), {
            "hard_safety_override", "risk_boundary_engine", "recovery_path_engine",
            "situational_verification", "capability_declaration"})

    def test_index_and_safety_contract_files_exist(self):
        for relative in ("GAMMA_DELTA_ARCHITECTURE.md", "INDEX_THREE_PHASE_CONTRACT.md", "SAFETY_PLANE_BOUNDARY.md",
                         "gamma_index/index.py", "delta_index/observer.py",
                         "safety_plane/topology.py", "tools/validate_control_topology.py",
                         "examples/index_states/control_topology.example.json", "schemas/gamma_handoff.schema.json", "schemas/delta_observation.schema.json", "examples/index_states/gamma_handoff.example.json", "examples/index_states/delta_observation.example.json"):
            self.assertTrue((ROOT / relative).is_file(), relative)

    def test_gamma_delta_phase_contract_is_explicit_and_non_authoritative(self):
        config = load_json("config/top_mold_chatgpt.json")
        phases = config["index_phase_contract"]
        self.assertEqual(phases["gamma"]["phases"], ["DISCOVER", "RESOLVE", "HANDOFF"])
        self.assertTrue(phases["gamma"]["discover_default_excludes_held"])
        self.assertTrue(phases["gamma"]["discover_pagination_uses_revision_guard"])
        self.assertFalse(phases["gamma"]["ambiguous_candidate_auto_selection"])
        self.assertFalse(phases["gamma"]["retrieval_authorized_by_gamma"])
        self.assertFalse(phases["gamma"]["activation_authorized_by_gamma"])
        self.assertEqual(phases["delta"]["phases"], ["OBSERVE", "COMPARE", "RECONCILE"])
        self.assertFalse(phases["delta"]["capture_mutates_current"])
        self.assertFalse(phases["delta"]["compare_mutates_current"])
        self.assertTrue(phases["delta"]["compare_includes_source_reference"])
        self.assertEqual(phases["delta"]["accept_requires_prior_snapshot_match"], "VERSION_DIGEST_AND_SOURCE_REFERENCE")
        self.assertFalse(phases["delta"]["activation_authority"])

    def test_gamma_handoff_schema_forces_no_authority(self):
        from jsonschema import Draft202012Validator
        schema = load_json("schemas/gamma_handoff.schema.json")
        example = load_json("examples/index_states/gamma_handoff.example.json")
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(example)), [])
        unsafe = dict(example, retrieval_authorized=True)
        self.assertTrue(list(Draft202012Validator(schema).iter_errors(unsafe)))

    def test_delta_observation_schema_accepts_capture_without_event(self):
        from jsonschema import Draft202012Validator, FormatChecker
        schema = load_json("schemas/delta_observation.schema.json")
        example = load_json("examples/index_states/delta_observation.example.json")
        self.assertEqual(list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(example)), [])

    def test_schema_rejects_whitespace_and_oversized_inputs(self):
        base = {"schema_version": "1.2", "goal": "valid goal", "readiness": "READY"}
        self.assertTrue(validate_envelope_contract({**base, "goal": "   "}))
        blocked = {"schema_version": "1.2", "goal": "valid goal", "readiness": "BLOCKED", "readiness_reason": "   "}
        self.assertTrue(validate_envelope_contract(blocked))
        oversized = {
            **base,
            "requirements": [
                {"id": f"R{i}", "text": "valid", "priority": "must", "source": "explicit"}
                for i in range(101)
            ],
        }
        self.assertTrue(validate_envelope_contract(oversized))
        long_goal = {**base, "goal": "x" * 2001}
        self.assertTrue(validate_envelope_contract(long_goal))

    def test_shared_validator_rejects_duplicate_ids_across_lists(self):
        envelope = {
            "schema_version": "1.2", "goal": "valid goal", "readiness": "READY",
            "requirements": [{"id": "DUP", "text": "one", "priority": "must", "source": "explicit"}],
            "exclusions": [{"id": "DUP", "text": "two", "source": "explicit"}],
        }
        errors = validate_envelope_contract(envelope)
        self.assertTrue(any("duplicate record id" in error for error in errors), errors)

    def test_shared_validator_fails_safely_on_malformed_roots(self):
        for malformed in (None, [], "not an object", 42):
            with self.subTest(value=malformed):
                self.assertTrue(validate_envelope_contract(malformed))

    def test_red_team_cases_are_explicitly_proposed_not_observed(self):
        cases_doc = load_json("tests/red_team_cases.json")
        self.assertEqual(cases_doc["schema"], "top-mold/red-team/v0.3.4")
        self.assertIn("not observed LLM results", cases_doc["purpose"])
        cases = cases_doc["cases"]
        ids = [case["id"] for case in cases]
        self.assertGreaterEqual(len(cases), 12)
        self.assertEqual(len(ids), len(set(ids)))
        for case in cases:
            self.assertTrue(case["input"].strip())
            self.assertTrue(case["expected"])
            self.assertIn("class", case)

    def test_cli_rejects_oversized_json_before_parsing(self):
        import tempfile
        from contextlib import redirect_stderr
        from io import StringIO
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "oversized.json"
            path.write_bytes(b" " * (MAX_INPUT_BYTES + 1))
            stderr = StringIO()
            with redirect_stderr(stderr):
                exit_code = validate_envelope_main([str(path)])
            self.assertEqual(exit_code, 2)
            self.assertIn("byte limit", stderr.getvalue())




    def test_every_schema_string_has_a_maximum_length(self):
        schema = load_json("schemas/request_envelope.schema.json")
        unbounded = []
        def walk(node, path="$schema"):
            if isinstance(node, dict):
                if node.get("type") == "string" and "maxLength" not in node:
                    unbounded.append(path)
                for key, value in node.items():
                    walk(value, f"{path}.{key}")
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, f"{path}[{index}]")
        walk(schema)
        self.assertEqual(unbounded, [], f"unbounded schema strings: {unbounded}")

    def test_invalid_schema_is_reported_without_raising(self):
        import tempfile
        base = {"schema_version": "1.2", "goal": "valid goal", "readiness": "READY"}
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "invalid-schema.json"
            schema_path.write_text('{"type":"not-a-json-schema-type"}', encoding="utf-8")
            errors = validate_envelope_data(base, schema_path)
            self.assertTrue(errors)
            self.assertIn("could not load valid schema", errors[0])

    def test_custom_schema_size_is_bounded(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            schema_path = Path(tmp) / "oversized-schema.json"
            schema_path.write_bytes(b" " * (MAX_SCHEMA_BYTES + 1))
            errors = validate_envelope_data(
                {"schema_version":"1.2", "goal":"valid goal", "readiness":"READY"},
                schema_path,
            )
            self.assertTrue(errors)
            self.assertIn("schema file exceeds", errors[0])

    def test_why_it_matters_is_bounded_and_nonblank(self):
        base = {"schema_version": "1.2", "goal": "valid goal", "readiness": "READY"}
        q = {"id": "Q1", "question": "Question?", "blocking": False}
        self.assertTrue(validate_envelope_contract({**base, "open_questions": [{**q, "why_it_matters": "   "}]}))
        self.assertTrue(validate_envelope_contract({**base, "open_questions": [{**q, "why_it_matters": "x" * 2001}]}))
        self.assertEqual(validate_envelope_contract({**base, "open_questions": [{**q, "why_it_matters": "x" * 2000}]}), [])

    def test_optional_semantic_strings_reject_blank_values(self):
        base = {"schema_version": "1.2", "goal": "valid goal", "readiness": "READY"}
        self.assertTrue(validate_envelope_contract({**base, "note": "   "}))
        self.assertTrue(validate_envelope_contract({**base, "readiness_reason": "   "}))
        self.assertEqual(validate_envelope_contract({**base, "readiness_reason": None}), [])

    def test_cli_parse_errors_fail_closed_without_traceback(self):
        from contextlib import redirect_stderr, redirect_stdout
        from io import StringIO
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            for name, payload, expected in [
                ("huge_integer.json", "9" * 5000, "INPUT ERROR"),
                ("deep_nesting.json", "[" * 10000 + "0" + "]" * 10000, "INPUT ERROR"),
                ("duplicate_keys.json", '{"schema_version":"1.2","goal":"first","goal":"second","readiness":"READY"}', "duplicate JSON object key"),
            ]:
                with self.subTest(name=name):
                    path = Path(tmp) / name
                    path.write_text(payload, encoding="utf-8")
                    stderr, stdout = StringIO(), StringIO()
                    with redirect_stderr(stderr), redirect_stdout(stdout):
                        exit_code = validate_envelope_main([str(path)])
                    self.assertEqual(exit_code, 2)
                    self.assertIn(expected, stderr.getvalue())
                    self.assertNotIn("Traceback", stderr.getvalue())

    def test_cli_enforces_json_nesting_limit_but_ignores_brackets_in_strings(self):
        from contextlib import redirect_stderr, redirect_stdout
        from io import StringIO
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            too_deep = "{" * (MAX_JSON_DEPTH + 1) + "\"x\"" + "}" * (MAX_JSON_DEPTH + 1)
            valid_string = json.dumps({"schema_version":"1.2", "goal":"literal {{{[[[ text", "readiness":"READY"})
            for name, payload, expected_code, expected_text in [
                ("too_deep.json", too_deep, 2, "nesting depth exceeds"),
                ("brackets_in_string.json", valid_string, 0, "VALID"),
            ]:
                with self.subTest(name=name):
                    path = Path(tmp) / name
                    path.write_text(payload, encoding="utf-8")
                    stderr, stdout = StringIO(), StringIO()
                    with redirect_stderr(stderr), redirect_stdout(stdout):
                        result = validate_envelope_main([str(path)])
                    self.assertEqual(result, expected_code)
                    self.assertIn(expected_text, stderr.getvalue() + stdout.getvalue())

    def test_transformation_and_conflict_schema_guards(self):
        base = {"schema_version":"1.2", "goal":"test", "readiness":"READY"}
        missing_loss_note = {
            **base,
            "transformations":[{"id":"T1","source_ref":"src","output_ref":"out","operation":"ocr","fidelity":"known_lossy"}],
        }
        self.assertTrue(validate_envelope_contract(missing_loss_note))
        missing_verification = {
            **base,
            "transformations":[{"id":"T1","source_ref":"src","output_ref":"out","operation":"parsing","fidelity":"lossless_verified"}],
        }
        self.assertTrue(validate_envelope_contract(missing_verification))
        resolved_without_ref = {
            **base,
            "conflicts":[{"id":"C1","topic":"state","status":"resolved","blocking":False,
                "claims":[{"statement":"A","source_ref":"a"},{"statement":"B","source_ref":"b"}]}],
        }
        self.assertTrue(validate_envelope_contract(resolved_without_ref))
        too_few_claims = {
            **base,
            "conflicts":[{"id":"C1","topic":"state","status":"unresolved","blocking":False,
                "claims":[{"statement":"A","source_ref":"a"}]}],
        }
        self.assertTrue(validate_envelope_contract(too_few_claims))

    def test_duplicate_resource_ids_are_rejected(self):
        envelope = {
            "schema_version": "1.2", "goal": "valid goal", "readiness": "READY",
            "resource_requests": [
                {"resource_id":"same","gap":"gap one","status":"declared","required_for_goal":False},
                {"resource_id":"same","gap":"gap two","status":"declared","required_for_goal":False},
            ],
        }
        errors = validate_envelope_contract(envelope)
        self.assertTrue(any("duplicate resource_id" in error for error in errors), errors)

    def test_mode_lock_scope_is_explicit(self):
        config = load_json("config/top_mold_chatgpt.json")
        rule = config["session_controls"]["mode_lock_rule"]
        self.assertIn("turn", rule)
        self.assertIn("session-level", rule)

    def test_json_documents_parse(self):
        for relative in [
            "config/top_mold_chatgpt.json", "examples/request_interpretation.example.json",
            "examples/epistemic_integrity.example.json", "tests/conformance_cases.json", "tests/red_team_cases.json", "tests/gamma_profile_cases.json", "tests/conversation_flow_cases.json",
            "schemas/request_envelope.schema.json", "schemas/outcome_review.schema.json", "schemas/task_profile.schema.json", "schemas/gamma_import_packet.schema.json", "schemas/module_manifest.schema.json", "schemas/module_result.schema.json", "examples/gamma_profile_import_packet.example.json", "config/clay_personalization.json", "examples/modules/code_specialist.example.json", "examples/modules/work_workflow.example.json", "examples/modules/multi_model_review.example.json", "examples/module_results/blocked_integration.example.json", "tests/module_conformance_cases.json", "tests/failure_recovery_cases.json"
        ]:
            with self.subTest(file=relative):
                self.assertIsInstance(load_json(relative), dict)


if __name__ == "__main__":
    unittest.main()
