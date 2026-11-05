# Destruction Test Report — Top Mold v0.3.2

## Executive result

The v0.3.1 baseline passed its 12 existing structural tests, but a separate 20-case mutation probe found gaps the original suite did not cover. The package was hardened, versioned as v0.3.2, and re-tested. The final package currently passes **32 automated tests** and **23/23 repeatable schema/contract probes**.

## v0.3.1 failures found

| Attack / mutation | Baseline result | Risk |
|---|---|---|
| Goal consisting only of ordinary spaces | Accepted by JSON Schema | A semantically empty request could appear valid |
| `BLOCKED` reason or blocking question consisting of spaces | Accepted by JSON Schema | Readiness states could carry empty explanations |
| Duplicate IDs across different record arrays | Accepted by Schema alone | Requirement/constraint references could be ambiguous |
| 101+ requirements or a 2,001+ character goal | Accepted | No input-shape/resource bounds at the contract layer |
| Malformed root values passed to helper-level checks | Not uniformly covered | Validators could crash or callers could mis-handle errors |

## v0.3.2 countermeasures

- Added maximum lengths and item counts to the request schema.
- Rejected whitespace-only and common zero-width/bidi-format-only semantic strings.
- Added a shared validator for JSON Schema plus cross-array record-ID uniqueness.
- Made malformed-root validation fail closed rather than crash.
- Added a 2,000,000-byte CLI file-read ceiling before JSON parsing.
- Required `evidence_ref` trace pointers for `context_refs.available` and `resource_requests.available/used` states.
- Clarified turn-scoped mode overrides versus explicit session-level mode changes.
- Added explicit rules for treating file/quote/tool-return content as untrusted data unless bounded authority is delegated.
- Added 16 adversarial model-level cases separately from deterministic code tests.

## Final package test results

- Unit tests: **32 passed**.
- Repeatable destructive schema/contract matrix: **23/23 expected results**.
- JSON Schema Draft 2020-12 meta-schema check: **passed**.
- Example envelope CLI validation: **valid**.

Run from the package root:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/validate_envelope.py examples/request_interpretation.example.json
python tools/run_destructive_probe_matrix.py
```

## Residual risks and scope limits

1. **Model-level prompt injection is not proven resistant.** The 16 entries in `tests/red_team_cases.json` are proposed prompts and expected behavior, not runs against a live ChatGPT endpoint. A controlled model-level harness is still needed.
2. **Evidence references are not proof.** The validator checks that a pointer is present and structurally valid; it cannot inspect the host, confirm file presence, or prove that an operation was actually performed.
3. **No permission enforcement.** The package contains declarative rules but no runtime that can prevent unauthorized side effects. The host must enforce approvals.
4. **No factuality guarantee.** A structurally valid envelope can still describe a false claim, and model outputs can still be wrong.
5. **Local file size ceiling is not a general service DoS defense.** It bounds this CLI's read path; it is not a sandbox for untrusted execution.

## Verdict

v0.3.2 is materially harder to confuse at the schema/contract layer. It should be described as **structurally hardened and adversarially tested at the contract level**, not as fully secure or behaviorally validated.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.
