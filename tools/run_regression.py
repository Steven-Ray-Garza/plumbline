#!/usr/bin/env python3
"""
run_regression.py — run the private golden regression against the compiled engine.

KEY mode (ANTHROPIC_API_KEY set): the canonical Gate-1 path — build, then point promptfoo at the
private goldens (prints the command; keep outputs out of git).
KEYLESS mode (default): the orchestration-graded path — lists the goldens and prints how to run the
shadow-eval regression via the Workflow tool + tools/regression.workflow.js. No key needed.

Private goldens live under datasets/goldens/*.yaml (git-ignored). The fix is public; the data is not.
Stdlib only. Usage: python tools/run_regression.py [--goldens DIR]
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def discover(goldens_dir: Path) -> list[Path]:
    return sorted(goldens_dir.glob("*.yaml")) if goldens_dir.exists() else []


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the private golden regression.")
    ap.add_argument("--goldens", default=str(ROOT / "datasets" / "goldens"))
    args = ap.parse_args()
    gdir = Path(args.goldens)
    goldens = discover(gdir)

    if not goldens:
        print(f"No goldens under {gdir} (git-ignored). Create one: anonymize a record, then "
              f"tools/make_golden.py. See docs/COMPOUNDING.md.")
        return 0

    print(f"{len(goldens)} private golden(s) in {gdir}:")
    for g in goldens:
        print(f"  - {g.name}")

    if os.environ.get("ANTHROPIC_API_KEY"):
        print("\nANTHROPIC_API_KEY present -> canonical Gate-1 (promptfoo). Build, then run e.g.:")
        print("  python tools/build.py")
        for g in goldens:
            print(f"  npx promptfoo eval -c evals/promptfooconfig.l1.yaml --tests {g} --no-table")
        print("Keep eval outputs out of git (datasets/ is git-ignored).")
    else:
        print("\nNo ANTHROPIC_API_KEY -> keyless, orchestration-graded regression (shadow-eval).")
        print("Run the Workflow tool against the runner (it reads these goldens itself):")
        print('  Workflow({ scriptPath: "tools/regression.workflow.js" })')
        print("See docs/COMPOUNDING.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
