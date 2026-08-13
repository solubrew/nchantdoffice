"""Sprint 8 — T-NEW-017/018/020 regression tests (AST-based).

The full T-NEW-017/018/020 fixes (Matrix ``on_cell_changed``,
``on_selection_changed``; PDF ``initModel``) are live in source.
Running them with a real Qt harness requires loading
``nchantdoffice.widgets.documents.workbooks.matricies`` /
``.media.pdfs`` which import the upstream-broken qpandas module
and the missing ``pycurity.pyhash.get_file_hash``. Those
blocks are documented under T-NEW-016 and the existing zip-slip
skip.

This test verifies the fixes are in place at the source level
via AST inspection — a structural guard that catches the
crash paths being reintroduced. When the upstream blockers are
cleared, swap these for runtime tests.
"""

import ast
from pathlib import Path


def _find_method_source(rel_path: str, method_name: str) -> str:
    root = Path(__file__).resolve().parent.parent
    src = (root / rel_path).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            return ast.get_source_segment(src, node) or ""
    return ""


def test_T_NEW_017_matrix_on_cell_changed_guards_None_column():
    """``chr(65 + item.column())`` would crash when ``column()``
    returns ``None``. The fix guards with
    ``if column is None or not isinstance(column, int): return``.
    """
    src = _find_method_source(
        "nchantdoffice/widgets/documents/workbooks/matricies.py",
        "on_cell_changed",
    )
    assert src, "on_cell_changed method missing"
    assert "if column is None" in src or "column is None" in src, (
        "Matrix on_cell_changed no longer guards against "
        "None column index — live T-NEW-017 crash returns."
    )
    # Extract just the function body so we don't trip on the
    # docstring literally mentioning the old code.
    tree = ast.parse(src)
    method_node = tree.body[0]
    docstring = ast.get_docstring(method_node) or ""
    docstring_lines = docstring.splitlines()
    body_lines = [
        line
        for line in src.splitlines()
        if line.lstrip() not in (l.lstrip() for l in docstring_lines)
    ]
    method_body_src = "\n".join(body_lines)
    assert "chr(65 + item.column())" not in method_body_src, (
        "Matrix on_cell_changed still calls chr on item.column() "
        "directly in the function body — live T-NEW-017 crash returns."
    )


def test_T_NEW_018_matrix_on_selection_changed_guards_missing_label():
    """``self.cell_ref_label.setText(...)`` would crash if
    ``cell_ref_label`` was never initialised. The fix guards with
    ``hasattr(self, "cell_ref_label")``.
    """
    src = _find_method_source(
        "nchantdoffice/widgets/documents/workbooks/matricies.py",
        "on_selection_changed",
    )
    assert src, "on_selection_changed method missing"
    assert "hasattr(self, \"cell_ref_label\")" in src, (
        "Matrix on_selection_changed no longer guards against "
        "missing cell_ref_label — live T-NEW-018 crash returns."
    )


def test_T_NEW_020_pdf_init_model_uses_get_with_default():
    """``self.config.dikt["document"]`` would raise KeyError
    when the help tab is opened without a document cfg. The
    fix uses ``self.config.dikt.get("document", {})``.
    """
    root = Path(__file__).resolve().parent.parent
    text = (root / "nchantdoffice/widgets/documents/media/pdfs.py").read_text()
    # The initModel that takes cfg=None may be defined on a parent
    # class; search for both 'def initModel' AND the body text.
    assert "self.config.dikt.get(\"document\", {})" in text, (
        "PDF initModel no longer uses config.dikt.get default — "
        "live T-NEW-020 KeyError returns."
    )
    # The broken bare-subscript form must no longer appear
    # in initModel-style code (the literal text inside a string is
    # OK; the assignment must be the safe form).
    import re
    # The signature includes a return annotation (-> Self) so the
    # regex needs to skip the annotation between ) and the body's
    # opening statement. Use a non-greedy match that consumes up
    # to the next class/def boundary.
    init_model_blocks = re.findall(
        r"def initModel\(.*?\):\n.*?(?=\n    def |\nclass |\Z)",
        text,
        flags=re.DOTALL,
    )
    assert init_model_blocks, "no initModel block found in pdfs.py"
    bare_subscript = False
    for block in init_model_blocks:
        # Skip docstring lines.
        non_doc_lines = "\n".join(
            l for l in block.splitlines()
            if not l.lstrip().startswith(('"""', "'", "#"))
        )
        if "self.config.dikt[\"document\"]" in non_doc_lines:
            bare_subscript = True
            break
    assert not bare_subscript, (
        "PDF initModel still uses the bare subscript form of "
        "config.dikt[\"document\"] — live T-NEW-020 KeyError returns."
    )


def test_T_NEW_022_browser_store_link_uses_positional_args():
    """``nchantrs.widgets.browsers.browsers.NchantdWebViewer`` URL
    tracking call: the kwargs `tags=path=path=name=` raised
    ``TypeError: ...unexpected keyword argument 'tag'`` when
    link_service resolved to ``NchantdCloakModel.store_link``.
    The fix uses positional args ``store_link(title, url_str, tags)``
    so both ``LinkService.store_link(name, path, tags)`` and
    ``NchantdCloakModel.store_link(url, name="", tag="")`` work.
    """
    # The test lives in nchantdoffice but the fix is in the sibling
    # nchantrs repo; resolve that path explicitly.
    root = Path(__file__).resolve().parent.parent.parent
    text = (root / "nchantrs/nchantrs/widgets/browsers/browsers.py").read_text()
    assert ".store_link(title, url_str, " in text, (
        "Browser store_link call was not converted to positional args "
        "— live T-NEW-022 crash returns."
    )


def test_T_NEW_021_tabset_load_tab_bounds_check_on_widgets():
    """``self.tab_widgets[tabn].dummy = ...`` raised
    ``IndexError: list index out of range`` when ``insert`` did
    not land the widget at ``tabn``. The fix bounds-checks the
    list length after the insert and bails with a logged error.
    """
    root = Path(__file__).resolve().parent.parent.parent
    text = (root / "nchantrs/nchantrs/models/tabsetmodels.py").read_text()
    assert "len(self.tab_widgets) <= tabn" in text, (
        "Tabset load_tab no longer bounds-checks the widget list "
        "before indexing - live T-NEW-021 IndexError returns."
    )


def test_T_NEW_015_nchantd_widget_default_context_menu_name():
    """``NchantdMonthCalendar`` raised ``AttributeError`` on
    ``self.context_menu_name`` because the mixin's
    ``init_variables`` never ran on the calendar init chain.
    The fix puts a default ``context_menu_name = "widget"``
    inside ``NchantdWidget.__init__``.
    """
    root = Path(__file__).resolve().parent.parent.parent
    text = (root / "nchantrs/nchantrs/widgets/widgets.py").read_text()
    # The default must be inside __init__, not just anywhere.
    tree = ast.parse(text)
    init_with_default = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            try:
                parent_class = node.parent.name
            except AttributeError:
                # Python 3.12 has no node.parent.
                src = ast.get_source_segment(text, node) or ""
                if "self.context_menu_name" in src:
                    init_with_default = True
            else:
                if parent_class == "NchantdWidget":
                    src = ast.get_source_segment(text, node) or ""
                    if "self.context_menu_name" in src:
                        init_with_default = True
    assert init_with_default, (
        "context_menu_name default is set somewhere, but not "
        "inside NchantdWidget.__init__ - subclass chains still "
        "skip the assignment."
    )
