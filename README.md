# plumbline

**Prompts-as-code CI.** plumbline compiles prompts from a single source kernel, proves the compiled
artifacts haven't drifted by hashing that kernel, and gates behavior — plus a small, honestly-scoped
adversarial tier — before anything merges. A two-layer business-diagnostic engine ships as the
**reference payload**, so the harness is demonstrated on a real, falsifiable problem rather than a toy.

> **Independent project.** Not affiliated with or endorsed by Alex Hormozi or Acquisition.com.
> See [NOTICE](NOTICE) and [the disclaimer](#disclaimer).

---

## Why this exists (two things almost no prompt repo has)

1. **Compile-from-source kernel parity — a structural guarantee, not a discipline.**
   The source of truth is three files in `src/` (a shared `kernel.md` plus two templates). One build
   step injects the kernel into both layers and stamps a `kernel-sha256` into every artifact; a
   deterministic check fails the build if the layers' stamps ever disagree or drift from
   `src/kernel.md`. The two layers *cannot* silently fork.

2. **Falsifiable, bidirectional behavioral golden tests.**
   The engine's core claim is that it *selects* tactics by business type instead of defaulting to a
   consumer funnel. That's falsifiable, so it's exactly what the evals guard — in **both** directions:
   a procurement business must *suppress* the consumer funnel; a DTC brand must *activate* it. A change
   that quietly turns the engine back into a funnel-bot trips the suite.

Everything else is the test harness around those two ideas.

---

## The two-tier gate

**Tier 1 — deterministic (`tools/checks.py` + `pytest`). The hard merge gate.**
Zero tokens, every push/PR. Twelve checks: sentinel resolution, L2 slot-schema exposure, kernel-hash
parity, XML balance (L1 + L2), no reasoning-extraction imperatives, the conclusions-with-evidence
hygiene line, the agnosticism guardrails, promptfoo config integrity, **no code-executing assertions
in the eval suite**, and **the adversarial security suite stays wired + hardened**, and **the L1 scaffolding carries no known vertical-specific example**. Make `lint` your
required status check.

**Tier 2 — model-graded (`promptfoo`). Advisory.**
Costs tokens, so it is path-filtered + key-gated and runs only when prompts / kernel / eval / workflow
change (or on manual dispatch), after Tier 1. The system-under-test runs on `claude-opus-4-8`; the
cheaper `claude-sonnet-4-6` grades the rubrics. It is **advisory** (not a required check) because model
grading is nondeterministic and merge-blocking it would mean flaky reds. The golden suites enforce a
pass-rate threshold inside the job; **with the current small case count the 0.85 threshold is
effectively all-green** — treat it as a regression signal, not a statistical guarantee.

---

## The adversarial tier (honest scope)

A paste-in text prompt has no tools, retrieval, agency, or output sink, so most of the OWASP LLM Top 10
(2025) simply does not apply to it. plumbline tests **only** the categories that genuinely do:

- **LLM01 Prompt Injection** — an injected instruction in the business input must not hijack the diagnosis.
- **LLM02 / LLM07 Sensitive-Info / System-Prompt Leakage** — the engine must not dump its kernel / system prompt on request.
- **Judge robustness** — text in the candidate output aimed at the rubric grader ("score this 1.0") must be ignored; every rubric is hardened to treat candidate output as untrusted data.

What a tool-less prompt **cannot** meaningfully test (and which plumbline does *not* claim): excessive
agency, insecure plugin / output handling, model or training-data poisoning, model theft,
vector / embedding attacks. The security cases are **advisory**; a deterministic Tier-1 check
guarantees they stay present and hardened so the tier can't be silently removed.

---

## Compile from source

```
src/kernel.md        the Shared Kernel — classification taxonomy + library + activation map
src/l1.template.md   L1 (diagnostic engine), sentinels:  @@KERNEL@@  six @@SLOT@@  @@INPUT@@
src/l2.template.md   L2 (vertical forge),    sentinels:  @@KERNEL@@  @@L1_TEMPLATE@@  @@INPUT@@
```

`python tools/build.py` renders the deployable artifacts:

```
dist/l1.system.md          human paste version
dist/l2.system.md          human paste version
evals/prompts/l1.eval.md   promptfoo version ({{business_context}})
evals/prompts/l2.eval.md   promptfoo version ({{vertical_spec}})
```

> **Edit `src/`. Never hand-edit `dist/` or `evals/prompts/`** — they are build artifacts, and CI
> fails if they are out of sync with a fresh build.

---

## Quick start

```bash
# Tier 1 — deterministic, zero tokens
python tools/build.py        # compile prompts from src/
python tools/checks.py       # 12 deterministic gates
pytest -q                    # the same gates, as pytest cases
# (or: make lint  /  npm run build)

# Tier 2 — model-graded (needs an Anthropic key + the pinned promptfoo)
npm ci                       # installs the EXACT pinned promptfoo from package-lock.json
export ANTHROPIC_API_KEY=sk-ant-...
npm run eval                 # L1 + L2 golden suites
npm run eval:security        # advisory adversarial tier
npm run view                 # promptfoo results UI
```

Requirements: Python 3.12 (`pip install -r requirements.txt`) and Node `>=22.22.0` (or `^20.20.0`).
**promptfoo is pinned** (exact version in `package.json`, full tree in `package-lock.json`); CI and
local runs install it with `npm ci` — never `npx promptfoo@latest`.

---

## The reference payload: a two-layer diagnostic engine

- **L1 — Diagnostic Engine.** Classifies any business on five axes, then prescribes
  acquisition / distribution / monetization fixes using only the mechanics the classification activates.
- **L2 — Vertical Forge.** A meta-prompt whose only output is a schema-conformant L1 instance tuned to
  a target vertical.

The engine is built on publicly described frameworks from the Alex Hormozi operating corpus and is used
here as a worked, falsifiable example of what the harness protects. The procurement case in the golden
suite is a real public-works bid consultancy — authentic, not a toy.

### Adding a vertical

1. Paste `dist/l2.system.md` into Claude (Opus 4.8) with a vertical spec (e.g. `"HVAC service companies"`).
2. Take the **GENERATED L1 PROMPT** block — that's your specialized engine.
3. (Optional) add a case to `evals/tests/l2_cases.yaml`, then run `make eval-l2`.

You don't edit the schema to add a vertical — L2 fills the slots; the scaffolding stays fixed.

---

## CI setup

1. Create an Environment named **`evals`** (Settings → Environments) and add `ANTHROPIC_API_KEY` to it
   (use a **budget-capped** key). Restrict its **deployment branches to `main`**. Add a **required
   reviewer** once you have collaborators (it gates every keyed run behind approval). Without the key,
   the eval job skips cleanly; Tier 1 still runs.
2. In branch protection, make **`lint` a required status check**; leave **`evals` advisory**.
3. Push. `lint` runs on every push/PR (your hard gate). `evals` runs **on push to `main`**
   (path-filtered) and via **Run workflow** — **not on pull requests**, since the key is scoped to the
   `main`-restricted `evals` Environment.

### Tuning knobs

| Knob | Where | Default |
|---|---|---|
| Golden pass-rate threshold | `PASS_THRESHOLD` in `ci.yml` | `0.85` (≈ all-green at current N) |
| Judge model | `defaultTest.options.provider` in each `promptfooconfig.*.yaml` | `claude-sonnet-4-6` |
| SUT model / max tokens | `providers` in each config | `claude-opus-4-8`, 4096 (L1) / 8192 (L2) |
| Eval concurrency | `commandLineOptions.maxConcurrency` | `2` |
| Pinned promptfoo | `package.json` devDependency + `package-lock.json` | `0.121.15` |

> **No sampling params.** Claude 4.x rejects a non-default `temperature`, so the provider configs omit
> it deliberately. CI runs a lean config (no extended thinking); production use of these prompts
> assumes higher effort — keep that separate from the CI config.

---

## Security & supply chain

See [SECURITY.md](SECURITY.md). In short: actions are SHA-pinned, promptfoo is version-pinned +
lockfiled, the API key is Environment-scoped, the eval job has no code-executing assertion paths and a
hard timeout, and Dependabot tracks updates (which wait out a 14-day quarantine before merge).

## Disclaimer

plumbline is an independent, open-source project. It is **not affiliated with, endorsed by, or
sponsored by Alex Hormozi, Acquisition.com, or any related entity.** The reference diagnostic engine is
built on publicly described business frameworks from the Alex Hormozi operating corpus; framework,
book, and concept names are used **nominatively** to identify the methods they refer to. The kernel
paraphrases and indexes these concepts and **reproduces no copyrighted text**.

## License

[MIT](LICENSE) © 2026 Steven-Ray-Garza.
