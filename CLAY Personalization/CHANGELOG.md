# Changelog

## 0.4.3 — Modification guide documentation addendum (2026-11-05; no version bump)

- Added `MODIFICATION_GUIDE.md` with practical examples for personal settings, behavior preferences, task-local instructions, specialist-module design, and cautious Core changes.
- Expanded `CHATGPT_LLM_SPEC.md` to specification version 0.2 with a bounded modification workflow, v0.4.3 generic Core baseline guidance, module-contract honesty, and change-record requirements.
- Updated `LLM_README.md` and `README.md` to expose the human modification guide and direct ChatGPT to use it when customization is requested.
- Added a schema-valid illustrative shopping module manifest example; it remains declarative and is not auto-loaded or executed.
- Documentation-only update; no runtime, loader, persistence, module execution, or provider integration was added.

## 0.4.3 — Publication documentation addendum (2026-11-05; no version bump)

- Reworked `README.md` for human readers, including the CLAY metaphor, individual-led adaptation, ChatGPT-first scope, implemented/non-implemented boundaries, laws and norms, community direction, and licensing caveat.
- Added `CHATGPT_LLM_SPEC.md`, a ChatGPT-oriented operating specification that explicitly subordinates package instructions to platform policies, applicable laws, and real host permissions.
- Updated LLM navigation and adapter documentation.
- Clarified that v0.4.3 is an experimental, incomplete preview and that v1.0 is a future maturity goal, not a current guarantee.
- Documentation-only change; no runtime, persistence, automatic learner, module loader, or new provider adapter was added.

## 0.4.3 — Scope completion and continuing exploration

### 2026-11-05 audit clarification (no version bump)

- Added a bounded rule: user-supplied tentative options are starting points, not necessarily exhaustive; explicitly bounded comparisons remain bounded.
- Clarified that initiative and verification are independent dimensions. Work-related tasks emphasize provenance, assumptions, reproducibility, and checked/unchecked status without automatic exhaustive formalism.
- Kept individual proactiveness/detail preferences in the behavior-profile layer; no user-specific data or persistence was added.
- Added 15 synthetic interaction-calibration test vectors and 8 structural traceability tests. These are not live LLM behavior results.
- See `INTERACTION_CALIBRATION_AUDIT.md` and `test-results/v0.4.3-audit/`.


- Added `COMPLETION_AND_CONTINUING_EXPLORATION.md` as a normative contract for aiming at complete scoped deliverables while leaving larger projects open to future exploration.
- Distinguished `COMPLETE_FOR_SCOPE` from the wider project's `OPEN`, `PAUSED`, or `CLOSED` state; preserved stable checkpoints and prohibited treating later iteration as retroactive failure.
- Added an optional iteration-checkpoint schema and synthetic example for acceptance criteria, effective patterns, reproduction conditions, failure prevention, unknowns, and user-confirmed next-step decisions.
- Required meaningful success reviews to preserve reproducibility conditions and boundaries; material failure lessons should become testable prevention or detection measures.
- Made after-action reflection proportionate rather than mandatory; pause, close, no next step, and user-declined review remain valid.
- Kept the LLM focused on the current requested issue and required confirmation before material scope or priority changes.
- Updated current-version references, CLI defaults, and regression tests to v0.4.3.
- Added 19 proposed synthetic iteration vectors and deterministic schema/contract tests. These are not live LLM behavior results.
- Clarified that exploration, discovery, and new questions have value beyond defect removal; curiosity and exploratory tone remain user-led rather than forced.
- Made gradual reciprocal understanding explicit without requiring the user and LLM to converge or become alike.
- No automatic project planner, persistent checkpoint database, autonomous learner, or provider runtime was added.

## 0.4.2 — User–LLM coexistence without cognitive imposition

- Added `COEXISTENCE_AND_NON_IMPOSITION.md` as a normative contract: CP adapts interaction to the user rather than shaping the user to fit CP.
- Clarified that CP has operational principles but does not impose a fixed assistant personality, ideal user profile, or preferred worldview.
- Preserved evidence-based disagreement and critical review while prohibiting coercive persuasion, identity judgment, and repeated pressure toward CP conformity.
- Required explicit confirmation for durable behavior-profile changes and explicit user requests for CP system modifications; retained platform/system, host, and non-delegable Safety Plane boundaries.
- Added transparent influence limits: CP does not claim zero cognitive influence and instead minimizes unrequested, opaque, persistent steering.
- Added 15 synthetic coexistence vectors and deterministic structure tests; these are not live LLM/user-impact results.
- Did not add a feature toggle, autonomous learning, persistence, or additional runtime. This release formalizes boundaries rather than adding more operating features.

## 0.4.1 — Outcome-aware learning and adaptive improvement

