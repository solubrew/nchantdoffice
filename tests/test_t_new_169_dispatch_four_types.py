"""T-NEW-169 WIRE-3 -- 4 high-value document-type instantiations.

This card replaces the WIRE-2 placeholder DOCUMENT_TYPE_DISPATCH
(which had `None` values) with the four real NchantdOffice*
classes:

  DOCUMENT_TYPE_DISPATCH = {
      "script":   <NchantdOfficeScript reference>,
      "notebook": <NchantdOfficeNotebook reference>,
      "image":    <NchantdOfficeImage reference>,
      "form":     <NchantdOfficeForm reference>,
  }

Tests are AST-source structural (mirroring T-NEW-167..170
pattern). The NchantdOffice* classes live in
nchantdoffice/widgets/documents/{media,workbooks}/ and each
extends NchantdOfficeDocument (or its parent NchantdForm for
NchantdOfficeForm) -- both of which boot Qt on construction.
"""

import ast
import re
from pathlib import Path


NCHANTDOFFICE_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/nchantdoffice.py"
)


# The canonical locations of the 4 NchantdOffice* classes.
WIDGET_PATHS = {
    "script":   Path(__file__).parents[1] / "nchantdoffice/widgets/documents/media/scripts.py",
    "notebook": Path(__file__).parents[1] / "nchantdoffice/widgets/documents/workbooks/notebooks.py",
    "image":    Path(__file__).parents[1] / "nchantdoffice/widgets/documents/media/images.py",
    "form":     Path(__file__).parents[1] / "nchantdoffice/widgets/documents/media/forms.py",
}
DOC_TYPE_ORDER = ("script", "notebook", "image", "form")


def _source() -> str:
    return NCHANTDOFFICE_PATH.read_text()


def _class_defs_in_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    return [n.name for n in tree.body if isinstance(n, ast.ClassDef)]


def test_dispatch_dict_resolves_script():
    """`DOCUMENT_TYPE_DISPATCH["script"]` resolves -- directly
    (a class reference) or lazily (an importable dotted path) --
    to `NchantdOfficeScript`.

    The constructor contract locks all 4 keys, but the
    references must resolve at instantiation time. Pre-fix
    was `None` (the WIRE-2 placeholder); post-fix is either
    `NchantdOfficeScript` (direct) or
    `nchantdoffice.widgets.documents.media.scripts.NchantdOfficeScript`
    (lazy / dotted).
    """
    src = _source()
    # Direct ref: "script": NchantdOfficeScript
    has_direct = bool(
        re.search(
            r"""DOCUMENT_TYPE_DISPATCH[^=]*=[^']*\{[^}]*['"]script['"]\s*:\s*NchantdOfficeScript""",
            src,
        )
    )
    # Lazy / dotted: "script": "...NchantdOfficeScript"
    has_lazy = bool(
        re.search(
            r"""DOCUMENT_TYPE_DISPATCH[^=]*=[^']*\{[^}]*['"]script['"]\s*:\s*['"][^'"]*\.NchantdOfficeScript['"]""",
            src,
        )
    )
    assert has_direct or has_lazy, (
        "T-NEW-169 WIRE-3: `DOCUMENT_TYPE_DISPATCH['script']` must "
        "resolve to `NchantdOfficeScript` (either direct class "
        "reference or lazy dotted import path)."
    )


def test_dispatch_dict_resolves_notebook():
    """`DOCUMENT_TYPE_DISPATCH['notebook']` resolves to `NchantdOfficeNotebook`."""
    src = _source()
    has_direct = bool(
        re.search(
            r"""DOCUMENT_TYPE_DISPATCH[^=]*=[^']*\{[^}]*['"]notebook['"]\s*:\s*NchantdOfficeNotebook""",
            src,
        )
    )
    has_lazy = bool(
        re.search(
            r"""DOCUMENT_TYPE_DISPATCH[^=]*=[^']*\{[^}]*['"]notebook['"]\s*:\s*['"][^'"]*\.NchantdOfficeNotebook['"]""",
            src,
        )
    )
    assert has_direct or has_lazy, (
        "T-NEW-169 WIRE-3: `DOCUMENT_TYPE_DISPATCH['notebook']` "
        "must resolve to `NchantdOfficeNotebook`."
    )


def test_dispatch_dict_resolves_image():
    """`DOCUMENT_TYPE_DISPATCH['image']` resolves to `NchantdOfficeImage`."""
    src = _source()
    has_direct = bool(
        re.search(
            r"""DOCUMENT_TYPE_DISPATCH[^=]*=[^']*\{[^}]*['"]image['"]\s*:\s*NchantdOfficeImage""",
            src,
        )
    )
    has_lazy = bool(
        re.search(
            r"""DOCUMENT_TYPE_DISPATCH[^=]*=[^']*\{[^}]*['"]image['"]\s*:\s*['"][^'"]*\.NchantdOfficeImage['"]""",
            src,
        )
    )
    assert has_direct or has_lazy, (
        "T-NEW-169 WIRE-3: `DOCUMENT_TYPE_DISPATCH['image']` "
        "must resolve to `NchantdOfficeImage`."
    )


