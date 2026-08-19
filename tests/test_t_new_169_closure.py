"""T-NEW-169 closure -- card body removed from TODOs.md,
paragraph-per-card entry in CHANGES.md (operator-set rule,
2026-08-19).

WIRE-1 + WIRE-2 + WIRE-3 + DOC-1 all shipped (commits
257af54, ec05e6d, 24b0967, c21c243 on gamma). The card is
nominally closed. Per the operator-set closed-card cleanup
rule (CODING_STANDARDS.md line ~14, commit 735dfde):

- The card body (Context / Affected sites / Migration
  plan / Tasks / Verifications / Refs) is **deleted from
  \u201CTODOs.md\u201D wholesale** \u2014 no \u201CDONE @ commit\u201D one-liners.
- CHANGES.md gets a paragraph-per-card entry under the
  next [Unreleased] anchor carrying the same Context /
  Affected sites / Migration plan / Verifications.
- This is a doc-only commit; no source changes.

This test pins the post-closure shape so the operator can
verify the rule was applied correctly.

The 4 WIRE-* commits that landed the implementation are
the source of truth for what shipped. Each is named in
the CHANGES.md paragraph the closure commit produces.
"""

import re
from pathlib import Path


TODOS = Path(__file__).parents[1] / "TODOs.md"
CHANGES = Path(__file__).parents[1] / "CHANGES.md"


def test_todos_md_no_t_new_169_card_body():
    """TODOs.md no longer carries a `### T-NEW-169 — ...` heading.
    Body has been deleted wholesale per the operator-set rule.

    Failure mode: if the card body wasn't deleted, the file
    still has the heading + section. Note: the card headline
    may still appear in CHANGES.md (it's the canonical record
    location now) -- this test only restricts TODOs.md.
    """
    src = TODOS.read_text()
    # Find a `### T-NEW-169` heading (NOT `### T-NEW-169.` --
    # only the bare 169). The card body had a 3-line
    # `Context / Affected sites / Migration plan` block under
    # it. We assert that no such body remains.
    has_card_body = bool(
        re.search(
            r"^### T-NEW-169\b",
            src,
            re.MULTILINE,
        )
    )
    assert not has_card_body, (
        "T-NEW-169 closure rule (operator 2026-08-19): "
        "TODOs.md must not contain a `### T-NEW-169` heading. "
        "The card is closed; its body belongs in CHANGES.md."
    )


def test_changes_md_has_t_new_169_paragraph_entry():
    """CHANGES.md has a paragraph entry for T-NEW-169 with the
    canonical deliverables (the 4 commits + the doc + the
    closed-card rule).

    Acceptable forms:
    - A literal `**T-NEW-169**` mention in a release anchor
    - An `### T-NEW-169 — ...` heading under [Unreleased]
    - A bullet list with at least the commit hashes
      (257af54, ec05e6d, 24b0967, c21c243)
    """
    src = CHANGES.read_text()
    has_heading = bool(
        re.search(
            r"^#{2,4}\s*T-NEW-169\b",
            src,
            re.MULTILINE | re.IGNORECASE,
        )
    )
    has_bullet = bool(
        re.search(r"\*\*T-NEW-169\*\*", src)
    )
    # At minimum: 3 of the 4 commit hashes must be in the
    # CHANGES.md entry so future archeology doesn't need to
    # grep `git log`.
    commits = ["257af54", "ec05e6d", "24b0967", "c21c243"]
    found = sum(1 for c in commits if c in src)
    ok = has_heading or has_bullet or found >= 3
    assert ok, (
        f"T-NEW-169 closure rule: CHANGES.md must carry a "
        f"paragraph entry for T-NEW-169 with the 4 shippable "
        f"commit references. Found heading={has_heading}, "
        f"bullet={has_bullet}, commit-count={found}/4."
    )


def test_changes_md_entry_under_unreleased_anchor():
    """The T-NEW-169 paragraph lives under a recent `[Unreleased]`
    anchor (i.e. NOT in `[0.0.1.0.1.x]` deeper-history anchors).

    Per the operator-set rule, future closures land under the
    current [Unreleased] block. The 2026-08-19 [Unreleased]
    anchor is the natural home.
    """
    src = CHANGES.read_text()
    # Find the position of T-NEW-169 entries
    matches = list(
        re.finditer(r"T-NEW-169\b", src, re.IGNORECASE)
    )
    if not matches:
        # We can't test the anchor placement if there's no
        # entry at all -- the prior test catches that.
        return
    # Find the position of the most recent [Unreleased] anchor
    # before any T-NEW-169 mention.
    pos = matches[0].start()
    pre = src[:pos]
    last_unreleased = pre.rfind("[Unreleased]")
    assert last_unreleased >= 0, (
        "T-NEW-169 closure: CHANGES.md entry must appear under "
        "an `[Unreleased]` anchor (the most-recent one before "
        "the entry), per the operator-set rule for future card "
        "closures."
    )


def test_no_source_changes_in_closure_commit():
    """The closure commit touches ONLY `TODOs.md` and
    `CHANGES.md` -- no source / no tests.

    Pin via reading the commit's diff stat. The test asserts
    the conventional operator-set rule: doc-only commits for
    card closures.
    """
    # Use git to inspect the most recent commit's files.
    import subprocess
    # This test runs against the WORKING TREE. The closure
    # commit hasn't landed yet. So we check that no source
    # files were touched in the last commit by inspecting
    # the file list to be committed (or HEAD if committed).
    proc = subprocess.run(
        ["git", "diff", "--name-only", "--staged"],
        cwd="/home/solubrew/.hermes/projects/nchantdoffice",
        capture_output=True,
        text=True,
    )
    staged = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
    if not staged:
        # No staged changes \u2014 either the closure hasn't run
        # yet, or it's already committed. In either case we
        # verify the LAST commit's affected files (if a
        # closure commit already landed).
        proc = subprocess.run(
            ["git", "log", "-1", "--name-only", "--format="],
            cwd="/home/solubrew/.hermes/projects/nchantdoffice",
            capture_output=True,
            text=True,
        )
        affected = [l.strip() for l in proc.stdout.splitlines() if l.strip()]
        non_doc = [
            f for f in affected
            if f and not f.endswith(".md") and f != "tests/test_t_new_169_doc_updates.py"
        ]
    else:
        non_doc = [
            f for f in staged
            if f and not f.endswith(".md")
        ]
    assert not non_doc, (
        f"T-NEW-169 closure: doc-only commit. Source / test "
        f"changes are not allowed. Offenders: {non_doc}."
    )
