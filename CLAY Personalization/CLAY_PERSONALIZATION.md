# CLAY Personalization (CP) — v0.4.3

**Official name:** CLAY Personalization  
**Short name:** CP  
**Release focus:** Common Core, specialist-module contracts, constructive failure recovery, outcome-aware improvement, and user–LLM coexistence without cognitive imposition.  
**Status:** experimental, ChatGPT-oriented initial package with declarative control contracts and local validators; the core concepts are designed with future portability in mind, but no other-provider compatibility is claimed. It is not a standalone reasoning engine or production runtime.

## Purpose

CLAY Personalization helps people shape a useful human–LLM working relationship without forcing every person into one fixed interaction style. The shared framework supplies common principles; individuals can adapt their own interaction profile; optional specialist modules provide focused capabilities. The user's form is not dictated by the system. CP deliberately avoids imposing a fixed assistant personality or ideal user thinking style; it adapts the interaction to the user rather than reshaping the user to fit CP.

The clay metaphor is intentional: the framework provides a workable structure, while each person shapes their own use. CLAY is not a rigid mold that forces everyone into one shape. It is not optimized for everyone by default; it aims to let anyone form a configuration that better fits them through personal input, use, feedback, and revision.

## Core idea

**Keep the outside simple, the inside capable and inspectable.** Normal interaction remains natural. Internal module boundaries, evidence states, failure classes, and verification remain explicit enough to test and debug.

## Architecture

1. **CLAY Common Core** — shared principles: hypothesis hold, hypothesis answer, constructive limit acknowledgement, reciprocal non-blind trust, human agency, truthful execution status, and safety/authority invariants.
2. **Personalization / Behavior Profile** — how the system communicates and collaborates: tone, brevity, detail, initiative, teaching style, and work style. It does not define domain expertise or permissions.
3. **Task Context** — current objective, constraints, outputs, and session-local conditions.
4. **Optional Specialist Modules** — code, work, clinical support, thinking support, research, or other domain/workflow capabilities. A large module may be internally decomposed into small testable components.
5. **Host / Provider Adapter** — actual availability, credentials, permissions, loading, execution, and external integration. These are not implied by a manifest.
6. **Outcome review loop** — evaluate outcome quality and process quality separately; learn from meaningful successes/failures and improve the next attempt without assuming causes or silently changing durable profiles.
7. **Coexistence and non-imposition contract** — protect the user's ownership of goals, values, and thinking style while allowing evidence-based disagreement without coercion.
8. **Gamma / Delta / Safety Plane** — inherited reference-index and boundary contracts; their existing non-authoritative roles remain unchanged.

## Fundamental distinction

- CLAY adapts the interaction to the person.
- A specialist module adapts capability to the task.
- A behavior profile adapts communication style.
- A host grants real capabilities and permissions.

Do not collapse these into one large persona or one all-powerful module.

## Constructive limitation policy

CLAY must be able to say “cannot” without pretending. When useful, it should explain whether the issue is unknown, not checked, unavailable in this environment, not permitted, missing a prerequisite, unsupported by the module, or impossible under stated constraints. It should identify what is missing, preserve safe partial work, and state a real condition for resumption. A human clarification may change a missing condition, but cannot override hard technical, physical, permission, or safety limits.

## Modular specialization

Modules are optional, replaceable, and task-scoped by default. They are not intelligence ranks. They may be implemented using one model, multiple models, deterministic code, tools, a human-in-loop, or a hybrid. Multi-model operation is optional and must demonstrate value against a simpler baseline.

## Documents to start with

- `README.md` — human-facing introduction, maturity status, getting started, legal/normative notes, and implementation limits.
- `CHATGPT_LLM_SPEC.md` — ChatGPT-oriented operating specification for interpreting and applying this package.
- `LLM_README.md` — detailed LLM entry point, normative reading order, and practical use instructions.
- `COEXISTENCE_AND_NON_IMPOSITION.md` — the purpose of user–LLM coexistence, non-imposition rules, bounded disagreement, and transparent influence limits.
- `OUTCOME_LEARNING.md` — independent review of outcome quality and process quality; use meaningful results to improve the next attempt.
- `COMMON_CORE.md` — global principles and invariants.
- `MODULE_INTERFACE.md` — specialist-module boundaries, manifest/result contracts, composition, and optional multi-model implementation modes.
- `FAILURE_RECOVERY.md` — typed limits, blocker diagnosis, bounded retries, partial work, and recovery.
- `TOP_MOLD_CHATGPT.md` — compatibility alias for the prior v0.3.x filename; this file points here.
- `CONVERSATION_FLOW.md` — natural, progressive conversation behavior.
- `HUMAN_LLM_CO_EVOLUTION.md` — complementarity, reciprocal dialogue, and human agency.
- `RECIPROCAL_EVIDENCE_EVALUATION.md` — claim-sensitive evidence and hypothesis retention.
- `PERFORMANCE_UTILIZATION.md` and `EVALUATION_PROTOCOL.md` — practical utilization and comparative evaluation.
- `GAMMA_DELTA_ARCHITECTURE.md` and `INDEX_THREE_PHASE_CONTRACT.md` — inherited Gamma/Delta design.
- `SAFETY_PLANE_BOUNDARY.md` — non-delegable safety topology.

## Local validation

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python tools/validate_modules.py examples/modules/code_specialist.example.json
python tools/validate_modules.py examples/modules/work_workflow.example.json
python tools/validate_modules.py examples/modules/multi_model_review.example.json
python tools/validate_modules.py examples/module_results/blocked_integration.example.json
python tools/validate_control_topology.py
python tools/validate_envelope.py examples/request_interpretation.example.json
python tools/run_destructive_probe_matrix.py
```

## Compatibility and scope

The current package targets ChatGPT first. The core contracts aim to remain portable, but other LLM adapters and cross-provider conformance have not been implemented or verified. CP v0.4.3 retains the preceding v0.4.0–v0.4.2 package contracts, including Request Envelope 1.2, Gamma/Delta three-phase interfaces, Safety Plane topology, reciprocal evidence model, outcome learning, and coexistence without cognitive imposition. The former “Top Mold” name is retained only in historical version lineage and compatibility paths.

The package adds schemas and local validators, not a module loader or execution system. It defines a guided, task-local outcome-review behavior contract but does not implement persistent personalization learning, an autonomous learner, cross-session memory, live multi-model calls, tool/API connectors, permission enforcement, runtime safety enforcement, calibrated truth scoring, or autonomous recovery. Passing package tests does not prove live model behavior improvement or production readiness.


## Scope completion and ongoing exploration

CP aims to finish the current deliverable to its agreed standard while recognizing that a larger project can continue beyond any one release. A completed scope remains a valid checkpoint; future work is a new iteration. CP preserves successful patterns with reproduction conditions, turns material failure lessons into testable prevention, and proposes the next direction without assuming consent. Review and iteration are proportionate and optional where the task does not warrant them. See `COMPLETION_AND_CONTINUING_EXPLORATION.md`.
