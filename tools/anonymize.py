#!/usr/bin/env python3
"""
anonymize.py — strip PII from a private L0 intake record so it can seed a shareable golden.

Records (see src/l0.schema.md) are private: they live under datasets/intake/, which is git-ignored.
This removes Group-0 PII (business_id / name and obvious contact fields), substitutes the business
name throughout the record with a STABLE pseudonym (same input -> same output, so cross-record links
survive), and optionally rounds money figures — keeping inferred_axes and the business_context blob
intact for golden creation (tools/make_golden.py).

NOT a guarantee: free-text scrubbing is best-effort (it can only replace names it is told about via the
PII fields); review the output before sharing. Stdlib + pyyaml (pyyaml only for the CLI).

Usage:
    python tools/anonymize.py datasets/intake/<record>.yaml [--out FILE] [--round]
"""
from __future__ import annotations

import argparse
import hashlib
import math
import re
import sys
from pathlib import Path

# Group-0 PII keys (and obvious contact fields) removed outright.
PII_KEYS = {"business_id", "business_name", "owner", "owner_name", "contact",
            "email", "phone", "address", "url", "website"}


def pseudonym(name: str) -> str:
    """Stable pseudonym from a name — same input always maps to the same output."""
    h = hashlib.sha256(name.strip().lower().encode("utf-8")).hexdigest()[:8]
    return f"business-{h}"


def _round_token(tok: str) -> str:
    """'$1,234.50' / '$12k' -> rounded to 2 significant figures, magnitude preserved."""
    raw = tok.lstrip("$").replace(",", "")
    mult = 1
    if raw.lower().endswith("k"):
        mult, raw = 1000, raw[:-1]
    try:
        val = float(raw) * mult
    except ValueError:
        return tok
    if val == 0:
        return tok
    factor = 10 ** (math.floor(math.log10(abs(val))) - 1)  # keep 2 significant figures
    return "$" + format(int(round(val / factor) * factor), ",")


def round_money(text: str) -> str:
    return re.sub(r"\$[\d,]+(?:\.\d+)?k?", lambda m: _round_token(m.group(0)), text, flags=re.I)


def _scrub_text(text: str, names: list[str], *, round_numbers: bool) -> str:
    out = text
    for n in sorted((n for n in names if n and n.strip()), key=len, reverse=True):
        out = re.sub(re.escape(n), "[BUSINESS]", out, flags=re.I)
    return round_money(out) if round_numbers else out


def anonymize(record: dict, *, round_numbers: bool = False) -> dict:
    """Return a PII-stripped copy of an L0 intake record."""
    rec = dict(record)
    names = [rec.pop(k) for k in list(rec) if k.lower() in PII_KEYS]
    names = [n for n in names if isinstance(n, str)]
    rec["business_id"] = pseudonym(names[0]) if names else "business-anon"
    if isinstance(rec.get("business_context_blob"), str):
        rec["business_context_blob"] = _scrub_text(rec["business_context_blob"], names,
                                                   round_numbers=round_numbers)
    ra = rec.get("raw_answers")
    if isinstance(ra, dict):
        for cell in ra.values():
            if isinstance(cell, dict) and isinstance(cell.get("value"), str):
                cell["value"] = _scrub_text(cell["value"], names, round_numbers=round_numbers)
    rec["_anonymized"] = True
    return rec


def main() -> int:
    import yaml
    ap = argparse.ArgumentParser(description="Strip PII from an L0 intake record.")
    ap.add_argument("record")
    ap.add_argument("--out")
    ap.add_argument("--round", action="store_true", help="also round money figures to 2 sig figs")
    args = ap.parse_args()
    rec = yaml.safe_load(Path(args.record).read_text(encoding="utf-8"))
    out = yaml.safe_dump(anonymize(rec, round_numbers=args.round), sort_keys=False, allow_unicode=True)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
