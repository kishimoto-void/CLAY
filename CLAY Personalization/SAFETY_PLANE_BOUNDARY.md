# Safety Plane Boundary — non-delegable placement rules

## 1. Core rule

**Safety systems MUST NOT be placed downstream of Delta Index.** They are global, cross-cutting authorities that constrain all stages, not optional processors in a sequential route.

This specifically protects:
- `hard_safety_override`
- `risk_boundary_engine`
- `recovery_path_engine`
- `situational_verification`
- `capability_declaration`

All are required, enabled, and marked `GLOBAL_NON_DELEGABLE` in the topology contract.

## 2. Delta is observation, not authority

Delta has exactly an observer/reconciliation role. It may report:
- a change was detected;
- a candidate version differs from the active version;
- a conflict is unresolved;
- evidence is missing;
- a previously observed state is no longer current.

Delta MUST NOT:
- authorize an operation;
- activate/deactivate a profile or component;
- mutate the active profile;
- enable/disable/relax a safety component;
- decide that a risk is acceptable;
- act as the sole source of observations for a safety-critical decision.

Delta events are advisory inputs. A host may notify Top Mold that revalidation is needed, but Safety Plane decisions remain independent and are made under their own trusted inputs and policies.

## 3. Safety plane independence

Risk Boundary and Situational Verification consume trusted context from the host's authorized observation/policy channels. They must not require Gamma or Delta to function. Capability declarations must originate from an actual host/device capability registry, not a task profile's assertion.

Recovery Path is a proposal and routing function subject to Risk Boundary, capability, permission, and human-oversight checks. It does not independently execute hazardous recovery actions.

## 4. Non-overridable constraints

Gamma entries, task profiles, Middle/Bottom modules, user-facing dials, and Delta events cannot:
- remove or weaken safety constraints;
- mark a prohibited action as allowed;
- convert `UNKNOWN` into `CAN` without evidence from an authorized capability source;
- infer consent or authority from a profile;
- cause a hard safety override to be disabled;
- defer emergency escalation merely because a profile requests a different workflow.

## 5. Failure semantics

- Missing/invalid Safety Plane module: `BLOCKED` for activation/execution paths that require it.
- Safety module disabled or placed in a sequential pipeline: topology validation fails.
- Safety dependency chain reaches Gamma, Delta, a task profile, or personalization overlay: topology validation fails.
- Delta attempts authority escalation: topology validation fails.
- Safety assessment is `UNKNOWN` or required evidence is absent: no claim of `ALLOW`; hold, request verification, or escalate according to the validated domain policy.
- Recovery option is unavailable or unsafe: report that limitation and seek an authorized alternative; do not improvise beyond declared capability.

## 6. Important implementation caveat

The supplied code validates topology declarations and exposes typed interfaces. It does **not** implement a live hard-stop circuit, risk model, sensor-validation system, rescue procedure, or host permission sandbox. A production physical system needs independently validated hardware/software interlocks, tested domain policies, failure-mode analysis, redundant observations with common-mode analysis, and qualified human oversight.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.
