# Gamma Index ↔ Top Mold Bridge — v0.3.8 inherited bridge contract

## 1. Purpose

This bridge lets Gamma Index select and supply a **task-domain profile** (for example, `work.general`) so Top Mold can validate it and construct a task-scoped overlay. Delta observes the resulting version/state transitions and update notifications.

The bridge does **not** turn Gamma into an authority source. It does not import a person's identity, biography, private preferences, or general memory into Top Mold. It does not automatically combine profiles.

## 2. Responsibility boundaries

| Component | Responsibility | Explicit non-responsibility |
|---|---|---|
| Gamma Index | Search/select a requested profile and return a versioned resource | Does not activate it or override Top Mold policy |
| Gamma adapter / host | Retrieve bytes, authenticate the source, enforce access/approval, provide an evidence reference | Must not represent an unverified source as verified |
| Top Mold bridge | Validate schema, identity/version match, digest and compatibility; produce a composition plan | Does not provide network access, authenticate a source, grant permissions, or execute activation |
| Top Mold core | Compose the active task overlay and preserve global authority/safety rules | Does not treat profile text as higher authority than the current task or system rules |
| Delta | Observe active profile ID/version/digest and emit update/state events | Does not fetch profiles, silently hot-swap them, or grant activation permission |
| Safety Override / host policy | Enforce non-overridable safety and host permissions | Cannot be weakened by a profile |

## 3. Profile kind and data boundary

v0.3.5 supports exactly one profile kind: `task_domain`.

A profile may describe:
- preferred task mode;
- behavior-dial preferences;
- output-format/section preferences;
- workflow stage descriptors;
- verification preferences;
- additive task constraints;
- required capability labels (declarations only).

A profile MUST NOT contain or change:
- personal identity, biography, personal memory, or private preference history;
- authority precedence, system/platform rules, or safety overrides;
- host permissions, tool availability, credentials, or action approvals;
- Top Mold's schema/validation rules;
- arbitrary executable code, prompt templates, or commands to the host.

Free-text fields inside a profile remain untrusted data. The adapter may translate structured descriptors into task guidance, but embedded instructions do not acquire authority merely because they arrived through Gamma.

## 4. Request and import lifecycle

1. **Select** — A user explicitly requests a profile (e.g. “仕事用プロファイルに切り替えて”). A general mention of a work topic is not profile-selection intent. The requested task mode must also be listed in the profile’s allowed `task_modes`.
2. **Resolve** — Gamma returns the exact `profile_id`, version, and resource reference. Ambiguous matches remain unresolved; Top Mold must not guess between profiles.
3. **Retrieve** — The host adapter retrieves only the selected profile. `requested`, `approved`, `available`, and `received` are separate states.
4. **Validate** — Check packet schema, profile schema, ID/version match, requested-task-mode scope, canonical digest, Top Mold compatibility range, and session scope. Declare and verify required capabilities separately.
5. **Authenticate / authorize** — The host adapter, outside this validator, confirms source authenticity, real resource access, and the required permission/approval.
6. **Stage** — Build a candidate overlay without mutating the current active configuration.
7. **Commit** — The host atomically activates the candidate only after all required gates pass. If any step fails, retain the previous active profile unchanged.
8. **Observe** — After host-confirmed activation, send the profile ID/version/digest and activation timestamp to Delta.
9. **Update / unload** — Stage and revalidate updates; do not silently hot-swap. Deactivation returns to the base configuration and records the state transition.

The included `interfaces/gamma_provider.py` defines typed provider, source-verifier, and runtime-host interfaces without implementing them. The included `tools/validate_gamma_profile.py` performs local structural/digest/compatibility checks and generates a detached `candidate_overlay_preview` for inspection. This is composition preview only: it does not mutate canonical config, stage into a runtime, load Gamma itself, or activate the profile. Its `execution_status` is always `NOT_INVOKED` and its `activation_status` is always `NOT_ACTIVATED`.

## 5. Overlay composition and precedence

For a selected, validated task profile, the intended preference composition is:

`Global Top Mold defaults → built-in task-domain overlay → one Gamma task profile → current-task explicit instructions`

This is a preference/configuration composition only. The helper now produces a deterministic, detached preview using this order; it does not perform a runtime switch. The explicitly requested current task mode remains authoritative even when a profile contains a different in-scope mode label. The merge does not supersede the normative authority order in `SPEC.md`:

- platform/system safety and actual host constraints remain highest;
- current explicit task instructions remain higher authority than a delegated profile;
- explicit session controls apply only where not contradicted by the current task;
- Gamma profile data is task-scoped delegated data, not an authority root;
- hypotheses and inferred metadata never create authority.

A Gamma profile may add constraints, not remove higher-priority constraints. Its dial values are preferences only and cannot weaken normative verification, epistemic-integrity, safety, or permission requirements. A required capability label is not proof that the capability exists.

## 6. Session isolation and atomicity

