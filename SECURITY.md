# Security Policy

## Scope & threat model

plumbline ships **paste-in text prompts** — they have no tools, retrieval, agency, plugins, or output
sink. Most application-layer LLM risks (excessive agency, insecure plugin/output handling, model or
training-data poisoning, model theft, vector/embedding attacks) are **out of scope for the artifact**,
because the artifact cannot exercise them. What *is* in scope is covered honestly by the advisory
adversarial tier (`evals/tests/security_cases.yaml`): **LLM01** prompt injection via the input,
**LLM02 / LLM07** system-prompt / kernel leakage, and **judge robustness** (indirect injection of the
rubric grader).

## What's hardened in this repo

- **Pinned, lockfiled eval toolchain.** promptfoo is pinned to an exact version in `package.json`,
  with the full transitive tree in `package-lock.json`; CI installs with `npm ci`. No
  `npx promptfoo@latest`.
- **SHA-pinned GitHub Actions.** Every action is pinned to a full commit SHA (with a `# vN` comment).
- **Environment-scoped secret.** `ANTHROPIC_API_KEY` lives in the `evals` Environment (restrict its
  deployment branches to `main`; add a required reviewer once collaborators exist).
- **No code-executing assertions in the key-bearing job.** A deterministic Tier-1 check forbids
  `type: javascript` / `type: python` / inline `transform:` / non-data `file://` assertions across the
  eval suite, so a poisoned test cannot run arbitrary code next to the key.
- **Hardened LLM judge.** Every rubric instructs the grader to treat candidate output as untrusted and
  to ignore any grading instructions embedded in it.
- **Job timeouts** on both CI jobs. **Dependabot** tracks action/npm updates — opened as PRs, never
  auto-merged, and merged only after a 14-day quarantine.
- **Pre-publish scan.** The working tree was scanned for secrets and client PII before going public.

## Reporting a vulnerability

Please open a **private security advisory** via the repository's **Security → Report a vulnerability**
tab. This is a single-maintainer project: reports are handled on a **best-effort** basis with **no
guaranteed response time**.
