# Validation Report — Top Mold v0.3.2 ChatGPT Model

**Validation type:** package structure, configuration consistency, JSON Schema, negative/boundary contract probes, and archive integrity  
**LLM behavior tested:** no  
**External integration tested:** no

## Checks performed

- `python -m unittest discover -s tests -v` — **32 tests passed**.
- `python tools/run_destructive_probe_matrix.py` — **23/23 schema/contract probes met expected outcomes**.
- `python tools/validate_envelope.py examples/request_interpretation.example.json` — **valid**.
- Validated `schemas/request_envelope.schema.json` against JSON Schema Draft 2020-12 using `jsonschema` 4.26.0 in the build environment.
- Parsed all package JSON documents successfully.
- The final ZIP passed `unzip -t`, and tests/probes were rerun from a fresh extraction of that ZIP.
- Rejected whitespace-only and zero-width-only text in semantic fields, duplicate IDs across record arrays, unbounded inputs, malformed roots, readiness contradictions, missing evidence pointers for claimed `available`/`used` resources, unknown fields, and CLI input files above 2,000,000 bytes.
- Confirmed boundary values at 2,000 characters for `goal` and 100 entries for bounded arrays remain accepted.

## Result

The included package-level contract checks passed. This establishes the behavior of the JSON Schema and deterministic validator for the tested cases only. An `evidence_ref` is a trace pointer required for auditability; the validator does **not** verify that the referenced resource or event genuinely exists.

## Not established

- That ChatGPT follows every instruction under all prompts or product surfaces;
- that prompt injection, negation, quotation, ambiguity, and permission edge cases are reliably handled by an actual model;
- that a dial improves measured performance;
- that hidden reasoning or compute is allocated to a coordinate;
- that any file, memory store, account, API, or external mold has been connected;
- that an LLM's factual claims will be correct;
- that a host permission system enforces external-action policy.

`tests/conformance_cases.json` and `tests/red_team_cases.json` remain proposed model-behavior test vectors, not observed LLM results. Use `EVALUATION_PROTOCOL.md` for controlled tests against the target model before claiming behavioral improvement.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.
