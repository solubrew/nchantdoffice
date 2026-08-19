"""T-NEW-169 DOC-1 -- doc updates + CLI.md section.

The card body says: update CLI.md with a `document` subcommand
section. The doc updates are a doc-only operation; this commit
ships no source changes \u2014 only doc edits + a structural
test pinning the doc shape.

The CLI.md section must:
- Describe the new `document` subcommand
- Document the `--type` argument with its choices
- Document the `--path` argument
- Show a usage example

Read the doc to confirm the shape.
"""

import re
from pathlib import Path


CLI_MD = Path(__file__).parents[1] / "CLI.md"


def _source() -> str:
    return CLI_MD.read_text()


def test_cli_md_document_section_present():
    """`CLI.md` has a section titled `### \`document\` Subcommand`
    (or close variant) describing T-NEW-169's new mode.
    """
    src = _source()
    # Heading forms accepted: any H3/H2 with `document` in it,
    # in either literal-`document` or backtick-`document`.
    has_section = bool(
        re.search(
            r"^#{2,3}\s.*[`*]?document[`*]?\s*(?:Subcommand|Single.?Doc)",
            src,
            re.MULTILINE | re.IGNORECASE,
        )
    )
    assert has_section, (
        "T-NEW-169 DOC-1: `CLI.md` must have a heading section "
        "describing the new `document` subcommand (e.g. "
        "`### \\`document\\` Subcommand` or `## Single-Document "
        "Boot`). The `--type` + `--path` arguments need a "
        "user-facing entry in the CLI reference."
    )


def test_cli_md_documents_type_argument():
    """`CLI.md` lists the `--type` argument and its 4 allowed
    values: script, notebook, image, form.
    """
    src = _source()
    has_type = "--type" in src
    # All four type names must appear in the doc body too.
    types_present = all(
        t in src.lower() for t in ("script", "notebook", "image", "form")
    )
    assert has_type and types_present, (
        "T-NEW-169 DOC-1: `CLI.md` must document `--type` and "
        "list its 4 allowed values (script, notebook, image, "
        "form). Without this the operator has no easy way to "
        "discover the dispatch names."
    )


def test_cli_md_documents_path_argument():
    """`CLI.md` lists the `--path` argument (optional file
    pre-load).
    """
    src = _source()
    has_path = "--path" in src
    assert has_path, (
        "T-NEW-169 DOC-1: `CLI.md` must document the `--path` "
        "argument for the `document` subcommand. The flag is "
        "implemented in cmds/runNchantdOffice.py but only "
        "operators reading CLI.md know it exists."
    )


def test_cli_md_documents_4_type_choices():
    """`CLI.md` lists each of the 4 doc types with a brief
    description of what each opens.

    The 4 types are the operator-approved priority list
    (LLC-RUN): script, notebook, image, form.
    """
    src = _source()
    has_script_desc = bool(
        re.search(r"^.{0,80}script.{0,80}$", src, re.MULTILINE)
    )
    has_notebook_desc = bool(
        re.search(r"^.{0,80}notebook.{0,80}$", src, re.MULTILINE)
    )
    has_image_desc = bool(
        re.search(r"^.{0,80}image.{0,80}$", src, re.MULTILINE)
    )
    has_form_desc = bool(
        re.search(r"^.{0,80}form.{0,80}$", src, re.MULTILINE)
    )
    assert all(
        [has_script_desc, has_notebook_desc, has_image_desc, has_form_desc]
    ), (
        f"T-NEW-169 DOC-1: `CLI.md` must describe each of the 4 "
        f"doc types (script, notebook, image, form). Found: "
        f"script={has_script_desc}, notebook={has_notebook_desc}, "
        f"image={has_image_desc}, form={has_form_desc}."
    )


def test_cli_md_documents_full_default_behavior():
    """`CLI.md` still describes the default (no-subcommand) behavior
    — the new `document` subcommand must NOT replace it.

    Pre-fix `CLI.md` documented `scratch` / `continue` / default
    (wizard) which were never actually wired (pre-existing
    doc-vs-reality drift, T-NEW-164 category). Post-fix the
    documented behaviour must match reality: no-subcommand boots
    the full main app (unchanged).
    """
    src = _source()
    # Acceptable clauses: a section that says the launch with no
    # subcommand boots the full main app / NchantdOfficeCloak /
    # unchanged from before. Use a more permissive regex than
    # word-pattern matching -- the canonical phrasing varies.
    has_default = bool(
        re.search(
            r"(?:default|no[\s-]*subcommand|without any)\s*(?:launch|behavi(?:our|or))|unchanged|boots?\s+(?:the\s+(?:full|main|unchanged)|\s*NchantdOfficeCloak)|full\s+NchantdOfficeCloak",
            src,
            re.IGNORECASE,
        )
    )
    assert has_default, (
        "T-NEW-169 DOC-1: `CLI.md` must describe the default "
        "(no-subcommand) behaviour — booting the full main "
        "app unchanged. The new `document` subcommand ADDS to "
        "the existing CLI surface; it does not replace it."
    )
