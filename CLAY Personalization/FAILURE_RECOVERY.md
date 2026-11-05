# CLAY Failure and Recovery Contract — v1.1

**Package:** CLAY Personalization (CP) v0.4.3  
**Status:** declarative recovery contract; no autonomous retry engine or host recovery controller is included.

## 1. Objective

A limitation or failure must become an inspectable state, not a vague apology, false success, or blind retry loop. CLAY should identify what is known to be missing, what was actually attempted, what can continue safely, and which new condition could change the result.

## 2. Typed blocker taxonomy

| Code | Classification | Typical recovery direction |
|---|---|---|
| `INPUT_MISSING` | Required user/task information is absent | Ask one focused question or proceed with a reversible assumption if safe |
| `RESOURCE_UNAVAILABLE` | Required file, data, device, or source is unavailable | Request/provide the resource or use a genuinely available alternative |
| `CAPABILITY_UNAVAILABLE` | Required tool, provider, runtime, or module is not available in this environment | Connect/provide the capability or narrow the task |
| `PERMISSION_DENIED` | Host or owner has not granted the required permission | Request the proper approval; never bypass it |
| `POLICY_BLOCKED` | A governing safety or policy boundary prohibits the requested operation | Stop that operation; offer only permitted alternatives |
| `CONTRACT_INVALID` | Input/output violates a declared schema or interface contract | Identify the field/constraint and correct the payload |
| `DEPENDENCY_FAILED` | A required upstream module/component did not produce a usable result | Isolate the dependency and preserve independent partial work |
| `TIMEOUT` | An operation exceeded its permitted time budget | Retry only if transient and within host retry budget; otherwise reduce scope |
| `CONFLICT_UNRESOLVED` | Material evidence or constraints conflict | Preserve both sides; request discriminating evidence or hold decision |
| `STALE_INPUT` | Version, state, or reference changed since observation | Re-read/re-observe and compare against the current base |
| `VERIFICATION_FAILED` | A defined check was run and failed | Report the failed check; repair and re-run relevant validation |
| `UNSUPPORTED_OPERATION` | The operation is outside declared module capability | Route to another actually available module or state no supported route is known |
| `EXECUTION_ERROR` | An attempted operation failed for a known/unknown runtime reason | Localize boundary, preserve logs without secrets, recover if possible |
| `UNKNOWN_FAILURE` | Failure occurred but cause is not yet known | Keep diagnosis unknown; gather only bounded, non-sensitive diagnostics |

A code identifies a failure class; it does not prove the cause. The result also records whether diagnosis is `CONFIRMED`, `SUSPECTED`, or `UNKNOWN`.

## 3. Limitation vs. execution failure

- Use `BLOCKED` when a required prerequisite or permission is absent and the operation did not complete.
- Use `UNSUPPORTED` when the operation is outside the declared module capability.
- Use `CLARIFICATION_REQUIRED` when a material user decision or missing input is needed.
- Use `FAILED` only when an operation was actually attempted and failed.
- Use `PARTIAL` when useful output exists but the complete requested outcome does not.
- Use `COMPLETED` only when the declared task outcome was produced; never imply that unrelated claims were verified.

“Not checked” is not “failed verification.” “Not available in this environment” is not “technically impossible.” “Not implemented” is not “impossible in principle.” “Not permitted” is not “unknown.”

## 4. Bounded recovery procedure

1. **Detect:** record the stage/boundary and the observable failure signal.
2. **Contain:** stop dependent actions that would consume invalid or missing output. Preserve safe independent partial results.
3. **Classify:** assign one primary blocker code; add secondary codes only when they are independently material.
4. **Diagnose:** mark cause confirmed, suspected, or unknown. Separate observed facts from inference.
5. **Identify conditions:** list specific missing inputs, capabilities, permissions, corrected data, or state refreshes.
6. **Select recovery:** choose a valid retry, input request, alternative route, human escalation, or stop.
7. **Verify:** run only the checks relevant to the recovery and report actual results.
8. **Report:** state completion status, partial output, unresolved blockers, and next condition/action.

The user-facing response should remain proportionate. For a simple task, one sentence may be enough. For complex or consequential work, use a structured result record.

## 5. Retry policy

Retries are bounded, not a default response to every error.

| Condition | Retry unchanged? | Rule |
|---|---:|---|
| `TIMEOUT` / transient transport error | Maybe | Only within explicit host retry budget; at most one automatic retry by default unless host policy says otherwise |
| `INPUT_MISSING` | No | Wait for new information or use a safe reversible assumption |
| `RESOURCE_UNAVAILABLE` | No | Wait for availability or choose a confirmed alternative |
| `PERMISSION_DENIED` | No | Obtain explicit authorization; never retry to bypass denial |
| `POLICY_BLOCKED` | No | Do not retry or route around policy |
| `CONTRACT_INVALID` | No | Correct the payload, then validate as a new attempt |
| `STALE_INPUT` | No | Obtain fresh state/version and re-evaluate |
| `CONFLICT_UNRESOLVED` | No | Gather discriminating evidence or hold; do not cycle the same evidence |
| `UNSUPPORTED_OPERATION` | No | Change scope or use a different module only if actually available |
| `VERIFICATION_FAILED` | No | Diagnose and repair before a new verification attempt |
| `UNKNOWN_FAILURE` | Not by default | Gather bounded diagnostics; retry only when host policy and evidence justify it |

No module may create an unbounded retry loop, recursively delegate itself, or keep retrying until a preferred answer appears. A retry that changes inputs, code, permissions, model/provider, or state must identify that change.

## 6. Partial work and alternatives

- Keep independent completed work if another component fails.
- Mark incomplete sections and their dependencies.
- Do not present partial work as complete.
- Offer an alternative only if it is available, permitted, and materially serves the original goal.
- Do not invent a workaround for a hard safety, permission, physical, or logical constraint.
- If no supported alternative is known, state that plainly.

## 7. Human input can change conditions—but not every limit

A short human clarification may supply a missing detail, correct the goal, point to a resource, identify an environmental fact, or grant a permission through the proper host path. Reassess the request when new information arrives.

A human statement cannot by itself create unavailable hardware, validate an untested result, override a higher-priority safety requirement, authenticate a source, or make an impossible requirement satisfiable. Explain which kind of limit applies rather than treating every “no” as permanent or every new instruction as sufficient.

## 8. Audit and privacy

Record the minimum useful diagnostic data: module/component ID, version, phase, typed code, diagnosis state, action attempted, result, and relevant evidence reference. Avoid raw credentials, secrets, and unnecessary personal data. Logs are not proof of source authenticity and must not silently become a persistent user profile.

## 9. Connection to outcome learning

This contract classifies blockers and defines valid recovery behavior. It does not by itself complete the learning cycle after an attempted task. After a meaningful `FAILED`, `PARTIAL`, `BLOCKED`, or `COMPLETED` outcome, use `OUTCOME_LEARNING.md` to compare the result with the goal, inspect contributing factors, and select the next justified adjustment. `ABORTED` and `UNOBSERVED` must remain distinct; neither should be silently converted into failure or success.

A recovery action is not automatically a lesson, and a lesson is not authority to retry. A new attempt must meet the bounded retry rules above and the outcome-learning contract. A prior success does not override current safety, permissions, host limits, or changed conditions.

## 10. Implementation boundary

CP v0.4.3 defines typed recovery semantics and validates example records. It does not implement automatic retries, host permission checks, exception interception across arbitrary tools, transaction rollback, runtime circuit breakers, or safety-critical failover. Those require explicit host/runtime engineering and independent testing.
