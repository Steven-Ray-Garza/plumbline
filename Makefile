# PYTHON defaults to python3 (Linux/macOS/CI). On Windows, override: `make lint PYTHON=python`,
# or just call the python scripts / npm scripts directly.
PYTHON ?= python3

.PHONY: build lint eval eval-l1 eval-l2 eval-security view clean
# Compile prompts from src/ into dist/ (human) and evals/prompts/ (promptfoo).
build:
	$(PYTHON) tools/build.py

# Tier 1 — deterministic, zero tokens. Build, verify sync, run checks + pytest.
lint: build
	$(PYTHON) tools/build.py --check
	$(PYTHON) tools/checks.py
	pytest -q

# Tier 2 — model-graded (needs ANTHROPIC_API_KEY + `npm ci` for the pinned promptfoo).
# Builds first so evals hit fresh artifacts. ADVISORY — not a merge gate.
eval-l1: build
	cd evals && npx promptfoo eval -c promptfooconfig.l1.yaml --output ../eval-results.l1.json
eval-l2: build
	cd evals && npx promptfoo eval -c promptfooconfig.l2.yaml --output ../eval-results.l2.json
eval: eval-l1 eval-l2

# Adversarial security tier (LLM01 / LLM02 / LLM07 + judge robustness). Advisory.
eval-security: build
	cd evals && npx promptfoo eval -c promptfooconfig.security.yaml --output ../eval-results.security.json

view:
	cd evals && npx promptfoo view

clean:
	rm -rf .promptfoo-cache eval-results*.json results __pycache__ tools/__pycache__ tests/__pycache__ .pytest_cache
