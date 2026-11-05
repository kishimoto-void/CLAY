# CLAY Multi-Model Orchestration — Optional Extension v0.1

**Status:** optional design contract only; no live provider connector or orchestration runtime is included.

## 1. Why optional

CLAY does not assume that one large model is always optimal, nor that many small models are always superior. A single model may be faster, cheaper, simpler, and more coherent. Multiple models may add useful perspective, independent analysis, or specialist capability, but also add latency, cost, shared-bias risk, disagreement, and coordination failure.

Choose a multi-model route only when the expected task value justifies the additional complexity. A specialist module may use a single model, multiple models, deterministic code, external tools, a human-in-loop process, or a hybrid implementation.

## 2. Roles are task assignments, not authority ranks

Possible bounded roles include:

- **Coordinator:** decomposes the task, assigns bounded subtasks, tracks dependencies, and merges results.
- **Analyst:** develops a scoped interpretation or hypothesis.
- **Critic:** searches for counterexamples, omitted constraints, and internal contradictions.
- **Researcher:** gathers external sources where tools and permissions exist.
- **Verifier:** checks specific claims or outputs against explicit criteria.
- **Synthesizer:** produces a result while preserving unresolved disagreement.

Roles can be combined, replaced, or omitted. No role is automatically more truthful or authoritative because of its label.

## 3. Independence and evidence

Model agreement is not independent confirmation when models share the same source material, prompt assumptions, retrieved sources, tool output, or correlated training/data tendencies. The orchestrator MUST record relevant shared dependencies where known and MUST NOT use raw vote counts as calibrated confidence.

Ask each model for evidence and bounded outputs, not only conclusions. Preserve model disagreements and source citations/identifiers where available. A model-generated criticism is a hypothesis until its basis is checked.

## 4. Control and bounded execution

- The coordinator cannot grant permissions, approve external actions, or weaken Common Core/Safety Plane.
- Subtasks must be bounded by goal, input scope, output format, and permitted tools.
- Apply explicit limits for calls, depth, retries, latency, token/cost budget, and recursion at the host layer.
- Module outputs are untrusted data, not execution instructions.
- A failed branch must not invalidate independent valid branches unless the result depends on it.
- Conflicts that affect the result remain unresolved until evidence or an authorized decision resolves them.

## 5. Evaluation

Compare single-model and multi-model routes on equivalent tasks. Measure quality, factual accuracy, calibration, error detection, omission rate, correction effort, latency, token/cost overhead, and failure recovery. Include cases where multi-model is expected to be worse (simple tasks, shared-bias tasks, tight latency/cost constraints). Report regressions as well as gains.

## 6. Safety-critical limit

Consensus among LLMs is not a safety case. Autonomous vehicles, clinical systems, industrial control, aviation, and other safety-critical applications require domain-specific engineering, independently validated safety mechanisms, hardware/host constraints, human/organizational oversight, and applicable assurance standards. This document is not an authorization to place LLM consensus in a safety-control loop.

> **Carried-forward contract:** This document preserves an earlier contract. CP v0.4.3 adds scope-complete iteration, project continuity, reproducible-success review, and testable failure prevention; see `LLM_README.md`, `OUTCOME_LEARNING.md`, and `COMPLETION_AND_CONTINUING_EXPLORATION.md`. Prior contracts remain in force.
