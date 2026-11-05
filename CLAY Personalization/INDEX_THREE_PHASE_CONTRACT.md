# Gamma / Delta Three-Phase Contract — Top Mold v0.3.8

## 1. Purpose and boundary

This document makes the Gamma and Delta lifecycles explicit and independently testable. It defines protocol phases, not a mandatory conversational pipeline and not an autonomous runtime.

- **Gamma** discovers metadata candidates, resolves one exact candidate, and hands a reference to the host/Top Mold for separate checks.
- **Delta** captures an observation, compares it with the last reconciled snapshot, and records an explicit reconciliation.
- Neither subsystem stores user-profile payloads, fetches remote resource contents, provides a durable database, or authorizes activation.
- The phases may be invoked separately and retried where their contracts permit. A phase result is not proof that a later phase happened.

## 2. Gamma: DISCOVER -> RESOLVE -> HANDOFF

### G1 — DISCOVER

Input: a bounded query, optional exact scope filter, and optional tags.

Output: a deterministic, paginated list of metadata-only candidates with their current index status and open holds.

The reference implementation uses case-insensitive substring matching over IDs, resource kind, scope, claims, and tags; tags and scope filters are exact (case-insensitive for tags, exact for scope). It does not implement semantic/vector search or relevance ranking. Intent interpretation and semantic query expansion remain the responsibility of the executing LLM or host adapter.

Normative rules:

1. Discovery is candidate generation, not semantic truth determination.
2. Results are not relevance-ranked by the reference implementation. Ordering is stable and deterministic only.
3. `HELD` entries are excluded by default. A caller must explicitly request them for review.
4. Pagination must state whether additional results exist; a truncated page must not be presented as exhaustive.
5. Every continuation page (`offset > 0`) must provide the previous page's index revision. If omitted, the request is rejected; if the index changed, pagination fails and must restart rather than silently skipping or duplicating candidates.
6. `scope` is an index filter/descriptor, not an access-control grant or permission check.
7. Rejected and superseded entries are not offered as live candidates; their historical records remain in the index snapshot.
8. Search does not fetch resource payloads, authenticate sources, or grant access.

### G2 — RESOLVE

Input: one exact `entry_id`, optionally constrained by expected `resource_id`, version, digest, and scope.

Output: one exact `GammaSearchResult` or a typed failure.

Normative rules:

1. A caller must identify an exact entry. Gamma must not silently choose among multiple candidates using an unreviewed score or lexical order.
2. Expected identity fields, when supplied, must match exactly.
3. An entry with an open hold or `HELD` status cannot be resolved for handoff.
4. `REJECTED` and `SUPERSEDED` entries cannot be resolved for handoff.
5. Resolution does not authenticate the source, validate the content, or authorize use.

### G3 — HANDOFF

Input: a candidate that passed G2.

Output: a reference-only `GammaHandoff` containing immutable identity metadata and required host checks.

Normative rules:

1. Handoff contains references and metadata only; it does not include source payload bytes.
2. `retrieval_authorized` and `activation_authorized` are always `false`.
3. The host must independently check source identity/authenticity, permissions, capabilities, compatibility, safety policy, and any required approval before retrieval or activation.
4. A catalog label of `source_status=VERIFIED` is a recorded declaration, not cryptographic proof and not a substitute for host verification.
5. A `FAILED` source status blocks handoff. `UNVERIFIED` may be handed off as an explicitly unverified reference, subject to host checks.

## 3. Delta: OBSERVE -> COMPARE -> RECONCILE

### D1 — OBSERVE / CAPTURE

API: `DeltaObserver.capture(snapshot, observation_id=None)`.

Output: a retained, validated in-memory `DeltaObservation`.

Normative rules:

1. Capture validates structural fields and records what was observed, including source reference and source observation time. The local `captured_at` receipt time is stored separately.
2. Capture does not classify the observation, update current state, or create an accepted change.
3. A caller-supplied observation ID is idempotent for the same target/version/digest/source tuple. Reuse with different content is rejected as a collision.
4. A generated observation ID is process-local; it is not a durable or cross-process identifier.

### D2 — COMPARE

API: `DeltaObserver.compare(observation_id)`.

Output: one `DeltaEvent` classified against the last reconciled snapshot for that target.

Normative rules:

