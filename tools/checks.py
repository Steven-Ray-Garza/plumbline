#!/usr/bin/env python3
"""
checks.py — Tier-1 deterministic gates for plumbline.

Zero tokens, no network, runs in seconds. Each check returns (name, ok, detail).
Run as a script (`python tools/checks.py`) for CI, or import the functions from pytest.

Gates (12 checks in ALL_CHECKS; gate 4 = XML balance runs separately for L1 and L2):
  1. L1 has no unresolved build sentinels.
  2. L2 exposes all six L1 slot tokens (the schema) and resolved its own build tokens.
  3. Kernel parity: both artifacts stamp the same sha256, equal to src/kernel.md.
  4. XML tag balance in both prompts (L2's embedded L1 schema treated as opaque).
  5. No reasoning-extraction imperatives ("show/echo/output your reasoning", ...).
  6. The conclusions-with-evidence hygiene line is present.
  7. The agnosticism guardrails (default-off + transfer rule) survived into both prompts.
  8. promptfoo configs are valid and reference files that exist.
  9. No code-executing assertion types run in the (key-bearing) eval suite (R1 exec-path policy).
 10. The adversarial security suite is wired in and judge-hardened (R2 blocking guarantee).
 11. The shipped L1 contains no known vertical-specific example (leak regression guard).
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SRC = ROOT / "src"
EVALS = ROOT / "evals"

L1 = DIST / "l1.system.md"
L2 = DIST / "l2.system.md"

L1_TAGS = ["role", "operating_standards", "knowledge", "background",
           "process", "output_format", "uncertainty", "scope", "examples"]
L2_TAGS = ["role", "knowledge", "input_contract", "generation_protocol",
           "l1_template", "output_format", "scope", "bonus_module"]

SLOT_TOKENS = ["@@ROLE@@", "@@BACKGROUND@@", "@@ACTIVE_MODULES@@",
               "@@QUALIFICATION@@", "@@EXAMPLES@@", "@@LEXICON@@"]
BUILD_TOKENS = ["@@KERNEL@@", "@@L1_TEMPLATE@@", "@@INPUT@@"]

BANNED = [
    r"\bshow your (?:chain[- ]of[- ]thought|chain of thought|thinking|reasoning)\b",
    r"\becho your (?:reasoning|thinking|chain of thought)\b",
    r"\brepeat your (?:reasoning|thinking)\b",
    r"\boutput your (?:chain of thought|reasoning|thinking)\b",
    r"\breveal your (?:internal )?(?:reasoning|thinking)\b",
    r"\btranscribe your (?:reasoning|thinking)\b",
]
HYGIENE = "do not narrate your internal reasoning"
GUARDRAILS = [
    "default state of every consumer-specific mechanic",
    "is OFF",
    "library, not a checklist",
    "VSL", "affiliate", "Veblen", "Paid Ads",
]

# ---- R1 exec-path policy. We parse the eval YAML structurally (not by line regex) so that
# flow-style assertions ({type: javascript}) are caught and adversarial block-scalar prose that
# merely *mentions* "type: python" is NOT a false positive. Only these extensions may sit behind a
# file:// — an ALLOWLIST, so .mjs/.cjs/.ts/.wasm and friends cannot slip through a .js|.py denylist.
EVAL_DATA_EXTS = {".yaml", ".yml", ".json", ".txt", ".md"}
CODEEXEC_TYPES = {"javascript", "python"}

# ---- R2: the adversarial security suite must stay present + hardened.
SECURITY_CASES = EVALS / "tests" / "security_cases.yaml"
SECURITY_CONFIG = EVALS / "promptfooconfig.security.yaml"
HARDENING_MARKER = "UNTRUSTED DATA"
REQUIRED_SECURITY_TAGS = ["LLM01", "judge-robustness"]  # plus LLM02 OR LLM07 (leakage)

# ---- Known vertical-specific EXAMPLE phrases that must not appear in the shipped L1's fixed
# scaffolding (which L2 reproduces into every vertical — e.g. a procurement bid-loser example leaking
# into a med-spa instance). This is a narrow REGRESSION tombstone for the KNOWN leak, NOT a proof of
# neutrality: it is substring-evadable by design. Broad domain-neutrality is a SEMANTIC property
# checked by the model-graded L2 eval rubric — which is intentionally ADVISORY (Tier-2, non-blocking),
# because model-graded gates must not be merge-blocking (R2). So neutrality beyond these literals is
# MONITORED, not hard-gated — a deliberate trade-off, not an oversight. Library mechanic names
# (VSL/affiliate/Veblen/Paid Ads) are intentionally NOT listed: they may legitimately appear in
# neutral guidance, so listing them would false-positive.
SCAFFOLD_LEAK_TOKENS = ["ACA-framework", "lost recent bids"]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _norm(text: str) -> str:
    """Collapse all whitespace runs to single spaces (robust to line wrapping)."""
    return " ".join(text.split())


def _iter_dicts(node):
    """Yield every dict in a parsed-YAML structure (depth-first)."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _iter_dicts(v)
    elif isinstance(node, list):
        for v in node:
            yield from _iter_dicts(v)


