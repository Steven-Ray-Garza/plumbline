"""
Tier-1 deterministic gate, exposed as pytest cases so it runs alongside the existing suite.
Run from the repo root:  pytest -q   (or: make lint)

Each prompt-engineering check from tools/checks.py becomes one test. They are pure/offline and
operate on the committed artifacts in dist/, so build first (`python tools/build.py`) — the
build_is_in_sync test enforces that the committed artifacts match a fresh build.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import build, checks  # noqa: E402


@pytest.mark.parametrize("check_fn", checks.ALL_CHECKS, ids=lambda fn: fn.__name__)
def test_tier1_check(check_fn):
    name, ok, detail = check_fn()
    assert ok, f"{name}: {detail}"


def test_build_is_in_sync():
    """Committed dist/ and evals/prompts/ must equal a fresh build from src/."""
    stale = [p.relative_to(ROOT) for p, content in build.render().items()
             if (p.read_text(encoding="utf-8") if p.exists() else None) != content]
    assert not stale, f"stale artifacts (run `python tools/build.py`): {stale}"
