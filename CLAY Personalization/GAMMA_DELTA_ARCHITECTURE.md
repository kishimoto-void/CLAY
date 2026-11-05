# Gamma Index + Delta Index — v0.2.0 Three-Phase Reference Contract

## 1. Design intent

Gamma and Delta are **independent control-plane subsystems** with module interfaces. They are not ordinary task processors and are not embedded inside Top Mold's reasoning core.

- **Gamma Index** indexes and resolves candidate resource/profile metadata, then hands off references to the host. It does not fetch resource payloads. It preserves unresolved candidates and explicit hold records.
- **Delta Index** observes version/state snapshots, records differences, and keeps competing or unverified changes pending. It does not apply changes.
- **Top Mold** validates task requests, composes a candidate configuration, and asks the host to authorize/activate it atomically.
- **Safety Plane** remains global, cross-cutting, and non-delegable. It is not a step placed after Delta.

The current package contains a small in-memory reference skeleton for Gamma and Delta. It has no remote connector, durable database, scheduler, or automatic activation service.

## 2. Control flow and authority

```text
                         GLOBAL / CROSS-CUTTING SAFETY PLANE
     +------------------------------------------------------------------+
     | Hard Safety Override | Risk Boundary | Situation Verification   |
     | Capability Declaration | Recovery Path                            |
     | Always available; cannot be disabled by Gamma/Profile/Delta      |
     +------------------------------------------------------------------+
                 | policy constraints / veto / safe alternatives
                 v
Gamma Index ---> Top Mold Core ---> Task Processor / Host Execution
 (discover,     (validate, compose,       (only after all required
  resolve,       policy-gate, stage,        host approvals and safety gates)
  handoff)       commit request)                    |
       ^                                                |
       |                                                v
       +--------- profile/resource lifecycle ------- Delta Index
                                                    (observe / diff /
                                                     retain / report)
                                                            |
                                                            v
                                                     Advisory Event Bus
                                                     (no authority)
```

The diagram shows two different things: task-data flow and authority. Delta may observe a post-activation state transition, but it is **not a safety authority layer** and its output does not authorize, activate, or invalidate an action by itself. Safety checks receive required observations from trusted host/sensor/policy channels independently of Delta.

## 3. Gamma Index responsibilities

### Does
- Keep metadata and references for known resources.
- Search by identifier, tag, scope, or descriptive text; discovery is bounded, paginated, stable within an index revision, continuation requires that revision, and results are not semantically ranked.
- Preserve candidate claims and provenance references.
- Mark unresolved records `HELD` with a reason, open questions, preserved references, and a revisit trigger.
- Close a hold only through an explicit decision with a rationale and evidence reference.
- Keep immutable entry IDs and reject identity/version digest collisions.

### Does not
- Treat an entry as true because it is indexed.
- Authenticate a source based on the source's own declaration.
- Decide that a candidate is suitable for a task solely by search score.
- Execute or activate a task profile.
- Change system/host permissions, Top Mold authority, or hard safety requirements.
- Delete held data automatically or silently convert `HELD` into `AVAILABLE`.

## 4. Gamma lifecycle and hold semantics

Entry states:

`CANDIDATE -> AVAILABLE | HELD | REJECTED | SUPERSEDED`

`HELD -> AVAILABLE | RESOLVED | REJECTED | SUPERSEDED`

The transition out of `HELD` requires an explicit resolution, non-empty rationale, and evidence reference. The hold record remains in the index as closed history. A new observation or a second candidate does not resolve an older hold.

Supported hold reasons include:
- `INSUFFICIENT_EVIDENCE`
- `CONFLICTING_CANDIDATES`
- `SOURCE_UNVERIFIED`
- `MISSING_CONTEXT`
- `MISSING_CAPABILITY`
- `APPROVAL_PENDING`
- `POLICY_REVIEW`
- `VERSION_COLLISION`

A hold is not a trash can and not a claim that the held material is false. It means: retain the candidate, preserve uncertainty, identify what is missing, and state what would cause reassessment.

## 5. Delta Index responsibilities

### Does
- Receive snapshots from a host/Top Mold event boundary.
- Compare target ID, version, canonical content digest, and source reference against the last reconciled snapshot.
- Record baseline candidates, unchanged observations, and change candidates.
- Preserve both prior and candidate states during review.
- Place competing candidates or unresolved changes on hold, with typed hold origin distinguishing automatic competition, caller hold, and stale base.
- Reconcile a candidate only with an explicit decision, rationale, and evidence reference.
- Retain metadata-only event records through reconciliation; the reference implementation does not provide an immutable transition-by-transition audit log.

