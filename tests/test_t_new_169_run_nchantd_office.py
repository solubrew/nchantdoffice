"""T-NEW-169 WIRE-1 -- argparse dispatch in cmds/runNchantdOffice.py.

The T-NEW-169 plan calls for `runNchantdOffice.py` to support:

  python runNchantdOffice.py document --type <name> [--path <file>]
      > standalone 2-pane minimal shell (DECIDE-2 (b): keep the
        tabset chrome with one tab). Hardware: argparse subcommand.

  python runNchantdOffice.py  # no subcommand
      > unchanged, full main-app behaviour (NchantdOfficeCloak)

This commit ships ONLY the argparse scaffold + dispatch (WIRE-1).
WIRE-2 (NchantdDocumentStandaloneWindow class) ships later once
the standalone shell is needed. WIRE-3 (per-type instantiations)
ships after WIRE-2.

Tests are AST-source structural (mirroring the T-NEW-167..170
pattern). `cmds/runNchantdOffice.py` can't be imported in tests
because it boots Qt and writes config on module load (see the
`write_default_config()` call near the top of the file). AST
inspection + reading the source as a string is the only safe path.
"""

import ast
import re
from pathlib import Path


RUN_FILE = Path(__file__).parents[1] / "cmds/runNchantdOffice.py"


def _source() -> str:
    return RUN_FILE.read_text()


def test_argparse_import():
    """`import argparse` (or `from argparse import ...`) is present."""
    src = _source()
    ok = re.search(r"^import\s+argparse\b", src, re.MULTILINE) is not None or re.search(
        r"^from\s+argparse\b", src, re.MULTILINE
    ) is not None
    assert ok, (
        "cmds/runNchantdOffice.py must import argparse to support "
        "`runNchantdOffice.py document --type <name>`. T-NEW-169 "
        "WIRE-1."
    )


def test_subparsers_add_document():
    """`parser.add_subparsers()` + `add_parser('document', ...)` is wired."""
    src = _source()
    has_subparsers = "add_subparsers" in src
    has_document_sub = bool(
        re.search(r"""add_parser\(\s*['"]document['"]""", src)
    )
    assert has_subparsers and has_document_sub, (
        "T-NEW-169 WIRE-1: cmds/runNchantdOffice.py must have "
        "`parser.add_subparsers()` + `group.add_parser('document')`. "
        "The current file has neither -- pre-fix it forwards the raw "
        "argv list straight to nchantment() which expects a dict, so "
        "the subcommand never takes effect."
    )


def test_four_high_value_doc_types_in_dispatch():
    """The dispatch table mentions all 4 high-value doc types."""
    src = _source()
    has_script = '"script"' in src or "'script'" in src
    has_notebook = '"notebook"' in src or "'notebook'" in src
    has_image = '"image"' in src or "'image'" in src
    has_form = '"form"' in src or "'form'" in src
    assert all([has_script, has_notebook, has_image, has_form]), (
        "T-NEW-169 WIRE-1: the doc-type dispatch table must mention "
        "all 4 of: script, notebook, image, form. WIRE-3 will wire "
        "these to the NchantdOffice* concrete classes; WIRE-1 only "
        "needs them present so the type names are recognized."
    )


def test_run_function_routes_on_mode():
    """`run(args)` reads the dispatch and routes based on `mode`.

    The pre-fix bug: `run(argv)` passed the raw argv list to
    `nchantment()`; `nchantment()` does `'instance' in args` which
    on a list returns False; the launch silently took the main-app
    branch every time.

    Post-fix: `run(args)` builds the dispatch dict, sees `mode`,
    and routes to either the standalone path or the main-app path.
    """
    src = _source()
    has_mode_read = (
        re.search(r"""args\[['"]mode['"]\]""", src) is not None
        or re.search(r"""\bargs\.get\(\s*['"]mode['"]""", src) is not None
    )
    has_dispatch_branch = (
        # variable form: if mode == "main": or if mode == "document":
        re.search(r"""if\s+mode\s*[=!]=\s*['"]main['"]""", src) is not None
        or re.search(r"""if\s+mode\s*[=!]=\s*['"]document['"]""", src) is not None
        # dict-key form: if args["mode"] == "..."
        or re.search(
            r"""if\s+args\[['"]mode['"]\]\s*[=!]=\s*['"](main|document)['"]""",
            src,
        ) is not None
    )
    assert has_mode_read and has_dispatch_branch, (
        "T-NEW-169 WIRE-1: `run(...)` must read `args['mode']` (or "
        "`args.get('mode')`) and route based on `mode == 'main'` "
        "or `mode == 'document'` branches. Pre-fix the function "
        "blindly forwarded argv to nchantment() and never branched "
        "on it -- `'instance' in <list>` is always False."
    )


def test_run_function_calls_build_dispatch_somewhere():
    """`_build_dispatch(...)` is invoked somewhere in the file's
    execution path so the parsed-dict shape actually materialises.

    Pre-fix the file had no argparse at all; `run(argv)` was called
    directly and the argv list was handed off unchanged. Post-fix
    argv must pass through `_build_dispatch` so `args['mode']`
    becomes meaningful.

    Acceptable call sites: inside `run()` (cleanest), inside the
    `__main__` block (also fine -- `run(_build_dispatch(argv))`),
    or anywhere else in the file. The contract is just that
    `_build_dispatch(argv)` is reached at launch time.
    """
    src = _source()
    has_helper_def = re.search(
        r"^def\s+_build_dispatch\(", src, re.MULTILINE
    ) is not None
    has_call_with_argv = bool(
        re.search(r"""_build_dispatch\(\s*argv\b""", src)
    )
    assert has_helper_def, (
        "T-NEW-169 WIRE-1: a `_build_dispatch(argv: list[str]) -> "
        "dict` helper must exist. It parses argparse argv into the "
        "dispatch dict that `run(args)` then routes on."
    )
    assert has_call_with_argv, (
        "T-NEW-169 WIRE-1: `_build_dispatch(argv)` must be called "
        "somewhere in cmds/runNchantdOffice.py (typically from the "
        "`__main__` block, e.g. `run(_build_dispatch(argv))`). "
        "Pre-fix the file had no argparse helper at all."
    )


def test_run_function_signature_dict():
    """`run(args)` first parameter's type annotation is `dict[...]`
    (or `Mapping[...]`), NOT `list[...]`.

    Pre-fix: `def run(args: list[str])` declares the contract is
    that args is a list. But the function uses `args` as a dict
    (`nchantment` does `'instance' in args` which is dict-shaped).

    Post-fix: `def run(args: dict[str, Any])` (or equivalent) so
    the type annotation matches the dispatch dict that
    `_build_dispatch(argv)` produces.
    """
    tree = ast.parse(_source())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            first_arg = node.args.args[0]
            ann = (
                ast.unparse(first_arg.annotation)
                if first_arg.annotation
                else ""
            )
            # accept dict / Mapping / MappingProxy; reject list / tuple
            ok = (
                "dict" in ann.lower()
                or "mapping" in ann.lower()
                or "mappings" in ann.lower()
            ) and "list[" not in ann.lower() and "tuple[" not in ann.lower()
            assert ok, (
                f"T-NEW-169 WIRE-1: `run(args)` first parameter's type "
                f"annotation must be a dict/Mapping shape, not a "
                f"list/tuple. Found: `{ann}`. The function routes "
                f"through a dispatch dict built from "
                f"`_build_dispatch(argv) -> dict`."
            )
            return
    raise AssertionError(
        "`run` function not found in cmds/runNchantdOffice.py"
    )
