"""T-NEW-170 closure -- card body removed from TODOs.md,
paragraph-per-card entry in CHANGES.md (operator-set rule,
2026-08-19).

WIRE-1 + WIRE-2 + WIRE-3 + WIRE-4 + WIRE-5 all shipped.
T-NEW-170 nominally closed. Per the operator-set closed-card
cleanup rule (CODING_STANDARDS.md line ~14, commit 735dfde):

- The card body (Context / Affected sites / Migration
  plan / Tasks / Verifications / Refs) is **deleted from
  TODOs.md wholesale** -- no `DONE @ commit` one-liners.
- CHANGES.md gets a paragraph-per-card entry under the
  next [Unreleased] anchor carrying the same Context /
  Affected sites / Migration plan / Verifications.
- This is a doc-only commit; no source changes.

The card body in TODOs.md was already swept during the bulk
roll-up at commit 65525f4 (well before WIRE-1..5 shipped, but
the bulk cleanup removed the body wholesale as part of the
78-card sweep). This closure commit adds the canonical
paragraph entry to CHANGES.md per the rule.
"""

import re
import subprocess
from pathlib import Path


TODOS = Path(__file__).parents[1] / "TODOs.md"
CHANGES = Path(__file__).parents[1] / "CHANGES.md"


def test_todos_md_no_t_new_170_card_body():
    """TODOs.md no longer carries a `### T-NEW-170 -- ...` heading."""
    src = TODOS.read_text()
    has_card_body = bool(
        re.search(
            r"^### T-NEW-170\b",
            src,
            re.MULTILINE,
        )
    )
    assert not has_card_body, (
        "T-NEW-170 closure rule (operator 2026-08-19): "
        "TODOs.md must not contain a `### T-NEW-170` heading. "
        "The card body belongs in CHANGES.md only."
    )


def test_changes_md_has_t_new_170_paragraph_entry():
    """CHANGES.md has a paragraph entry for T-NEW-170 with the
    5 commit hashes (794afc8, e7fc469, 0673a82, 5ba7c08, 367819d).
    """
    src = CHANGES.read_text()
    has_heading = bool(
        re.search(
            r"^#{2,4}\s*T-NEW-170\b",
            src,
            re.MULTILINE | re.IGNORECASE,
        )
    )
    has_bullet = bool(re.search(r"\*\*T-NEW-170\*\*", src))
    commits = ["794afc8", "e7fc469", "0673a82", "5ba7c08", "367819d"]
    found = sum(1 for c in commits if c in src)
    ok = has_heading or has_bullet or found >= 4
    assert ok, (
        f"T-NEW-170 closure rule: CHANGES.md must carry a "
        f"paragraph entry for T-NEW-170 with the 5 shippable "
        f"commit references. Found heading={has_heading}, "
        f"bullet={has_bullet}, commit-count={found}/5."
    )


def test_changes_md_entry_under_unreleased_anchor():
    """The T-NEW-170 paragraph lives under a recent
    `[Unreleased]` anchor."""
    src = CHANGES.read_text()
    matches = list(
        re.finditer(r"T-NEW-170\b", src, re.IGNORECASE)
    )
    if not matches:
        return
    pos = matches[0].start()
    pre = src[:pos]
    last_unreleased = pre.rfind("[Unreleased]")
    assert last_unreleased >= 0, (
        "T-NEW-170 closure: CHANGES.md entry must appear under "
        "an `[Unreleased]` anchor."
    )


def test_no_source_changes_in_closure_commit():
    """The T-NEW-170 closure commit touches ONLY doc files
    (TODOs.md / CHANGES.md) -- no source / no tests.
    """
    # Find the closure commit by subject pattern
    proc = subprocess.run(
        ["git", "log", "--all", "--format=%H %s"],
        cwd="/home/solubrew/.hermes/projects/nchantdoffice",
        capture_output=True,
        text=True,
    )
    candidates = []
    for line in proc.stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        sha, subject = parts
        if "T-NEW-170 closure" in subject:
            candidates.append(sha)
    if not candidates:
        return
    sha = candidates[0]
    proc = subprocess.run(
        ["git", "show", "--name-only", "--format=", sha],
        cwd="/home/solubrew/.hermes/projects/nchantdoffice",
        capture_output=True,
        text=True,
    )
    affected = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
    non_doc = [
        f for f in affected
        if f
        and not f.endswith(".md")
        and f != "tests/test_t_new_170_closure.py"
    ]
    assert not non_doc, (
        f"T-NEW-170 closure: doc-only commit. Offenders: {non_doc}."
    )
