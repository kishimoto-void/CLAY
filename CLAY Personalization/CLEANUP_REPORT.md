# Historical Cleanup Report — Top Mold v0.3.7

> Historical package-cleanup record for v0.3.7. The v0.3.8 build and validation are documented in `BUILD_MANIFEST.md` and `VALIDATION_REPORT.md`.

## Scope

- Source archive: `top_mold_v0.3.7_gamma_delta_conversation_flow.zip`
- Output: `top_mold_v0.3.7_gamma_delta_conversation_flow_CLEAN.zip`
- Cleanup type: package-only cleanup; no runtime, schema, configuration, or protocol behavior changes intended.

## Changes

- Retained the complete `top_mold_v0.3.7_gamma_delta_conversation_flow/` tree.
- Removed the duplicate `top_mold_v0.3.6_gamma_delta_control_plane/` top-level tree from the distribution archive.
- Preserved the v0.3.7 relative paths and file contents.
- Added this cleanup report.
- Regenerated the SHA-256 sidecar for the final archive.

## Validation of final archive

- ZIP integrity (`ZipFile.testzip`): PASS
- Clean extraction: PASS
- Top-level roots: exactly one, `top_mold_v0.3.7_gamma_delta_conversation_flow`
- v0.3.6 root present: NO
- Archive entries: 91 (including directory entries)
- Regular files: 78
- Test suite: `python -m pytest -q` — 138 passed, 77 subtests passed

## Scope limitations

This verifies package integrity and the included automated test suite in the current execution environment. It does not establish live LLM behavior, independent evaluator results, or production safety. No claim is made that the cleanup changes model behavior.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.