def _iter_strings(node):
    """Yield every string *value* in a parsed-YAML structure (dict keys are not yielded)."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for v in node.values():
            yield from _iter_strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _iter_strings(v)


def _balance(text: str, tags: list[str]) -> list[str]:
    """Balance only BLOCK-LEVEL tags — those alone on their own line. Inline references to a tag
    inside prose (e.g. 'see <uncertainty>') are intentionally not counted."""
    problems = []
    for tag in tags:
        opens = len(re.findall(rf"(?m)^\s*<{tag}(?:\s[^>]*)?>\s*$", text))
        closes = len(re.findall(rf"(?m)^\s*</{tag}>\s*$", text))
        if opens != closes:
            problems.append(f"<{tag}> {opens} open / {closes} close")
        elif opens == 0:
            problems.append(f"<{tag}> missing")
    return problems


def _strip_embedded_l1(l2_text: str) -> str:
    """Treat the embedded L1 schema as opaque so only the OUTER L2 structure is balanced.
    Excise from the block-level <l1_template> line through the block-level </l1_template> line."""
    return re.sub(r"(?ms)^\s*<l1_template>\s*$.*?^\s*</l1_template>\s*$",
                  "<l1_template>\n</l1_template>", l2_text)


def _kernel_hash() -> str:
    return hashlib.sha256(_read(SRC / "kernel.md").encode("utf-8")).hexdigest()[:16]


def _stamped_hash(text: str) -> str | None:
    m = re.search(r"kernel-sha256:\s*([0-9a-f]{16})", text)
    return m.group(1) if m else None


def _eval_yaml_files() -> list[Path]:
    """All YAML files under evals/, case-insensitive on extension (so .YAML/.YML are not a
    Windows-vs-Linux blind spot)."""
    return sorted(p for p in EVALS.rglob("*")
                  if p.is_file() and p.suffix.lower() in {".yaml", ".yml"})


# ---- checks -----------------------------------------------------------------

def check_l1_sentinels_resolved():
    text = _read(L1)
    left = [t for t in re.findall(r"@@[A-Z_]+@@", text)]
    return ("L1 sentinels resolved", not left,
            "clean" if not left else f"unresolved: {sorted(set(left))}")


def check_l2_schema_slots():
    text = _read(L2)
    missing = [s for s in SLOT_TOKENS if s not in text]
    leaked = [b for b in BUILD_TOKENS if b in text]
    ok = not missing and not leaked
    detail = "all six slots exposed; build tokens resolved"
    if not ok:
        detail = f"missing slots: {missing}; leaked build tokens: {leaked}"
    return ("L2 exposes L1 schema slots", ok, detail)


def check_kernel_parity():
    expected = _kernel_hash()
    h1, h2 = _stamped_hash(_read(L1)), _stamped_hash(_read(L2))
    ok = h1 == expected and h2 == expected
    return ("Kernel parity (L1 == L2 == src)", ok,
            f"src={expected} l1={h1} l2={h2}")


def check_l1_xml_balance():
    problems = _balance(_read(L1), L1_TAGS)
    return ("L1 XML balance", not problems, "balanced" if not problems else "; ".join(problems))


def check_l2_xml_balance():
    problems = _balance(_strip_embedded_l1(_read(L2)), L2_TAGS)
    return ("L2 XML balance", not problems, "balanced" if not problems else "; ".join(problems))


def check_banned_phrases():
    hits = []
    for label, p in [("L1", L1), ("L2", L2)]:
        text = _read(p).lower()
        for pat in BANNED:
            if re.search(pat, text):
                hits.append(f"{label}: /{pat}/")
    return ("No reasoning-extraction imperatives", not hits,
            "clean" if not hits else "; ".join(hits))


def check_hygiene_line():
    missing = [lbl for lbl, p in [("L1", L1), ("L2", L2)] if HYGIENE not in _read(p).lower()]
    return ("Conclusions-with-evidence hygiene present", not missing,
            "present in both" if not missing else f"missing in: {missing}")


def check_guardrails():
    miss = []
    for lbl, p in [("L1", L1), ("L2", L2)]:
        text = _norm(_read(p)).lower()
        for g in GUARDRAILS:
            if _norm(g).lower() not in text:
                miss.append(f"{lbl}:'{g}'")
    return ("Agnosticism guardrails survived", not miss,
            "default-off + transfer rule intact" if not miss else f"missing: {miss}")


def check_promptfoo_configs():
    try:
        import yaml  # noqa
    except Exception:
        return ("promptfoo config integrity", True, "skipped (pyyaml not installed)")
    import yaml
    problems = []
    configs = sorted(EVALS.glob("promptfooconfig*.y*ml"))
    if not configs:
        return ("promptfoo config integrity", False, "no promptfooconfig*.yaml found")
    for cfg in configs:
        data = yaml.safe_load(_read(cfg))
        base = cfg.parent
        refs = []
        for pr in data.get("prompts", []) or []:
            if isinstance(pr, str) and pr.startswith("file://"):
                refs.append(pr[len("file://"):])
        t = data.get("tests")
        for item in (t if isinstance(t, list) else [t]):
            if isinstance(item, str) and item.startswith("file://"):
                refs.append(item[len("file://"):])
        for r in refs:
            if not (base / r).exists():
                problems.append(f"{cfg.name} -> missing {r}")
        provs = data.get("providers", []) or []
        ids = [p.get("id", "") if isinstance(p, dict) else str(p) for p in provs]
        if not any("anthropic:messages:" in i for i in ids):
            problems.append(f"{cfg.name} -> no anthropic:messages: provider")
    return ("promptfoo config integrity", not problems,
            f"{len(configs)} config(s) ok" if not problems else "; ".join(problems))


def check_no_codeexec_assertions():
    """R1 (structural): no code-executing assertion surface anywhere in the eval suite — no assertion
    `type: javascript|python`, no `transform:` key, and no `file://` value whose target extension is
    outside the data allowlist. YAML is parsed, so flow-style ({type: python}) is caught and
    block-scalar prose that merely mentions those tokens is not a false positive. Fails closed if
    pyyaml is unavailable (a security gate must not silently skip)."""
    try:
        import yaml
    except Exception:
        return ("No code-exec assertions in eval suite", False,
                "pyyaml required for the structural code-exec check (pip install -r requirements.txt)")
    problems = []
    for f in _eval_yaml_files():
        try:
            rel = f.relative_to(ROOT).as_posix()
        except ValueError:
            rel = f.as_posix()
        try:
            docs = list(yaml.safe_load_all(_read(f)))
        except Exception as e:
            problems.append(f"{rel}: unparseable YAML ({e.__class__.__name__})")
            continue
        for doc in docs:
            for d in _iter_dicts(doc):
                t = d.get("type")
                if isinstance(t, str) and t.strip().lower() in CODEEXEC_TYPES:
                    problems.append(f"{rel}: assertion type '{t.strip().lower()}'")
                if "transform" in d and d.get("transform") not in (None, ""):
                    problems.append(f"{rel}: 'transform' (executable) present")
            for s in _iter_strings(doc):
                if s.startswith("file://"):
                    target = s[len("file://"):].split("?")[0].split("#")[0]
                    if Path(target).suffix.lower() not in EVAL_DATA_EXTS:
                        problems.append(f"{rel}: file:// non-data target '{s}'")
    return ("No code-exec assertions in eval suite", not problems,
            "no javascript/python/transform/exec-file:// in eval YAML"
            if not problems else "; ".join(problems))


def check_security_suite_wired():
    """R2 (structural): the adversarial security suite must exist, parse, carry >=3 real cases with
    assertions, be tagged (LLM01, LLM02|LLM07, judge-robustness) in case descriptions, be
    judge-hardened (the UNTRUSTED DATA marker inside an actual llm-rubric value), and be wired via the
    config's `tests:` field. Structural so comment-only magic strings cannot game it. Fails closed
    without pyyaml. This is the BLOCKING Tier-1 guarantee that the (otherwise advisory) security tier
    cannot be silently deleted, gutted, or unwired."""
    try:
        import yaml
    except Exception:
        return ("Security suite wired (Tier-1 blocking)", False, "pyyaml required for this check")
    problems = []
    if not SECURITY_CASES.exists():
        problems.append("missing evals/tests/security_cases.yaml")
    if not SECURITY_CONFIG.exists():
        problems.append("missing evals/promptfooconfig.security.yaml")
    if not problems:
        try:
            cases = yaml.safe_load(_read(SECURITY_CASES))
        except Exception as e:
            cases = None
            problems.append(f"security_cases.yaml unparseable ({e.__class__.__name__})")
        if isinstance(cases, list):
            real = [c for c in cases if isinstance(c, dict) and c.get("assert")]
            if len(real) < 3:
                problems.append(f">=3 real cases with assertions required, found {len(real)}")
            descs = " ".join(str(c.get("description", "")) for c in real)
            for tag in REQUIRED_SECURITY_TAGS:
                if tag not in descs:
                    problems.append(f"no case description tagged '{tag}'")
            if "LLM02" not in descs and "LLM07" not in descs:
                problems.append("no case description tagged 'LLM02'/'LLM07' (leakage)")
            rubric_vals = [str(a.get("value", "")) for c in real for a in (c.get("assert") or [])
                           if isinstance(a, dict) and str(a.get("type", "")).strip() == "llm-rubric"]
            if not any(HARDENING_MARKER in v for v in rubric_vals):
                problems.append(f"no llm-rubric carries the hardening marker '{HARDENING_MARKER}'")
        elif cases is not None:
            problems.append("security_cases.yaml is not a list of cases")
        try:
            cfg = yaml.safe_load(_read(SECURITY_CONFIG)) or {}
        except Exception as e:
            cfg = {}
            problems.append(f"promptfooconfig.security.yaml unparseable ({e.__class__.__name__})")
        tests = cfg.get("tests")
        tests_str = tests if isinstance(tests, str) else " ".join(str(t) for t in (tests or []))
        if "security_cases.yaml" not in tests_str:
            problems.append("config 'tests:' does not reference security_cases.yaml")
    return ("Security suite wired (Tier-1 blocking)", not problems,
            "security tier present, parsed, tagged, hardened, wired"
            if not problems else "; ".join(problems))


def check_scaffolding_no_known_leak():
    """Regression guard: the SHIPPED L1 (dist/l1.system.md) must not contain a KNOWN vertical-specific
    example phrase (the procurement bid-loser example that previously leaked into med-spa instances via
    L2's verbatim reproduction of the fixed scaffolding). Scans the compiled artifact, which folds in
    ALL origins — src/l1.template.md, the build.py slot defaults, and the injected kernel — so a leak
    from any origin surfaces here; the build-sync gate (test_build_is_in_sync / build.py --check)
    guarantees dist reflects current sources. Whitespace-normalized so line-wrapped phrases match.
    NOTE: a denylist catches KNOWN leaks only — broad neutrality is the advisory L2 eval rubric's job."""
    text = _norm(_read(L1)).lower()
    hits = [t for t in SCAFFOLD_LEAK_TOKENS if _norm(t).lower() in text]
    return ("L1 scaffolding: no known vertical leak", not hits,
            "no known vertical-specific example in shipped L1" if not hits
            else f"known vertical-leak phrase in dist/l1.system.md: {hits}")


ALL_CHECKS = [
    check_l1_sentinels_resolved,
    check_l2_schema_slots,
    check_kernel_parity,
    check_l1_xml_balance,
    check_l2_xml_balance,
    check_banned_phrases,
    check_hygiene_line,
    check_guardrails,
    check_promptfoo_configs,
    check_no_codeexec_assertions,
    check_security_suite_wired,
    check_scaffolding_no_known_leak,
]


def run_all():
    results = [fn() for fn in ALL_CHECKS]
    width = max(len(name) for name, _, _ in results)
    failed = 0
    for name, ok, detail in results:
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{mark}] {name.ljust(width)}  {detail}")
    print(f"\n{len(results) - failed}/{len(results)} checks passed.")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
