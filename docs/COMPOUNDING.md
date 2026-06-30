# The compounding loop — how plumbline gets smarter with each real case

plumbline improves by grounding the engine in real-world cases and expert ground truth, then **locking
each learning so it can't regress.** Two layers:

## 1. Knowledge (the log)
Each validated case adds reusable patterns and a backlog of concrete engine changes to a **private**
`LEARNINGS.md`. Example: the first real case (a local moving company, graded against a world-class
operator's actual diagnosis) yielded *"the engine is input-starved, not reasoning-poor"* → which became
the **L0 intake layer**.

## 2. Capability (the engine + the gate — the real memory)
Each case becomes a **regression golden** and drives **kernel/prompt fixes**, both locked by the Tier-1
gate so they can never silently regress:
- **Universal learnings → kernel `§4 Diagnostic Discipline`** (stage honesty, assumption hygiene, goal
  framing not goal math, abandoned-is-not-dead, leverage over volume). The kernel compiles verbatim into
  L0/L1/L2, so every interview, diagnosis, and forged vertical inherits them.
- **Case-specific learnings → golden eval cases** the engine must keep passing.

## Privacy split
The engine, tooling, and *generic* fixes are public (this repo). Real records, anonymized goldens, and
the learnings log are **private** — under `datasets/` (git-ignored) or outside the repo — and never ship.
The fix is public; the data is not.

## The flywheel (per case)
1. **Interview** with L0 (`dist/l0.system.md`) → a private record under `datasets/intake/`.
2. `tools/anonymize.py` strips PII → `tools/make_golden.py` builds a golden skeleton (the universal
   §4 MUST-NOTs are pre-baked into every rubric) → fill in the expert **MUST-IDENTIFY** → save under
   `datasets/goldens/`.
3. **Run the regression** — `python tools/run_regression.py`:
   - **Keyless** (default): orchestration-graded via the Workflow tool + `tools/regression.workflow.js`
     — the engine runs each golden and an independent skeptical judge grades it against the rubric.
   - **Keyed** (canonical Gate-1): promptfoo with a budget-capped `ANTHROPIC_API_KEY`.
4. **Failures → fixes:** universal ones go to the kernel/prompts (public PR, gated); case nuances stay
   in the private `LEARNINGS.md`. New goldens join the suite.

Each cycle the golden suite grows and the kernel sharpens — monotonically. That is the compounding.
