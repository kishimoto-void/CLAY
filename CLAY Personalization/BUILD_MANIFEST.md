# Build Manifest — CLAY Personalization v0.4.3

- Immediate base archive: `clay_personalization_v0.4.2_coexistence.zip`.
- Release archive: `clay_personalization_v0.4.3_iterative_coexistence.zip`.
- Root directory: `clay_personalization_v0.4.3_iterative_coexistence/`.
- Release intent: scope-complete deliverables, open-ended exploration, reproducible successes, testable failure prevention, optional after-action reflection, and user-confirmed next-step changes.
- No autonomous planner, iteration scheduler, persistent checkpoint database, or live provider conformance runner is included.

## v0.4.3 changes

1. Added `COMPLETION_AND_CONTINUING_EXPLORATION.md` as the normative contract for scope-level completion and ongoing project exploration.
2. Added an optional `iteration_checkpoint` schema, synthetic example, and 19 proposed conformance vectors.
3. Explicitly separated deliverable completion from project status; a release can be complete for its scope while the larger project remains open.
4. Added preservation of stable checkpoints and clarified that a later iteration is not retroactive failure of an earlier release.
5. Required meaningful success reviews to capture reproduction conditions and limits, and meaningful failure lessons to include testable prevention/detection and verification.
6. Made formal reviews proportionate and optional; pause, close, no-next-step, and user-declined review are valid outcomes.
7. Required user confirmation for material changes of scope or priority.
8. Updated current-version markers, Gamma profile CLI defaults, and associated regression tests to `0.4.3`.
9. Clarified that exploration and discovery have value beyond defect removal, while curiosity and exploratory tone remain user-led and are not forced.
10. Added explicit reciprocal, gradual understanding without requiring the user and LLM to converge or become alike.

## Source and compatibility

- Base SHA-256 is recorded in `SOURCE_BASE_SHA256.txt`.
- The legacy `config/top_mold_chatgpt.json` remains a byte-equivalent JSON alias of canonical `config/clay_personalization.json`.
- The legacy `TOP_MOLD_CHATGPT.md` filename remains as a compatibility document.
- Request Envelope 1.2, Gamma/Delta boundaries, the Safety Plane topology, module interfaces, and non-imposition constraints are preserved.

## Verification boundary

This manifest records package construction and local validation only. Test results do not establish live LLM adherence, long-term cognitive effects, production safety, source authenticity, or correctness outside the tested environment. See `VALIDATION_REPORT.md` and `test-results/v0.4.3/`.


## 2026-11-05 audit addendum (release version retained at v0.4.3)

- Clarified tentative candidate-set handling and the independence of initiative and verification in `CONVERSATION_FLOW.md`, `SPEC.md`, and canonical/legacy config files.
- Added `INTERACTION_CALIBRATION_AUDIT.md`, 15 synthetic interaction-calibration vectors, 8 static traceability tests, and logs under `test-results/v0.4.3-audit/`.
- No live LLM runner, profile persistence, domain specialist, or runtime enforcement was added.


## 2026-11-05 publication-documentation addendum (package version retained at v0.4.3)

- Reworked `README.md` as a human-facing bilingual introduction with project purpose, non-goals, ChatGPT-first scope, current implementation boundaries, getting-started guidance, legal/normative considerations, community direction, and licensing status.
- Added `CHATGPT_LLM_SPEC.md` as the ChatGPT-oriented LLM operating specification. It distinguishes implemented, specified, and proposed behavior; preserves the platform/host authority boundary; and explicitly describes current non-capabilities.
- Updated `LLM_README.md`, `CLAY_PERSONALIZATION.md`, and `CHATGPT_ADAPTER.md` to point to the new entry documents and clarify that other-provider compatibility is a future direction, not a current claim.
- Documentation-only change. No implementation, schema, runtime capability, provider integration, or versioned API was added.
- The package remains an experimental v0.4.3 preview; this addendum does not establish v1.0 readiness or live ChatGPT conformance.


## 2026-11-05 modification-guide addendum (package version retained at v0.4.3)

- Added `MODIFICATION_GUIDE.md` for end users, with examples spanning personal settings, behavior preferences, task-local settings, specialist modules, and carefully isolated Core changes.
- Updated `CHATGPT_LLM_SPEC.md` to specification version 0.2 with modification classification, baseline-preservation guidance, module-contract limitations, and change-record requirements.
- Updated `LLM_README.md` and `README.md` to reference the modification guide.
- Added a schema-valid shopping module manifest example under `examples/modules/`; it is declarative only.
- Documentation and example-only update. No automatic module loader/executor, persistence service, runtime permission enforcement, or new provider adapter was added.
