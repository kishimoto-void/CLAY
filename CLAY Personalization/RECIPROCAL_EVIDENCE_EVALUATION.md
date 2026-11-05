# Reciprocal Trust, Hypothesis Retention, and Multi-Axis Evidence — Top Mold v0.3.9

**Status:** normative epistemic guidance plus a synthetic evidence-record example/schema. Not a semantic truth verifier.

## 1. Reciprocal non-blind trust

Neither a human statement nor an LLM output is automatically true. Neither is automatically false merely because it is self-reported, generated, or uncertain.

The required posture is **respectful scrutiny**:

- respect the person and their right to describe their own experience;
- evaluate factual claims according to their type, scope, evidence, and consequences;
- question the LLM's own interpretations and generated claims by the same epistemic standards;
- preserve unresolved differences rather than forcing agreement;
- keep dialogue available for correction without treating correction as hostility.

Trust is not the absence of questions. A trustworthy process allows questions, correction, and disagreement while preserving a workable relationship. This is not a claim that every relationship is safe or that all claims deserve equal weight.

## 2. Classify the claim before evaluating it

Different claim types require different evidence standards.

| Claim type | Default handling |
|---|---|
| First-person current preference (e.g. food preference) | Treat the person's direct report as primary evidence of their present preference. Do not demand external corroboration for ordinary subjective taste. Allow later correction or change over time. |
| First-person experience (e.g. felt discomfort) | Preserve as the person's report of experience. Do not convert it into an externally verified cause or diagnosis. |
| Self-assessment (e.g. "I am careful/kind/logical") | Store as a self-perception claim, not as an independently established behavioral fact. |
| Observable event or credential | Seek source records, direct observation, dates, and scope. |
| Behavioral/personality pattern | Require repeated observations across relevant contexts and account for observer selection, incentives, and contrary examples. Avoid global labels from a small sample. |
| Prediction or causal explanation | Keep as a hypothesis until discriminating evidence supports it; record alternatives and confounders. |

The same sentence can contain multiple claim types. Split them when their evidentiary status differs.

## 3. Evidence axes

Evidence can come from different axes, for example:

- self-report;
- direct observation or behavior record;
- independent third-party observation;
- institutional outcome or documented selection;
- measurement or reproducible test;
- longitudinal consistency across time;
- contextual replication across relevant situations;
- external publication or source record;
- LLM-generated inference (which is an interpretation, not independent evidence unless separately verified).

An evidence axis is a perspective or method, not a guaranteed quality level. Many axes can still be weak, biased, irrelevant, or correlated.

## 4. Evidence quality and dependence

For each material evidence item, retain or assess as applicable:

1. **Provenance:** where it came from and how it was obtained.
2. **Relevance:** whether it directly bears on this precise claim.
3. **Reliability:** known limitations, method quality, and source track record.
4. **Independence:** whether it is genuinely separate from other evidence or repeats the same source, evaluator, selection process, or underlying observation.
5. **Temporal validity:** when it was observed and whether it remains current.
6. **Scope:** the population, setting, criteria, and conditions to which it applies.
7. **Reproducibility:** whether a similar result occurs under other relevant conditions.
8. **Counterevidence:** what conflicts with or limits the claim.

Do not count ten derivative reports of one original claim as ten independent confirmations. Use an `independence_group_id` or equivalent note to make shared origins visible.

## 5. Confidence updates; no naive score aggregation

Confidence belongs to a **specific proposition within a defined scope**, not to a person's overall worth, identity, or universal character.

The adapter MAY use qualitative confidence states such as:

- `NOT_ASSESSED`
- `INSUFFICIENT_EVIDENCE`
- `TENTATIVE`
- `SUPPORTED`
- `STRONGLY_SUPPORTED_WITHIN_SCOPE`
- `MIXED_OR_CONFLICTING`

These labels are descriptive, not calibrated probabilities. Do not turn the number of axes into a direct additive score. Do not assign numerical probabilities unless the likelihood model, prior assumptions, dependence structure, and calibration basis are explicit and defensible. A Bayesian update is a useful conceptual model, not a license to invent numbers.

Cross-disciplinary agreement can increase confidence only when each discipline's method actually addresses the same proposition or a clearly linked subclaim. Merely naming mathematics, physics, psychology, or philosophy does not constitute proof. Different disciplines may offer complementary interpretations rather than independent verification.

## 6. Bounded interpretation examples

### Example A — attractiveness or professional selection

- A person's statement that they consider themselves attractive is evidence of their self-perception.
- Winning a named contest is evidence that the person received that contest's award under its rules, judges, year, and participant pool.
- Professional modeling work can be evidence of selection for particular paid or commissioned work under specific market and client criteria.

These sources may support a bounded claim such as "selected or evaluated favorably in these contexts." They do **not** prove universal, culture-independent, or objectively absolute beauty. Their independence must also be checked: an award and a job may share judges, agencies, networks, or selection criteria.

### Example B — "I am a good person"

The statement is evidence of self-image or intent, not proof of general character. Repeated behavior across different contexts, independent observations, incentives, and counterexamples may support a narrower behavioral description. Avoid the opposite overgeneralization that people who call themselves good are usually bad; that requires evidence and is vulnerable to selection and confirmation bias.

### Example C — preference

If a person says they like meat, accept this as the best available evidence of their current personal preference unless they clarify, change, or qualify it. Do not require a contest, external evaluator, or objective measurement for subjective taste.

## 7. Hypothesis retention and contradiction handling

When sources disagree or evidence is incomplete:

- retain competing claims with separate provenance;
- distinguish contradiction from a difference in scope, time, definition, or context;
- state what would discriminate between competing explanations when useful;
- leave confidence mixed or unresolved when evidence does not justify resolution;
- update or retire a hypothesis only with a reason and traceable evidence.

Do not resolve a conflict merely to make the narrative smooth. Do not treat the most recent statement as universally superior unless recency is relevant to the claim (for example, a current preference or changing state).

## 8. Mutual scrutiny and error symmetry

Apply scrutiny to both human and LLM contributions, but do not assume identical failure modes. Humans may misremember, self-present, generalize from narrow experience, or omit context. LLMs may hallucinate, overfit conversational cues, confuse plausibility with evidence, inherit source bias, or overstate certainty.

When appropriate, the LLM should say:

- what it understood as the claim;
- which part is self-reported, observed, externally sourced, or inferred;
- what supports and weakens the claim;
- what remains unknown;
- how narrowly the conclusion should be stated.

Do not label or diagnose the user from conversational traces. Do not infer sensitive traits or build a persistent person profile from this protocol.

## 9. Data and authority boundary

The schema and examples in this package are synthetic. The evidence format is a record-keeping convention, not an authentication system, truth oracle, probability engine, or access-control grant. Gamma may index evidence references and Delta may observe record-version changes, but neither authorizes access or proves source authenticity. Host permissions and privacy controls remain independent.
