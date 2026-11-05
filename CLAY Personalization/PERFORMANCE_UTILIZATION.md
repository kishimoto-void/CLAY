# Performance Utilization — Top Mold v0.3.9

**Status:** design and evaluation protocol. No claim of guaranteed improvement.

## 1. Capability is not the same as utility

A more capable base model does not automatically produce a more useful experience for a particular person or task. Practical utility also depends on whether the model's available capabilities are invoked with the right context, interaction pattern, evidence, tools, and constraints.

Top Mold targets **capability utilization**, not base-model capability creation:

- It does not add model parameters, training, hidden compute, or private provider access.
- It does not independently make the LLM more intelligent.
- It can guide context selection, task framing, response pacing, verification, resource use, and conversational fit.
- Any improvement must be measured; it must not be inferred from the existence of the package or from local structural tests.

## 2. Utilization pathway

1. **Context fit:** select only relevant context and preserve provenance; avoid unrelated personal data.
2. **Task fit:** identify the real objective, constraints, risk, and expected output.
3. **Interaction fit:** answer first, explore when invited, ask only useful questions, and allow either participant to introduce the next relevant idea.
4. **Capability fit:** use search, calculation, code, comparison, explanation, or other tools when available and appropriate; do not simulate unavailable capabilities.
5. **Evidence fit:** distinguish facts, reports, observations, inferences, hypotheses, and unknowns.
6. **Correction fit:** accept corrections, revise interpretations, and preserve unresolved alternatives.
7. **Agency fit:** reduce avoidable operational burden without removing the user's meaningful thinking or decision opportunities.

## 3. Useful utilization versus over-automation

The objective is not to minimize all human effort or maximize autonomous action. Some effort is productive: forming a hypothesis, making a judgment, learning, noticing a physical response, or deciding what matters. The adapter SHOULD remove repetitive or avoidable friction while preserving user agency and useful cognitive participation.

The LLM may lead a bounded instructional or analytical activity when this serves the user's stated goal. That does not transfer real-world decision authority. For hands-on, embodied, preference-sensitive, or responsibility-bearing matters, the human may need to initiate, observe, decide, or validate. Roles should be selected by task, not by a universal hierarchy.

## 4. Evaluation dimensions

Evaluate practical utility with task-specific measures. Possible measures include:

- task success and output quality;
- factual accuracy and calibration of uncertainty;
- relevant evidence use and provenance quality;
- omission, contradiction, and unsupported-claim rates;
- useful follow-up-question yield (not raw question count);
- rate of unnecessary questions, verbosity, or irrelevant personalization;
- context retrieval precision and cross-domain leakage;
- human correction effort and total task effort;
- time, tool use, and token/context overhead where measurable;
- preservation of user agency and learning/understanding where relevant.

Do not collapse every dimension into a single score without documenting weights and trade-offs. Faster or shorter is not automatically better; more detailed is not automatically better.

## 5. Comparative test design

For a credible comparison:

1. Use the same base model/version, tool access, task set, and external information conditions for baseline and Top Mold conditions where possible.
2. Compare a representative set of tasks, not only hand-picked success stories.
3. Use repeated or paired cases; randomize order when practical to reduce order effects.
4. Use a predeclared rubric. Where feasible, have outputs evaluated without the evaluator knowing which condition produced them.
5. Track errors and regressions as carefully as improvements.
6. Separate model/version changes, tool differences, prompt differences, and task difficulty as confounders.
7. Record human effort and experience, not only model output scores.
8. Report uncertainty, sample size, exclusions, and limitations. Do not claim statistical significance without an appropriate design.

Package unit tests establish only local structural or deterministic contract behavior. They do not establish live ChatGPT behavior, model capability uplift, reduced token use, improved user experience, factual truth, or production readiness.

## 6. Social-scale cognition

Cross-domain synthesis can widen an individual's access to ideas and perspectives. It should be treated as an aid to thinking, not as a replacement for society, specialist consultation, plural human perspectives, field observation, or empirical testing. The LLM's available sources and training patterns may share blind spots; wider synthesis is not automatically independent diversity.

## 7. Success criterion

A successful Top Mold configuration should help the user accomplish their actual goal with better quality, understanding, or reduced avoidable friction, while preserving uncertainty, verification, and human decision rights. A higher base-model score or a larger feature count is not by itself success.
