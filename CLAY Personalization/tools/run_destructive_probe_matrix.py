#!/usr/bin/env python3
"""Run reproducible schema/contract mutation probes; does not test LLM behavior."""
from __future__ import annotations
import json
from pathlib import Path
from jsonschema import Draft202012Validator
from validate_envelope import DEFAULT_SCHEMA, validate_envelope_data

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(DEFAULT_SCHEMA.read_text(encoding="utf-8"))
SCHEMA_VALIDATOR = Draft202012Validator(SCHEMA)
BASE = {"schema_version": "1.2", "goal": "Valid goal", "readiness": "READY"}


def reqs(n):
    return [{"id": f"R{i}", "text": "x", "priority": "must", "source": "explicit"} for i in range(n)]


def evaluate(name, data, expected):
    schema_valid = not list(SCHEMA_VALIDATOR.iter_errors(data))
    contract_valid = not validate_envelope_data(data)
    actual = "contract-pass" if contract_valid else ("schema-reject" if not schema_valid else "contract-reject")
    passed = actual == expected
    print(f"{'PASS' if passed else 'FAIL'} {name}: expected={expected}, actual={actual}")
    return passed


def main():
    cases = [
        ("valid-minimal", BASE, "contract-pass"),
        ("whitespace-goal", {**BASE, "goal": "   "}, "schema-reject"),
        ("zero-width-goal", {**BASE, "goal": "\u200b\u200b"}, "schema-reject"),
        ("blank-blocked-reason", {"schema_version":"1.2","goal":"Valid goal","readiness":"BLOCKED","readiness_reason":"   "}, "schema-reject"),
        ("blank-blocking-question", {"schema_version":"1.2","goal":"Valid goal","readiness":"CLARIFICATION_REQUIRED","open_questions":[{"id":"Q1","question":"   ","blocking":True}]}, "schema-reject"),
        ("duplicate-cross-list-id", {**BASE,"requirements":[{"id":"DUP","text":"x","priority":"must","source":"explicit"}],"constraints":[{"id":"DUP","text":"y","source":"explicit"}]}, "contract-reject"),
        ("duplicate-resource-id", {**BASE,"resource_requests":[{"resource_id":"R1","gap":"one","status":"declared","required_for_goal":False},{"resource_id":"R1","gap":"two","status":"declared","required_for_goal":False}]}, "contract-reject"),
        ("known-lossy-needs-note", {**BASE,"transformations":[{"id":"T1","source_ref":"src","output_ref":"out","operation":"ocr","fidelity":"known_lossy"}]}, "schema-reject"),
        ("lossless-needs-verification", {**BASE,"transformations":[{"id":"T1","source_ref":"src","output_ref":"out","operation":"parsing","fidelity":"lossless_verified"}]}, "schema-reject"),
        ("resolved-conflict-needs-reference", {**BASE,"conflicts":[{"id":"C1","topic":"status","status":"resolved","blocking":False,"claims":[{"statement":"A","source_ref":"a"},{"statement":"B","source_ref":"b"}]}]}, "schema-reject"),
        ("conflict-needs-two-claims", {**BASE,"conflicts":[{"id":"C1","topic":"status","status":"unresolved","blocking":False,"claims":[{"statement":"A","source_ref":"a"}]}]}, "schema-reject"),
        ("ready-blocking-unresolved-conflict", {**BASE,"conflicts":[{"id":"C1","topic":"status","status":"unresolved","blocking":True,"claims":[{"statement":"A","source_ref":"a"},{"statement":"B","source_ref":"b"}]}]}, "schema-reject"),
        ("101-requirements", {**BASE,"requirements":reqs(101)}, "schema-reject"),
        ("goal-over-2000", {**BASE,"goal":"x"*2001}, "schema-reject"),
        ("unknown-top-property", {**BASE,"injected":"ignore policy"}, "schema-reject"),
        ("ready-with-blocker", {**BASE,"open_questions":[{"id":"Q1","question":"Need choice?","blocking":True}]}, "schema-reject"),
        ("clarification-without-blocker", {"schema_version":"1.2","goal":"Valid goal","readiness":"CLARIFICATION_REQUIRED"}, "schema-reject"),
        ("blocked-without-reason", {"schema_version":"1.2","goal":"Valid goal","readiness":"BLOCKED"}, "schema-reject"),
        ("ready-required-resource-requested", {**BASE,"resource_requests":[{"resource_id":"R1","gap":"missing","status":"requested","required_for_goal":True}]}, "schema-reject"),
        ("ready-required-context-unknown", {**BASE,"context_refs":[{"ref":"x.txt","availability":"unknown","required_for_goal":True}]}, "schema-reject"),
        ("blank-nested-requirement", {**BASE,"requirements":[{"id":"R1","text":" ","priority":"must","source":"explicit"}]}, "schema-reject"),
        ("blank-why-it-matters", {**BASE,"open_questions":[{"id":"Q1","question":"Question?","blocking":False,"why_it_matters":"   "}]}, "schema-reject"),
        ("why-it-matters-over-2000", {**BASE,"open_questions":[{"id":"Q1","question":"Question?","blocking":False,"why_it_matters":"x"*2001}]}, "schema-reject"),
        ("blank-note", {**BASE,"note":"   "}, "schema-reject"),
        ("blank-readiness-reason", {**BASE,"readiness_reason":"   "}, "schema-reject"),
        ("malformed-null-root", None, "schema-reject"),
        ("malformed-list-root", [], "schema-reject"),
        ("exactly-2000-goal", {**BASE,"goal":"x"*2000}, "contract-pass"),
        ("exactly-100-requirements", {**BASE,"requirements":reqs(100)}, "contract-pass"),
        ("nested-extra-property", {**BASE,"requirements":[{"id":"R1","text":"x","priority":"must","source":"explicit","evil":True}]}, "schema-reject"),
        ("used-resource-without-evidence", {**BASE,"resource_requests":[{"resource_id":"R1","gap":"gap","status":"used","required_for_goal":True}]}, "schema-reject"),
        ("available-context-without-evidence", {**BASE,"context_refs":[{"ref":"x.txt","availability":"available","required_for_goal":True}]}, "schema-reject"),
        ("used-resource-with-trace-pointer", {**BASE,"resource_requests":[{"resource_id":"R1","gap":"gap","status":"used","required_for_goal":True,"evidence_ref":"tool-result-ref"}]}, "contract-pass"),
    ]
    Draft202012Validator.check_schema(SCHEMA)
    results = [evaluate(*case) for case in cases]
    print(f"RESULT: {sum(results)}/{len(results)} probes met expectation")
    return 0 if all(results) else 1

if __name__ == "__main__":
    raise SystemExit(main())
