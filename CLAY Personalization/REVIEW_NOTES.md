# Review Notes — Top Mold v0.3.7

## Review objective

Convert v0.3.3 into a generic control contract with no person-specific data structures, while carrying N3-derived epistemic lessons back into the top-level rules.

## Findings from v0.3.3

1. The package bundled a Personal Data Contract, personal-resource manifest example, and profile-oriented dials. These were not required for a generic TOP control contract.
2. The contract described factual distinctions but did not elevate preservation of unknowns, unresolved contradictions, and lossy input transformations into a unified normative section.
3. The CLI rejected excessive nesting through Python parser failure, but did not state or enforce a package-specific nesting threshold.
4. Resource request IDs were not checked for duplicates within the resource-request collection.
5. The envelope had no first-class record for transformations or competing source claims.

## v0.3.5 changes

- Removed `PERSONAL_DATA_CONTRACT.md` and `config/personal_resource_manifest.example.json`. These are historical removal references, not active package paths; current exclusions and handling boundaries are defined in `DATA_BOUNDARY.md`.
- Removed person-profile/persistence fields and associated profile dials. Generic task-domain overrides remain and are task categories, not person profiles.
- Added `DATA_BOUNDARY.md` and machine-readable package exclusion flags.
- Added dials: `uncertainty_preservation`, `contradiction_preservation`, and `transformation_fidelity`; renamed `user_agency` to `human_control`.
- Added normative rules against unsupported gap-filling, forced coherence, unbounded generalization, and untracked lossy transformations.
- Added conformance cases for blank completion, semantic projection, overgeneralization, contradictions, transformation loss, and goal drift.
- Added JSON maximum-depth and custom-schema size enforcement, plus duplicate `resource_id` validation.
- Bumped the envelope to schema 1.2 with reference-only transformation records and source-linked contradiction records; a blocking unresolved conflict prevents `READY`.

## Deliberately not added

- No personal memory, user profile, identity store, or personal-resource manifest.
- No LLM API client or autonomous execution runtime.
- No prompt-injection detector claim or semantic truth verifier.
- No access-control enforcement implementation.
- No claims that new dials directly control hidden model internals.

## Residual limitations

- Instructions are declarative and depend on the executing model and host.
- A JSON schema/validator can check structure, not factual truth or whether a trace pointer is authentic.
- Conformance prompts are test vectors until run in blinded, controlled model trials.
- Transformation provenance is a contract requirement; the package does not automatically inspect or reconstruct arbitrary transformations.


## v0.3.5 Gamma bridge review

- Gamma is a selector/resource provider; Top Mold owns validation and overlay composition; Delta observes host-confirmed version/state events.
- The imported artifact is restricted to a task-domain profile and current-task-session scope. It is not a personal profile or memory import.
- The first skeleton supports one Gamma profile per task. Multi-profile auto-composition is deliberately disabled.
- The bridge has no network connector, source authenticator, permission enforcement, auto-loader, runtime activator, persistence, or Delta subscriber.
- SHA-256 checks canonical content consistency only; it is not source authentication. Host declarations in a packet are not authenticated by the local validator.
- The validator emits a detached candidate-overlay preview and plan, but always reports `NOT_INVOKED` / `NOT_ACTIVATED`.
- Packet-embedded host check claims are never treated as authorization; host decisions must arrive out-of-band from the integrating adapter with an evidence reference.


## v0.3.6 Gamma / Delta / Safety Plane review

- Gamma and Delta are classified as independent control-plane subsystems with replaceable module interfaces, not as ordinary task processors.
- Gamma retains unresolved information with explicit hold reason, open questions, preserved references, and revisit triggers.
- Delta detects state/version changes but does not mutate current state until an evidence-backed reconciliation is accepted.
- Safety components are global cross-cutting authorities. In particular, Risk Boundary and Recovery Path must not sit downstream of Delta or depend on Gamma/Delta profiles.
- Delta has no authorization, activation, active-profile mutation, or safety-disable authority.
- The current code is an in-memory skeleton; storage, connectors, live events, runtime enforcement, and actual safety evaluation remain future work.


## v0.3.7 ChatGPT conversation-flow review

- Identified an adapter usability gap: existing epistemic-integrity rules said *what* to preserve but did not sufficiently specify *when/how much* conversational structure to expose.
- Added `CONVERSATION_FLOW.md`: answer-first natural conversation, soft non-linear progression, incremental decomposition, hypothesis handling without reflexive endorsement, explicit rigor triggers, one-question clarification discipline, and anti-projectization.
- Kept conversation flow separate from task mode and did not add a new numeric dial, parser, inference engine, or persistence backend.
- Retained schema 1.2 and all Gamma/Delta/Safety Plane boundaries.
- Added 12 synthetic model-level cases plus deterministic structural tests; no live behavioral improvement claim is made.

## v0.3.8 Gamma / Delta three-phase review

- Gamma is now expressed as bounded discovery, exact candidate resolution, and reference-only host handoff.
- Discovery excludes `HELD` by default, offers deterministic pagination metadata with an index-revision guard, and does not claim semantic ranking.
- Handoff cannot authorize resource retrieval or activation, even when the catalog field says `source_status=VERIFIED`.
- Delta now exposes capture and comparison separately; the legacy `observe()` method remains a compatibility wrapper.
- Delta acceptance now uses a compare-and-swap-style guard against the candidate's recorded prior version/digest/source reference, preventing a stale candidate from overwriting a newer reconciled snapshot.
- Delta comparison treats a source-reference change as a candidate change even when the content digest is unchanged.
- Gamma copies list-backed claims/tags into immutable tuples to prevent callers from mutating registered metadata after registration.
- A supplied observation ID is idempotent within one process; this is not cross-process persistence or durable exactly-once delivery.
- No user profile, personal data store, Middle Mold, domain-specific module, live connector, or persistence backend was introduced.


## Additional strictness checks (v0.3.8)

- Gamma continuation requests require the exact index revision returned by the preceding page; an omitted revision is rejected.
- Gamma entry claims/tags are frozen once from finite tuple/list inputs; query tag iterables are bounded to a sentinel item beyond the configured maximum.
- Delta hold origin is a typed field (`SYSTEM_COMPETITION`, `USER`, `STALE_BASE`) rather than inferred from caller-controlled free-form reason text.
- Accepting a candidate moves other unresolved candidates to stale-base hold; a fresh observation can be compared against the newly reconciled snapshot without being blocked by stale historical candidates.
- Rejecting/superseding a candidate releases only automatic system-competition holds; explicit caller-created holds remain held.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.


## v0.4.0 review focus

The v0.4.0 changes formalize the CLAY Common Core and module interface. The key audit points are: capability/behavior separation; no module authority over Common Core or Safety Plane; truthful limitation diagnosis; bounded retry rules; partial-result preservation; composite fault localization; and no use of model majority as calibrated confidence.
