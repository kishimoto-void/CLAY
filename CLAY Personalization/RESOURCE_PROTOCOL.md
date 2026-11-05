# Resource Protocol — Top Mold v0.3.8

## Purpose

Manage optional TOP/MIDDLE/BOTTOM molds, domain procedures, tools, files, and other declared task resources without loading everything for every task. This protocol does not define personal-resource or user-profile storage. Gamma task-profile import is separately specified in `GAMMA_BRIDGE.md`; it is task-domain-only and session-scoped.

## Responsibilities

- **Executing LLM:** identifies a concrete task gap and may recommend or request a resource.
- **Requester / authorized operator:** supplies or approves access when required.
- **Host / adapter:** confirms actual availability, permissions, loading, and execution where implemented.
- **Resource:** declares purpose, inputs/outputs, scope, version, dependencies, and limitations.

A recommendation is not a request; a request is not approval; approval is not proof of access; access is not proof of use; use is not proof that every derived claim is correct.

## Resource descriptor

```json
{
  "resource_id": "example.workflow.v1",
  "resource_kind": "MIDDLE",
  "purpose": "specific task gap this resource can address",
  "capabilities": ["declared capability labels"],
  "input_types": [],
  "output_types": [],
  "domain_scope": [],
  "dependencies": [],
  "permission_class": "operator_review",
  "availability": "declared",
  "version": "1.0.0",
  "limitations": []
}
```

This metadata does not prove that the resource, file, runtime, or integration exists. A descriptor is not authorization and must not contain credentials.

## State vocabulary

- `declared`: metadata says the resource should exist;
- `requested`: access or loading was requested;
- `approved`: the required actor granted approval;
- `available`: actual contents/function were exposed and access was verified by the host;
- `used`: the resource materially contributed to the current task;
- `verified`: a specific claim or operation was independently checked;
- `declined`, `failed`, or `unavailable`: the operation cannot proceed as proposed.

When an envelope marks a resource or context reference as `available` or `used`, include an `evidence_ref` trace pointer. The pointer is an audit aid, not proof that its target exists or is authentic. Approval does not prove loading; loading does not prove correct use; using a resource does not verify every derived claim.

## On-demand flow

1. Check whether current inputs are sufficient.
2. Name the concrete gap.
3. Request the smallest useful resource and state why it is needed.
4. Obtain required approval from the correct actor.
5. Confirm actual exposure/read/connection.
6. Use only relevant material within task scope.
7. Report actual state and limitations.
8. Stop selecting irrelevant resources for the task.

Use MIDDLE/BOTTOM only when they close a demonstrable gap or are explicitly requested. Complexity alone is not sufficient reason to add layers. If resources conflict and no declared scope/priority resolves the conflict, state it or ask rather than inventing precedence.

## Availability and unloading

If access fails, report the failure. If the host cannot unload context, the LLM may stop selecting or referencing a resource for this task; that is not physical unloading or deletion.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.

> **Carried-forward contract:** This document preserves an earlier contract. CP v0.4.3 adds scope-complete iteration, project continuity, reproducible-success review, and testable failure prevention; see `LLM_README.md`, `OUTCOME_LEARNING.md`, and `COMPLETION_AND_CONTINUING_EXPLORATION.md`. Prior contracts remain in force.