def test_dispatch_dict_resolves_form():
    """`DOCUMENT_TYPE_DISPATCH['form']` resolves to `NchantdOfficeForm`."""
    src = _source()
    has_direct = bool(
        re.search(
            r"""DOCUMENT_TYPE_DISPATCH[^=]*=[^']*\{[^}]*['"]form['"]\s*:\s*NchantdOfficeForm""",
            src,
        )
    )
    has_lazy = bool(
        re.search(
            r"""DOCUMENT_TYPE_DISPATCH[^=]*=[^']*\{[^}]*['"]form['"]\s*:\s*['"][^'"]*\.NchantdOfficeForm['"]""",
            src,
        )
    )
    assert has_direct or has_lazy, (
        "T-NEW-169 WIRE-3: `DOCUMENT_TYPE_DISPATCH['form']` "
        "must resolve to `NchantdOfficeForm`."
    )


def test_nchantd_office_script_class_exists():
    """`NchantdOfficeScript` is defined in scripts.py."""
    classes = _class_defs_in_file(WIDGET_PATHS["script"])
    assert "NchantdOfficeScript" in classes, (
        f"T-NEW-169 WIRE-3 prerequisite: `NchantdOfficeScript` "
        f"must be a class in `{WIDGET_PATHS['script']}`. "
        f"Found: {classes}."
    )


def test_nchantd_office_notebook_class_exists():
    """`NchantdOfficeNotebook` is defined in notebooks.py."""
    classes = _class_defs_in_file(WIDGET_PATHS["notebook"])
    assert "NchantdOfficeNotebook" in classes, (
        f"T-NEW-169 WIRE-3 prerequisite: `NchantdOfficeNotebook` "
        f"must be a class in `{WIDGET_PATHS['notebook']}`. "
        f"Found: {classes}."
    )


def test_nchantd_office_image_class_exists():
    """`NchantdOfficeImage` is defined in images.py."""
    classes = _class_defs_in_file(WIDGET_PATHS["image"])
    assert "NchantdOfficeImage" in classes, (
        f"T-NEW-169 WIRE-3 prerequisite: `NchantdOfficeImage` "
        f"must be a class in `{WIDGET_PATHS['image']}`. "
        f"Found: {classes}."
    )


def test_nchantd_office_form_class_exists():
    """`NchantdOfficeForm` is defined in forms.py."""
    classes = _class_defs_in_file(WIDGET_PATHS["form"])
    assert "NchantdOfficeForm" in classes, (
        f"T-NEW-169 WIRE-3 prerequisite: `NchantdOfficeForm` "
        f"must be a class in `{WIDGET_PATHS['form']}`. "
        f"Found: {classes}."
    )


def test_init_view_uses_dispatch_dict():
    """`NchantdDocumentStandaloneWindow.initView` body consults
    `DOCUMENT_TYPE_DISPATCH` to construct the document widget.

    Pre-fix the placeholder central widget ignored the dispatch.
    Post-fix the dispatch is consulted and the corresponding
    class is constructed + `setCentralWidget(...)` is called
    with the resulting instance.
    """
    tree = ast.parse(_source())
    found = False
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "NchantdDocumentStandaloneWindow"):
            continue
        for body_node in node.body:
            if (
                not isinstance(body_node, ast.FunctionDef)
                or body_node.name != "initView"
            ):
                continue
            src = ast.unparse(body_node)
            if "DOCUMENT_TYPE_DISPATCH" in src or "DOC_TYPE_DISPATCH" in src:
                found = True
                break
    assert found, (
        "T-NEW-169 WIRE-3: `NchantdDocumentStandaloneWindow.initView` "
        "must consult the dispatch dict (`DOCUMENT_TYPE_DISPATCH`) "
        "to construct the document widget. Pre-fix the placeholder "
        "ignored the dispatch entirely -- the standalone shell showed "
        "a stub label instead of a real document."
    )


def test_init_view_dispatch_passed_correctly():
    """The dispatch lookup reads `self.document_type` to get the
    key, and passes it through to the dispatch dict lookup.

    Acceptable patterns:
      `DOCUMENT_TYPE_DISPATCH[self.document_type]`
      `DOCUMENT_TYPE_DISPATCH.get(self.document_type)`
      `DOCUMENT_TYPE_DISPATCH.get(self.document_type, None)`
    """
    tree = ast.parse(_source())
    for node in tree.body:
        if not (isinstance(node, ast.ClassDef) and node.name == "NchantdDocumentStandaloneWindow"):
            continue
        for body_node in node.body:
            if (
                not isinstance(body_node, ast.FunctionDef)
                or body_node.name != "initView"
            ):
                continue
            src = ast.unparse(body_node)
            patterns = [
                r"DOCUMENT_TYPE_DISPATCH\[self\.document_type\]",
                r"DOCUMENT_TYPE_DISPATCH\.get\(\s*self\.document_type",
                r"DOC_TYPE_DISPATCH\[self\.document_type\]",
            ]
            ok = any(re.search(p, src) for p in patterns)
            assert ok, (
                f"T-NEW-169 WIRE-3: `initView` must look up the "
                f"document class via `DOCUMENT_TYPE_DISPATCH[self.document_type]` "
                f"or `.get(...)`. Source: {src[:600]}"
            )
            return
    raise AssertionError(
        "`NchantdDocumentStandaloneWindow.initView` not found"
    )
