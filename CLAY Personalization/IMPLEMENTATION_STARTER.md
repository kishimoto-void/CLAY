# CLAY Personalization v0.4.3 — Implementation Starter

## What is executable now

The `clay_runtime` package provides a deterministic reference pipeline:

`JSON Request Envelope -> schema + semantic validation -> task overlay resolution -> adapter-context rendering`

- `ClayRuntime.prepare(envelope)` validates the canonical Request Envelope 1.2 contract.
- Non-READY envelopes return their readiness state without rendering execution context.
- READY envelopes receive global dial defaults plus a bounded mapping from task mode to an existing task-domain overlay.
- The renderer emits a compact, source-preserving instruction block for a host LLM adapter.
- Invalid input fails closed with structured validation errors.
- Configuration loading rejects duplicate JSON keys, oversized files, excessive nesting, unsupported schema identifiers, and invalid dial values.

## Quick start

Requires Python 3.10+ and the existing development dependency `jsonschema>=4.21,<5`.

```bash
python -m pip install -r requirements-dev.txt
python -m unittest tests.test_runtime -v
python tools/prepare_task.py examples/request_interpretation.example.json
```

Library use:

```python
from clay_runtime import ClayRuntime

runtime = ClayRuntime()
result = runtime.prepare(envelope)

if result.status == "PREPARED":
    adapter_prompt = result.adapter_context
elif result.status == "INVALID":
    print(result.errors)
else:
    # READY was not established; do not dispatch to the LLM.
    print(result.status)
```

## Task-mode mapping

| Request Envelope task mode | Applied task overlay |
|---|---|
| `work` | `development` |
| `design` | `development` |
| `research` | `learning` |
| `verify` | `general` |
| `chat` or omitted | `general` |

This mapping is intentionally explicit and deterministic. It is not natural-language classification. Overlay values affect interaction preferences only; they cannot grant capability, authority, permission, or safety exceptions.

## Host integration contract

A production host should:
1. Parse the user's natural-language request using its own LLM/application layer.
2. Construct a Request Envelope with provenance and unresolved questions preserved.
3. Call `ClayRuntime.prepare`.
4. Dispatch only a `PREPARED` adapter context to the selected LLM.
5. Enforce permissions, approvals, tool allowlists, budgets, and safety policy outside CLAY.
6. Record actual tool execution and verification separately from model claims.
7. Return typed outcomes and preserve unknowns; never infer success from a generated answer alone.

## Explicit non-capabilities

This implementation does **not**:
- parse natural language or decide user intent;
- call ChatGPT or another LLM;
- guarantee that a model follows the rendered instructions;
- detect prompt injection or verify factual truth;
- execute tools, grant permissions, or approve external actions;
- store personal profiles, learn durable preferences, or persist checkpoints;
- implement Gamma/Delta persistence, connectors, event delivery, or automatic profile activation;
- provide live Safety Plane enforcement.

The Safety Plane and host authorization remain external interfaces. This package is an executable reference adapter, not a production security boundary.

## Test interpretation

`tests/test_runtime.py` covers the deterministic pipeline's happy path, non-READY short-circuit, invalid-envelope fail-closed behavior, and duplicate-key rejection. Existing package tests continue to cover the underlying schemas and reference components. Passing local tests does not establish live LLM adherence or production safety.
