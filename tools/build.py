#!/usr/bin/env python3
"""
build.py — Compile the Hormozi Operator Codex from source.

Source of truth lives in src/:
    kernel.md         the Shared Kernel (taxonomy + library + activation map)
    l1.template.md    L1 Diagnostic Engine, with @@KERNEL@@, six @@SLOT@@, @@INPUT@@
    l2.template.md    L2 Vertical Forge, with @@KERNEL@@, @@L1_TEMPLATE@@, @@INPUT@@

Outputs (build artifacts — do not edit by hand):
    dist/l1.system.md         human paste version (clean, [INSERT ...] placeholder)
    dist/l2.system.md         human paste version
    evals/prompts/l1.eval.md  promptfoo version ({{business_context}})
    evals/prompts/l2.eval.md  promptfoo version ({{vertical_spec}}; embedded L1 raw-wrapped)

Kernel parity is structural: the kernel is injected from a single file into both layers, so they
cannot drift. A short kernel-sha256 stamp is embedded in each artifact for the Tier-1 hash check.

Stdlib only. Run:  python tools/build.py        (writes artifacts)
                   python tools/build.py --check (fails if artifacts are stale)
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST = ROOT / "dist"
EVAL_PROMPTS = ROOT / "evals" / "prompts"

SLOTS = ["@@ROLE@@", "@@BACKGROUND@@", "@@ACTIVE_MODULES@@",
         "@@QUALIFICATION@@", "@@EXAMPLES@@", "@@LEXICON@@"]

# Generic defaults for the base (un-specialized) L1 engine. A direct run self-classifies in Step 0.
L1_BASE_DEFAULTS = {
    "@@ROLE@@": (
        "You are a senior business diagnostician trained on the full Alex Hormozi operating corpus\n"
        "($100M Offers, Leads, Money Models, and the Lost Chapters). You diagnose acquisition,\n"
        "distribution, and monetization across ANY business type — consumer, SMB, enterprise, or\n"
        "public-sector procurement. You are not a funnel specialist and you do not assume a business\n"
        "runs on ads, video, or affiliates until the evidence says so. Your expertise is selecting the\n"
        "right framework for the business in front of you and prescribing the smallest intervention\n"
        "that moves the binding constraint."
    ),
    "@@BACKGROUND@@": (
        "(No vertical preset. Derive buyer type, sales motion, ticket/cycle, offer character, and\n"
        "stage from the Step 0 Triage against the business context below.)"
    ),
    "@@ACTIVE_MODULES@@": (
        "(No preset. Treat the full Hormozi Library as available and activate the subset the Step 0\n"
        "classification warrants, per the Conditional Activation Map. Default-off mechanics — VSL,\n"
        "affiliate activation, paid ads, Veblen/luxury — stay off unless the classification turns\n"
        "them on.)"
    ),
    "@@QUALIFICATION@@": (
        "(Select the qualification logic that fits the buyer and sales motion identified in Step 0:\n"
        "BANT for sales-led B2B; fit/eligibility gating — credentials, registration, bonding, calendar\n"
        "— for procurement; light or none for self-serve/transactional.)"
    ),
    "@@EXAMPLES@@": "(none — the base engine runs zero-shot and is domain-neutral.)",
    "@@LEXICON@@": "(Use the operator's own terminology exactly as it appears in the business context.)",
}

# What the embedded L1 schema inside L2 shows in place of the kernel (kept lean; L2 reproduces the
# kernel verbatim from its own <knowledge> per generation_protocol step 4).
KERNEL_PLACEHOLDER_IN_SCHEMA = "[SHARED KERNEL — reproduce verbatim from <knowledge> above]"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _kernel_hash(kernel: str) -> str:
    return hashlib.sha256(kernel.encode("utf-8")).hexdigest()[:16]


def _stamp(khash: str) -> str:
    return (f"<!-- BUILD ARTIFACT — do not edit. Source: src/. "
            f"kernel-sha256: {khash}. Regenerate: python tools/build.py -->\n\n")


def _build_l1_body(kernel: str) -> str:
    """L1 with kernel + slot defaults filled. @@INPUT@@ still present (caller swaps it)."""
    body = _read(SRC / "l1.template.md").replace("@@KERNEL@@", kernel)
    for token, value in L1_BASE_DEFAULTS.items():
        body = body.replace(token, value)
    return body


def _build_l1_schema_for_embedding() -> str:
    """The L1 template as a SCHEMA for L2: kernel -> short placeholder, slot tokens PRESERVED,
    @@INPUT@@ -> literal {{business_context}} so a generated L1 ends with the CI input token."""
    schema = _read(SRC / "l1.template.md").replace("@@KERNEL@@", KERNEL_PLACEHOLDER_IN_SCHEMA)
    schema = schema.replace("@@INPUT@@", "{{business_context}}")
    return schema  # six @@SLOT@@ tokens remain on purpose — they document L1's fillable slots


def _build_l2_body(kernel: str, *, raw_wrap_schema: bool) -> str:
    """L2 with kernel + embedded L1 schema. @@INPUT@@ still present (caller swaps it).
    raw_wrap_schema wraps the embedded schema in Nunjucks {% raw %} so promptfoo does not eat the
    literal {{business_context}} token inside it."""
    body = _read(SRC / "l2.template.md").replace("@@KERNEL@@", kernel)
    schema = _build_l1_schema_for_embedding()
    if raw_wrap_schema:
        schema = "{% raw %}\n" + schema + "\n{% endraw %}"
    body = body.replace("@@L1_TEMPLATE@@", schema)
    return body


def render() -> dict[Path, str]:
    kernel = _read(SRC / "kernel.md")
    khash = _kernel_hash(kernel)
    stamp = _stamp(khash)

    l1_body = _build_l1_body(kernel)
    l2_eval_body = _build_l2_body(kernel, raw_wrap_schema=True)
    l2_human_body = _build_l2_body(kernel, raw_wrap_schema=False)

    artifacts = {
        DIST / "l1.system.md":
            stamp + l1_body.replace("@@INPUT@@", "```[INSERT BUSINESS CONTEXT HERE]```"),
        DIST / "l2.system.md":
            stamp + l2_human_body.replace("@@INPUT@@", "```[INSERT VERTICAL SPECIFICATION HERE]```"),
        EVAL_PROMPTS / "l1.eval.md":
            stamp + l1_body.replace("@@INPUT@@", "{{business_context}}"),
        EVAL_PROMPTS / "l2.eval.md":
            stamp + l2_eval_body.replace("@@INPUT@@", "{{vertical_spec}}"),
    }
    return artifacts


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile the Hormozi Operator Codex.")
    ap.add_argument("--check", action="store_true",
                    help="Verify committed artifacts match a fresh build; exit 1 if stale.")
    args = ap.parse_args()

    artifacts = render()
    stale = []
    for path, content in artifacts.items():
        existing = _read(path) if path.exists() else None
        if existing != content:
            stale.append(path.relative_to(ROOT))
        if not args.check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    if args.check:
        if stale:
            print("STALE artifacts (run `python tools/build.py`):")
            for p in stale:
                print(f"  - {p}")
            return 1
        print("Artifacts are in sync with src/.")
        return 0

    for path in artifacts:
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
