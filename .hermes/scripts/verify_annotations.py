"""T-NEW-077+ followup — local verification for the type_annotations sweep.

Mirrors the EXACT regex pair used by sasquatch's compliance auditor
(sasquatch/analysis/auditors/compliance.py:_check_type_annotations)
so we can verify progress without booting the full audit stack.

The auditor's step formula: `if ratio < 0.5: score = int(ratio * 100) else: score = 100`.
Threshold for a perfect score on the dim is 50%.

Usage:
    python3 .hermes/scripts/verify_annotations.py             # whole project
    python3 .hermes/scripts/verify_annotations.py --top 20   # top 20 files by untyped count
    python3 .hermes/scripts/verify_annotations.py --file nchantdoffice/models.py
"""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

# EXACT copies from /home/solubrew/.hermes/projects/sasquatch/sasquatch/analysis/auditors/compliance.py
TOTAL_RE = re.compile(r"^\s*(?:async\s+)?def\s+\w+\([^)]*\)\s*(?:->\s*[^:]+)?\s*:", re.MULTILINE)
TYPED_RE = re.compile(r"def\s+\w+\([^)]*\)\s*->\s*[^:\n]+:")

# Auditor's file-skip logic (same as compliance.py:266-271):
SKIP_PATH_SUBSTRINGS = ("__pycache__", ".git")
SKIP_TEST_SUBSTRINGS = ("/tests/", "/test_", "tests/")


def _is_skippable_path(path_str: str) -> bool:
    if any(s in path_str for s in SKIP_PATH_SUBSTRINGS):
        return True
    if any(s in path_str for s in SKIP_TEST_SUBSTRINGS):
        return True
    return False


def count_functions(path: Path) -> tuple[int, int]:
    """Return (total, typed) using the auditor's exact regex pair."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return (0, 0)
    total = len(TOTAL_RE.findall(content))
    typed = len(TYPED_RE.findall(content))
    return (total, typed)


def scan_project(root: Path) -> list[tuple[int, int, Path]]:
    """Return [(total, typed, path), ...] for every Python file under root
    that the auditor would count (skipping tests/, __pycache__, .git)."""
    results: list[tuple[int, int, Path]] = []
    for fp in sorted(root.rglob("*.py")):
        fp_str = str(fp)
        if _is_skippable_path(fp_str):
            continue
        t, ty = count_functions(fp)
        if t > 0:
            results.append((t, ty, fp))
    return results


def print_table(breakdown: list[tuple[int, int, Path]], top: int | None = None) -> None:
    total_funcs = sum(t for t, _, _ in breakdown)
    typed_funcs = sum(ty for _, ty, _ in breakdown)
    ratio = (typed_funcs / total_funcs) if total_funcs else 0.0
    score = int(ratio * 100) if ratio < 0.5 else 100
    threshold = "✓ ABOVE 50% threshold (perfect score)" if ratio >= 0.5 else "✗ below 50% threshold"
    print(f"OVERALL: {typed_funcs}/{total_funcs} = {ratio*100:.2f}%  -> score={score}  {threshold}\n")
    breakdown_sorted = sorted(breakdown, key=lambda r: (r[0] - r[1]), reverse=True)
    rows = breakdown_sorted if top is None else breakdown_sorted[:top]
    print(f"{'untyped':>8} {'typed':>8} {'total':>8}  path")
    for t, ty, fp in rows:
        print(f"{t-ty:>8} {ty:>8} {t:>8}  {fp}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top", type=int, default=None, help="Show only the top N files by untyped count")
    parser.add_argument("--file", type=Path, default=None, help="Scan a single file path")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root (default: cwd)")
    args = parser.parse_args()

    if args.file is not None:
        t, ty = count_functions(args.file)
        print(f"{args.file}: total={t}, typed={ty}, untyped={t-ty}")
        return 0

    breakdown = scan_project(args.root)
    print_table(breakdown, top=args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())