- One Gamma task profile may be active for a task at a time in this skeleton.
- Activation scope is `current_task_session`; no durable profile store is introduced.
- A profile selection does not mutate the canonical Top Mold configuration.
- Candidate profile and active profile are distinct states.
- Activation is transactional: validate → stage → host-confirmed commit.
- On error, retain the last known-good active profile; do not partially apply fields.
- Unloading/deactivation does not claim to delete Gamma's source resource.

## 7. Delta event contract

Delta receives state facts from the host/Top Mold bridge; it does not fetch or activate resources.

| Event | Meaning |
|---|---|
| `PROFILE_CANDIDATE_RECEIVED` | A profile packet entered validation |
| `PROFILE_VALIDATED` | Local contract/digest/compatibility checks passed |
| `PROFILE_REJECTED` | A contract, scope, integrity, compatibility, or host gate failed |
| `PROFILE_ACTIVATED` | Host confirmed atomic activation; include profile ID/version/digest |
| `PROFILE_ACTIVATION_FAILED` | Host attempted the atomic commit but confirmed failure; previous overlay remains active |
| `PROFILE_UPDATE_AVAILABLE` | A newer source version or changed candidate digest was observed |
| `PROFILE_DEACTIVATED` | Host confirmed return to base configuration |

An update notification starts a new validation/staging cycle. It does not replace the active profile. A changed digest under the same profile ID and version is a version-collision/mutability fault and must be rejected. Invalid or unavailable updates leave the prior active profile intact unless a separate higher-priority safety/revocation policy requires deactivation.

## 8. Failure states

| Condition | Required result |
|---|---|
| Profile not found / Gamma unavailable | `UNAVAILABLE`; retain current profile |
| Ambiguous profile selection | `CLARIFICATION_REQUIRED`; do not guess |
| Schema / ID / version / digest mismatch | `REJECTED`; do not stage |
| Top Mold version incompatible | `INCOMPATIBLE`; do not stage |
| Source authentication not verified | `HOST_CHECK_REQUIRED` or `REJECTED` by host policy; no activation |
| Permission pending / denied | `PENDING` / `DENIED`; no activation |
| Required capability absent | `BLOCKED`; report the missing capability |
| Atomic commit failure | `ACTIVATION_FAILED`; retain prior active profile |
| Delta unavailable | Activation must not be falsely reported as Delta-observed; host records pending/unreported event |

## 9. Security and epistemic caveats

- SHA-256 here detects content mismatch against the packet's supplied digest; by itself it does not authenticate Gamma or prove authorship.
- `host_checks` fields in a JSON packet are declarations. The local validator cannot prove that a trusted host actually performed them. Packet-embedded host fields are never used to satisfy activation gates. A trusted in-process adapter may pass independently obtained decisions out-of-band to the planning function, together with an evidence reference; this is a caller trust boundary, not cryptographic authentication by the helper. Required capabilities must likewise be checked against the host registry; their labels in the profile do not create capabilities.
- A valid schema does not establish that profile content is truthful, useful, safe, or appropriate.
- The profile schema rejects unknown fields, including accidental authority/permission extension fields, but cannot semantically detect every secret or personal datum embedded in free text. The trusted adapter must apply data minimization and review.
- No connector, network fetcher, signature verifier, permission enforcement, activation runtime, persistence, or Delta event subscriber is included. The helper's trusted-host-check argument is an interface seam for a future in-process adapter; it must not be populated from untrusted packet fields.

## 10. Current skeleton status

Implemented:
- task-profile and import-packet schemas;
- typed Gamma provider / trust verifier / runtime host protocol interfaces;
- synthetic `work.general` profile and import packet;
- canonical-digest / compatibility / schema validator;
- deterministic candidate-overlay preview with explicit layer precedence and monotonic union of verification requirements / additive constraints;
- plan-only output and deterministic tests for precedence, immutability, and rejected authority fields.

Not implemented:
- live Gamma Index connection or search;
- source signature/authentication verification;
- host approval/permission enforcement;
- automatic profile loading or activation;
- atomic runtime configuration swap;
- Delta runtime subscription or persistence.


## v0.3.8 inherited module boundary

The independent Gamma and Delta reference modules are documented in `GAMMA_DELTA_ARCHITECTURE.md`. Gamma hold records preserve unresolved candidate data. Delta records state differences and leaves changes pending until explicit evidence-backed reconciliation. The protected Safety Plane is defined in `SAFETY_PLANE_BOUNDARY.md`; Risk Boundary and Recovery Path are cross-cutting peers, never downstream components of Delta.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.

> **Carried-forward contract:** This document preserves an earlier contract. CP v0.4.3 adds scope-complete iteration, project continuity, reproducible-success review, and testable failure prevention; see `LLM_README.md`, `OUTCOME_LEARNING.md`, and `COMPLETION_AND_CONTINUING_EXPLORATION.md`. Prior contracts remain in force.