- Added `OUTCOME_LEARNING.md`: a deliverable-first, bounded review cycle for meaningful failures, partial outcomes, repeated corrections, regressions, and reusable successes.
- Distinguished `SUCCESS`, `PARTIAL`, `FAILURE`, `BLOCKED`, `ABORTED`, and `UNOBSERVED`; cancellation and missing observation are not misclassified as failure/success.
- Added causal-status discipline (`OBSERVED_FACTOR`, `SUPPORTED_INFERENCE`, `HYPOTHESIS`, `UNKNOWN`) and responsibility-locus labels to prevent invented root causes or default blame.
- Defined narrow adaptation scopes: response-local, task strategy, proposed behavior-profile change, or none. Durable behavior changes require evidence and explicit user confirmation.
- Added `LLM_README.md` as an explicit LLM entry point and reading/operation sequence.
- Added `schemas/outcome_review.schema.json`, two synthetic example records, 18 proposed behavior vectors, and deterministic contract tests.
- Updated the Common Core, failure recovery, core specification, configuration, adapter guidance, package maps, and evaluation protocol.
- No autonomous learner, durable profile store, cross-session memory, automatic replay, or live-model behavior guarantee was added.


## 0.3.7 — ChatGPT adaptive conversation flow

- Added `CONVERSATION_FLOW.md` as a ChatGPT-facing adapter protocol for natural conversation, exploration, hypothesis refinement, incremental problem decomposition, verification/test design, and execution.
- Made the phases explicitly soft, non-linear, skippable, and task-local; they are not task modes or claims about hidden model state.
- Added progressive formalization rules: answer first, structure only when useful, do not turn every casual tangent into a project, and limit unsolicited follow-up suggestions.
- Added anti-sycophancy guidance: examine user hypotheses without reflexive endorsement, present material alternatives, and identify discriminating observations when useful.
- Added 12 synthetic conversation-flow conformance vectors and 6 deterministic structural tests.
- Preserved v0.3.6 Gamma/Delta Index, Safety Plane topology, request-envelope schema 1.2, and existing authority/resource boundaries.
- No reasoning engine, deterministic conversation classifier, live LLM runner, or persistent conversation-state backend was added.


## 0.3.6 — Gamma + Delta Index control-plane skeleton

- Added Gamma Index as an independent metadata index with immutable resource identities, search, and explicit unresolved/held states.
- Added hold reasons, preserved source/evidence references, revisit triggers, and evidence-backed explicit hold closure.
- Added Delta Index as an observer-only snapshot/diff subsystem with baseline candidates, pending changes, conflict holds, and evidence-backed reconciliation.
- Ensured observed candidates do not mutate current state until explicitly accepted; rejected/superseded candidates retain the prior state.
- Added a protected global Safety Plane contract for Hard Safety Override, Risk Boundary, Recovery Path, Situational Verification, and Capability Declaration.
- Added topology checks forbidding safety components from being placed after Delta, disabled, weakened, or transitively dependent on Gamma, Delta, task profiles, or personalization overlays.
- Added Delta authority constraints: no authorization, activation, active-profile mutation, or safety disabling.
- Added synthetic examples and tests for hold preservation, competing candidates, stale state, evidence requirements, and forbidden safety placements.
- No remote connector, durable persistence, live event bus, runtime activation, or real safety enforcement is claimed.

## 0.3.5 — Gamma task-profile bridge skeleton

- Added a task-domain-only Gamma profile contract and import-packet schema.
- Added a synthetic `work.general` profile and import packet; no personal profile or memory data is included.
- Added canonical JSON SHA-256 digest, profile ID/version consistency, schema, and Top Mold compatibility checks.
- Added plan-only output: no live Gamma connector, source authenticator, permission enforcement, profile loader, atomic activation runtime, persistence, or Delta subscriber is included.
- Defined explicit user selection, one profile per task, session-only scope, staging/atomic-commit expectations, rollback semantics, and Delta lifecycle events.
- Prohibited profiles from changing authority, safety, host capability, permission, or approval boundaries.

## 0.3.4 — Generic core and epistemic-integrity hardening

- Removed the person-specific Personal Data Contract and personal-resource manifest from the package.
- Removed `personalization_depth` and `retention_preference`; renamed the generic agency dial to `human_control`.
- Reframed domain profiles as task-domain overlays and removed person-preference overrides.
- Added uncertainty, contradiction, and transformation-fidelity dials.
- Added explicit rules for unknown preservation, contradiction handling, bounded generalization, lossy transformations, provenance, and goal re-anchoring.
- Bumped the request-envelope schema to 1.2 with reference-only `transformations` and source-linked `conflicts` records; blocking unresolved conflicts cannot be marked READY.
- Added a package data-boundary declaration and tests for absence of profile/personal-resource artifacts.
- Added JSON nesting-depth and custom-schema byte limits, plus duplicate resource-ID validation and regression coverage.
- Added synthetic conformance cases derived from unknown/blank/contradictory/transformed-input failure modes.
- Retained the request-envelope schema shape (1.1) for compatibility.

