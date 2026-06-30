"""
Smoke tests for the flywheel tooling (anonymize + make_golden). Pure/offline — no yaml, no network.
Run from the repo root:  pytest -q
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import anonymize, make_golden  # noqa: E402

SAMPLE = {
    "schema_version": 1,
    "business_id": "Flex Sun Moving",
    "owner": "Nas",
    "interview_date": "2026-06-30",
    "inferred_axes": {"buyer": "consumer", "motion": "marketing-funnel-led", "stage": "early/cash-flow"},
    "raw_answers": {"price": {"value": "Flex Sun Moving charges $165/hr", "confidence": "measured"}},
    "business_context_blob": "Flex Sun Moving, run by Nas, charges about $1,650 per job.",
}


def test_anonymize_strips_pii():
    anon = anonymize.anonymize(SAMPLE)
    blob = anon["business_context_blob"].lower()
    assert "flex sun" not in blob and "nas" not in blob          # name scrubbed from free text
    assert "owner" not in anon                                   # PII key removed
    assert anon["business_id"].startswith("business-")           # pseudonymized
    assert anon["inferred_axes"]["buyer"] == "consumer"          # non-PII preserved
    assert "flex sun" not in anon["raw_answers"]["price"]["value"].lower()


def test_pseudonym_is_stable():
    assert anonymize.pseudonym("Flex Sun Moving") == anonymize.pseudonym("flex sun moving ")


def test_anonymize_round_money():
    anon = anonymize.anonymize(SAMPLE, round_numbers=True)
    assert "$1,650" not in anon["business_context_blob"]         # coarsened


def test_make_golden_shape():
    case = make_golden.make_golden(anonymize.anonymize(SAMPLE))
    assert case["vars"]["business_context"]
    assert case["assert"][0]["type"] == "llm-rubric"
    rubric = case["assert"][0]["value"]
    assert "MUST NOT" in rubric and "goal-progress" in rubric    # §4 discipline baked in
    assert "buyer=consumer" in rubric                            # triage seeded from axes
