# Business artifacts

Plain-language documentation for non-technical stakeholders evaluating **plumbline** and its
reference diagnostic engine. These files capture, **verbatim**, a Q&A from the build conversation
(2026-06-29) — the questions are the operator's; the answers are Claude's (Opus 4.8), reproduced
unedited — and are filed by business-document type.

| File | Type | Answers |
|---|---|---|
| [OVERVIEW.md](OVERVIEW.md) | Overview / explainer | "What is this designed to do and what business problem does it solve?" (explained to a non-technical business owner) |
| [FAQ.md](FAQ.md) | FAQ / honest status | "That's hard to believe." — what is actually proven vs. what is still an untested claim |
| [REQUIREMENTS.md](REQUIREMENTS.md) | Requirements / intake | The information and datapoints required to run an end-to-end pressure test of the engine |

This set is intentionally honest about limitations (see **FAQ.md**): as of capture, the model-graded
quality evals had **not yet run** (no API key configured), so claims about the *quality* of the
engine's advice are untested hypotheses, not demonstrated results. The deterministic quality-control
machinery, by contrast, is verified (11/11 checks).

*Affiliation note: plumbline is independent and not affiliated with or endorsed by Alex Hormozi — see [NOTICE](../../NOTICE).*