1. No current snapshot yields `BASELINE_CANDIDATE`.
2. Matching version, digest, and source reference yields `NO_CHANGE`.
3. A differing version, digest, or source reference yields `CHANGE_CANDIDATE`.
4. Another unresolved candidate for the same target causes a new changed/baseline candidate to be held rather than guessed. `hold_source` distinguishes `SYSTEM_COMPETITION`, `USER`, and `STALE_BASE`; free-form `hold_reason` is never used as the authority signal.
5. Compare records a candidate event but does not mutate the reconciled current snapshot.
6. Repeating compare for an already-compared observation returns the same event.

### D3 — RECONCILE

API: `DeltaObserver.reconcile(event_id, decision, resolution, evidence_ref)`.

Allowed decisions: `ACCEPT_CANDIDATE`, `REJECT_CANDIDATE`, `SUPERSEDE_CANDIDATE`.

Normative rules:

1. Reconciliation requires a non-empty rationale and evidence reference. The reference implementation checks non-empty string presence and length only; it does not authenticate or verify the evidence.
2. Only `ACCEPT_CANDIDATE` updates Delta's recorded current snapshot.
3. Before accepting, the candidate's recorded prior version/digest/source reference must still match the current reconciled base. A stale candidate is rejected with `STALE_CANDIDATE_REQUIRES_REOBSERVATION` and remains unresolved.
4. Competing candidates are retained and marked for re-observation/re-comparison after one candidate is accepted. Re-observation must use a new observation ID; replaying the prior ID returns the prior comparison. Stale-base holds do not deadlock a fresh comparison against the new current base. If one candidate is rejected or superseded, candidates held only by the automatic competition gate return to review; caller-created holds remain held.
5. Rejecting or superseding a candidate leaves the current snapshot unchanged.
6. Delta's `current` means **last reconciled reference snapshot held by Delta**. It does not mean a live profile was loaded, activated, or changed.
7. Delta cannot grant permissions, authorize execution, activate a profile, mutate a live resource, or disable the Safety Plane.

## 4. Cross-index separation

Gamma and Delta are complementary but not a single linear chain:

- Gamma is a metadata discovery/selection/handoff index.
- Delta is an observation/diff/reconciliation ledger for versioned state snapshots.
- A host or Top Mold adapter may emit a Delta observation after an independently authorized operation; Delta is not the authority for that operation.
- Delta must not be treated as Gamma's payload store. Gamma's `source_ref` and Delta's event `source_ref` are references, not embedded resource content.
- Cross-domain reads, data-store access, identity management, personal-data persistence, and module composition are outside this release.

## 5. Authority and safety invariant

The Safety Plane remains global, cross-cutting, and non-delegable. Gamma cannot weaken it. Delta cannot authorize, activate, or disable it. The topology validator checks declared architecture; it is not a runtime security boundary. Actual permission checks and execution gates must be enforced by the host outside these in-memory reference indexes.

## 6. Reference implementation status

Implemented in v0.3.8:

- Gamma `discover`, `resolve`, and `handoff` APIs, alongside legacy `search`/`get` compatibility.
- Bounded deterministic discovery with exact scope filtering, stable pagination metadata, mandatory revision-guarded continuation, and held-entry exclusion by default.
- Reference-only handoff with explicit `retrieval_authorized=false` and `activation_authorized=false`.
- Delta `capture`, `compare`, and `reconcile` APIs, alongside the legacy `observe` convenience method.
- Idempotent observation capture for caller-supplied observation IDs within one process.
- Stale-base protection over prior version/digest/source reference before accepting a candidate, with explicit hold-origin metadata to distinguish user, system-competition, and stale-base holds.
- Deterministic competing-candidate recovery: rejection/supersession reopens only automatic competition holds; acceptance stale-holds other candidates; fresh observations against the new base can proceed without clearing historical stale records.
- Additional schemas, examples, and deterministic tests for the phase contracts.

Not implemented:

- Persistent storage, cross-process idempotency, remote retrieval, content authentication, access-control enforcement, external connectors, automatic module loading, runtime activation, transactional crash recovery, or live safety enforcement.
- Personal profile storage or user-specific memory.
- Live LLM behavior experiments or proof of token/latency reduction.

These modules remain reference implementations for the contract, not production services.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.

> **Carried-forward contract:** This document preserves an earlier contract. CP v0.4.3 adds scope-complete iteration, project continuity, reproducible-success review, and testable failure prevention; see `LLM_README.md`, `OUTCOME_LEARNING.md`, and `COMPLETION_AND_CONTINUING_EXPLORATION.md`. Prior contracts remain in force.
