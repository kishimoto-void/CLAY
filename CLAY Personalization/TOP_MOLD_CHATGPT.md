# Legacy filename compatibility alias — use CLAY Personalization

**Official system name:** CLAY Personalization (CP) v0.4.3.  
**Canonical instruction file:** `CLAY_PERSONALIZATION.md`.

This filename is retained so older package references and scripts do not break. It is not a separate control layer and does not define a second authority hierarchy. Load `CLAY_PERSONALIZATION.md`, `COMMON_CORE.md`, and the task-relevant module contracts instead.

The former Top Mold v0.3.x contracts remain part of the release lineage. Their compatible behavior is retained in the current CP documentation, schemas, Gamma/Delta reference modules, and tests. Do not load this alias as an additional set of potentially conflicting instructions.

For conversation pacing, use `CONVERSATION_FLOW.md`; for provider translation and current ChatGPT-specific adapter interpretation, use `CHATGPT_ADAPTER.md`.