### Does not
- Fetch a resource from Gamma.
- Decide which of two conflicting versions is correct without adjudication.
- Mutate Top Mold's active configuration.
- Activate, deactivate, or rollback a profile.
- Grant permissions, declare capabilities, or authorize actions.
- Run, disable, route around, or replace any Safety Plane component.

## 6. Delta state model

Event statuses:
- `PENDING_REVIEW`: change/baseline candidate observed; no state mutation.
- `HELD`: ambiguity, conflict, or missing evidence prevents resolution.
- `CONFIRMED`: explicit reconciliation has accepted the candidate, or an unchanged current snapshot was observed.
- `REJECTED`: explicit review rejected the candidate.
- `SUPERSEDED`: explicit review marked the candidate obsolete.

Only an explicit `ACCEPT_CANDIDATE` reconciliation updates Delta's current reference snapshot. `REJECT_CANDIDATE` and `SUPERSEDE_CANDIDATE` leave the previous current snapshot unchanged. Reconciliation requires an evidence reference and rationale, and acceptance requires the candidate's recorded prior version, digest, and source reference to match the latest current snapshot. Hold origin is typed as system competition, user hold, or stale-base hold; stale-base records remain inspectable but do not block a fresh comparison, while user holds are never auto-released. Pending/held events are retained; this skeleton has no TTL cleanup.

## 7. Shared hold principle

`UNKNOWN != FALSE` and `UNVERIFIED != REJECTED`.

- Preserve raw observations separately from interpretations.
- Keep competing claims/versions addressable.
- Record source/evidence references and why a question remains open.
- Do not automatically generalize from an unresolved record.
- Do not treat repeated copies from one origin as independent corroboration.
- Revisit only when an identified trigger or new evidence arrives.

## 8. Interface boundary with Top Mold

1. User or task explicitly requests a resource/profile.
2. Gamma resolves candidates and returns references; ambiguous selection remains unresolved.
3. Host retrieves the selected source and separately verifies source identity, permissions, and required capabilities.
4. Top Mold validates schema, scope, compatibility, provenance, and constraints; it creates a detached candidate overlay.
5. Safety Plane independently checks the proposed operation and current situation.
6. Host performs atomic activation only when every required gate authorizes it.
7. Host emits a receipt/snapshot. Delta records the confirmed activation or a pending observation.
8. Updates enter a new validation/staging cycle. They never hot-swap silently.

A valid Gamma entry is not an activation receipt. A Delta confirmation is an observation/reconciliation result, not an activation permission.

## 9. Implementation status

Implemented in this skeleton:
- in-memory Gamma metadata index, search, immutable entry registration, explicit hold/resolve lifecycle;
- in-memory Delta snapshot observer, diff candidate, pending/held queue, explicit reconciliation;
- topology guard for protected Safety Plane placement and Delta's observer-only authority;
- synthetic examples and deterministic unit tests.

Not implemented:
- Gamma/Delta network connectors or storage backends;
- source authentication/signature trust root;
- live event bus or subscriptions;
- concurrent durable transactions and crash recovery;
- LLM/robot/device execution;
- risk scoring, domain-specific rescue/medical policies, or actual Safety Override enforcement;
- automatic Recovery Path execution.

The code is a reference skeleton and contract test target, not a production safety system.

## 10. v0.3.8 three-phase interfaces

The normative phase definitions are in `INDEX_THREE_PHASE_CONTRACT.md`.

- Gamma: `DISCOVER -> RESOLVE -> HANDOFF`. Discovery is bounded and deterministic; resolution requires an exact entry ID; handoff is a reference-only envelope and never grants retrieval or activation.
- Delta: `OBSERVE/CAPTURE -> COMPARE -> RECONCILE`. Capture is separately inspectable, comparison creates a candidate event without mutating current state, and reconciliation requires evidence/rationale plus a matching prior version/digest/source reference before acceptance.
- Acceptance of a stale Delta candidate is rejected. Competing candidates remain retained and require a fresh observation and comparison against the new reconciled base.

These are protocol boundaries around the existing in-memory indexes, not additional execution engines or storage systems.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.
