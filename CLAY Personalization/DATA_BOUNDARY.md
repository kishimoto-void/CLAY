# Package Data Boundary — Top Mold v0.3.8

## Scope

This release is a generic control-contract package, not a personal profile or memory package. It includes one synthetic task-domain profile example for the Gamma bridge; this is not an individual profile. The ZIP contains no individual profile records, person-specific preference history, personal-resource manifest, account identifier, credential, biometric record, precise location record, or user-specific conversation excerpt.

## Included

- task-domain profile schema and a synthetic Gamma import packet;
- a plan-only validator for task-profile schema, digest, identity/version consistency, and compatibility.

- generic instruction and authority contracts;
- synthetic task-envelope examples;
- generic configuration defaults;
- schema and validation tools;
- synthetic conformance and destructive-test cases;
- reports describing package-level checks.

## Not included

- user profile or personalization database;
- persistent memory or retention backend;
- personal files, personal-resource manifest, or personal-history export;
- credentials, API keys, session tokens, or account identifiers;
- biometric or precise-location records.

## Runtime boundary

Callers may supply task inputs at runtime. Those inputs are not embedded in this package and are not stored by the included validator. The validator reads a local JSON envelope and emits validation status/errors; it is not an archive, memory, or personal-data manager. The schema 1.2 `transformations` and `conflicts` records store references and short claims only; source payloads should remain in their source location. Any future runtime that records inputs requires a separate data-handling review, including minimization, redaction, access control, retention, and deletion behavior.

## Verification

The package test suite checks that person-specific artifacts and configuration keys are absent, the Gamma example is synthetic/task-domain-only, and the declared package boundary is consistent. Such checks do not prove that a caller's external runtime contains no personal data.


## v0.3.9 relationship/evidence/utilization overlay

This document is carried forward from the v0.3.8 baseline. The v0.3.9 additions are specified in `HUMAN_LLM_CO_EVOLUTION.md`, `RECIPROCAL_EVIDENCE_EVALUATION.md`, and `PERFORMANCE_UTILIZATION.md`. No additional runtime, persistence, source authentication, or truth-verification capability is implied by this cross-reference.


## v0.3.9 evidence-record boundary

The evidence-bundle example is synthetic and stores source references and evaluation notes, not real personal records. The evidence schema is not a source authenticator or truth verifier. No persistent person profile or personal-data store is added.


## v0.4.0 module data rule

Module manifests and synthetic examples define capabilities and data scope only. They do not contain personal profiles, preference histories, credentials, or actual runtime user data. Persistent personal-data handling remains out of scope and requires a separate reviewed design and explicit consent.
