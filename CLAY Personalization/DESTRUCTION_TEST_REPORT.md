# Destruction Test Report — Top Mold v0.3.7 (inherited envelope probes retained)

## Scope

This report covers deterministic mutation tests of the request-envelope schema and validator. The probes do not attack a live service or test an LLM's internal behavior.

## Observed result

**33 / 33 probes met their expected outcome.** The complete output is in `test-results/DESTRUCTIVE_PROBE_LOG.txt`.

## Probe families

- Blank, whitespace-only, and invisible-character values.
- Oversized scalar fields and arrays at/over configured boundaries.
- Duplicate record IDs across requirement/constraint/exclusion/question/transformation/conflict collections.
- Duplicate resource IDs.
- Readiness inconsistencies, including `READY` with blocking questions, missing required resources, unavailable required context, or unresolved blocking conflicts.
- Missing evidence references for resources/context declared available or used.
- Transformation records marked `known_lossy` without a loss note, or `lossless_verified` without a verification reference.
- Resolved conflicts without a resolution reference and conflicts with fewer than two claims.
- Unknown fields at the envelope and nested-object levels.
- Malformed JSON roots and valid boundary values.

Additional unit tests check byte limits, custom-schema limits, JSON maximum nesting depth (64), rejection at depth 65, and correct ignoring of bracket characters inside JSON strings.

## Gamma bridge coverage

`tests/gamma_profile_cases.json` contains 10 proposed scenarios for explicit selection, topic/command distinction, profile injection, schema extension attempts, digest mismatch, task scope, missing capabilities, source authentication, updates, and multiple-profile composition. These are test vectors only; they have not been run against a live Gamma connector or an LLM adapter. Deterministic Gamma bridge implementation checks are included in the 78-test unit suite.

## Interpretation

A passing probe means the schema/validator accepted or rejected that synthetic input as expected. It does not prove resistance to arbitrary hostile inputs, parser vulnerabilities in every runtime, live model compliance, or security of downstream systems. Continue fuzzing and review if the envelope is embedded in a service that accepts untrusted network input.


## v0.3.7 conversation-flow test scope

The v0.3.6 request-envelope probe results above are retained as historical results. v0.3.7 adds 6 structural tests for the new conversation-flow policy and 12 synthetic model-level conformance vectors. These vectors are proposed scenarios, not live model execution. The full v0.3.7 validation summary is recorded in `VALIDATION_REPORT.md`.

## v0.3.8 Gamma / Delta phase probes

The v0.3.8 phase test suite adds synthetic probes for invalid discovery limits/offsets, held and terminal entries, mismatched expected identities, failed source handoff, observation ID collisions, repeated compare calls, and stale candidate acceptance after a competing candidate is reconciled. These are deterministic local contract tests; they are not penetration tests, source-authentication tests, or live LLM behavior trials.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.


## v0.3.9 scope note

The inherited request-envelope destructive probe matrix was re-run for v0.3.9 and all 33 probes met their expected outcomes. The new v0.3.9 relationship/evidence/utilization contracts also have six focused static/schema tests in `tests/test_v039_collaboration_contract.py`. These tests check declared boundaries and example conformance; they do not test the semantic accuracy of an LLM's evidence judgments, a live personalization loop, source authenticity, or user experience.

> **Carried-forward contract:** This document preserves an earlier contract. CP v0.4.3 adds scope-complete iteration, project continuity, reproducible-success review, and testable failure prevention; see `LLM_README.md`, `OUTCOME_LEARNING.md`, and `COMPLETION_AND_CONTINUING_EXPLORATION.md`. Prior contracts remain in force.