## Source lineage

Derived from the v0.3.5 generic control contract + Gamma bridge. This remains an experimental declarative control contract and reference skeleton, not a production authorization or safety system.

## 0.3.8 — Gamma / Delta three-phase contract hardening

- Formalized Gamma phases as `DISCOVER -> RESOLVE -> HANDOFF`.
- Added bounded, deterministic, revision-guarded pagination, exact scope filtering, and held-entry exclusion by default.
- Added exact-ID resolution with optional expected identity checks; ambiguous candidates are never auto-selected.
- Added a reference-only Gamma handoff envelope. Retrieval and activation authorization are fixed to `false`; host verification remains mandatory.
- Formalized Delta phases as `OBSERVE/CAPTURE -> COMPARE -> RECONCILE` while preserving the legacy `observe()` convenience API.
- Added inspectable observation capture and same-process idempotency for caller-supplied observation IDs.
- Added stale-base protection over prior version, digest, and source reference: an outdated candidate cannot overwrite a newer reconciled snapshot; fresh observation/comparison is required.
- Delta comparison now treats a source-reference change as a change candidate, even when the content digest is unchanged.
- Gamma freezes caller-supplied list metadata on registration and tracks an index revision so paginated search cannot silently drift across index mutations.
- Tightened iterable, text-length, page-size, timestamp, and hold-input validation.
- Added typed Delta hold origin and a non-deadlocking re-observation path: stale historical candidates are retained, automatic competition holds can be released after rejection/supersession, and caller-created holds are not auto-lifted.
- Required the index revision on every Gamma continuation page; requests without it fail closed.
- Added handoff/observation schemas, examples, phase tests, and explicit implementation-boundary documentation.
- Preserved Request Envelope 1.2, Conversation Flow policy, the Safety Plane topology, and the non-authoritative roles of Gamma and Delta.
- No personal-data store, durable database, remote retrieval, access-control enforcement, automatic activation, or live-model/token-efficiency experiment was added.


## 0.3.9 — Human–LLM complementarity, reciprocal evidence, and capability utilization

- Added a human–LLM complementarity contract: no fixed conversational leader; distinguish functional contribution from decision authority; preserve human real-world accountability.
- Distinguished ordinary reciprocal dialogue from negotiation involving commitments, competing goals, resources, acceptance conditions, or explicit decision rights.
- Formalized answer-first interaction with optional, contextually useful follow-up questions; rejected mandatory end-of-response questions and profile-harvesting behavior.
- Added reciprocal non-blind trust: scrutinize human claims and LLM inferences without default cynicism; retain uncertainty, competing hypotheses, provenance, and counterevidence.
- Added claim-type-sensitive evidence handling. First-person subjective preferences remain primary evidence for current personal taste; self-assessments remain attributed as self-perception unless independently supported.
- Added multi-axis evidence dimensions: provenance, relevance, reliability, independence/correlation, temporal validity, scope, reproducibility, and counterevidence. Raw axis/source counts are not confidence scores.
- Added a synthetic evidence-bundle JSON Schema and example. This is a record shape, not a truth verifier, source authenticator, or calibrated probability engine.
- Added capability-utilization principles and a comparative evaluation protocol. No base-model intelligence, weights, hidden compute, or guaranteed improvement is claimed.
- Middle Mold and domain-specific modules remain out of scope; no persistent personal profile, personalization learner, live benchmark, negotiation engine, or truth-verification runtime was added.


## 0.4.0 — CLAY Personalization Common Core and specialist-module contracts

- Adopted the official name **CLAY Personalization (CP)**; retained legacy Top Mold filenames as compatibility aliases/lineage only.
- Added `COMMON_CORE.md` with hypothesis hold, hypothesis answer, constructive limitation acknowledgement, reciprocal scrutiny, agency, context discipline, and safety/authority invariants.
- Added typed constructive failure and recovery rules; distinguished blocked, unsupported, clarification-required, partial, and failed outcomes.
- Added `MODULE_INTERFACE.md`: specialist capability separated from personalization/behavior profile and task context; optional composite modules with internal fault-localization paths.
- Added machine-readable module manifest/result schemas, synthetic examples, conformance cases, and `tools/validate_modules.py`.
- Added optional multi-model orchestration contract; model count/majority is not treated as independent evidence or guaranteed quality improvement.
- Retained Request Envelope 1.2, Gamma/Delta phase contracts, evidence evaluation, conversation flow, and non-delegable Safety Plane.
- No live loader, module executor, model API orchestration, persistent personalization learner, host permission enforcement, runtime safety controller, or calibrated truth engine was added.
- Hardened the local module validator against malformed semantic types; added regression tests for malformed result status and malformed capability entries so invalid input is reported without validator traceback.
