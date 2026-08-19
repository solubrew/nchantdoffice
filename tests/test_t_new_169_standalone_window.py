"""T-NEW-169 WIRE-2 -- NchantdDocumentStandaloneWindow class.

The T-NEW-169 plan calls for a new
`NchantdDocumentStandaloneWindow` class in
`nchantdoffice/nchantdoffice.py`. The class is the
QMainWindow host for the standalone 2-pane minimal shell
(DECIDE-2 (b): keep tabset chrome with one tab).

LOCKED DESIGN (operator-approved 2026-08-19):
  DECIDE-1 (a) -- argparse subcommand (WIRE-1)
  DECIDE-2 (ii) -- full standalone 2-pane shell that
  reuses the standalone window as a first-class widget.
  This class IS that shell.

Public API (the WIP contract, extending in WIRE-3):

  standalone = NchantdDocumentStandaloneWindow(
      parent=None,
      document_type="script",  # one of script/notebook/image/form
      preload_path=None,
  )
  standalone.initWidget()    # builds central + dock widgets
  standalone.show()          # QMainWindow standard

Inside the class:
  - Central widget: a single QWidget that hosts one document
    (a `NchantdOfficeScript` / `NchantdOfficeNotebook` / ...)
    per the dispatched `document_type`.
  - Right dock: a single-tool-bar / single-pane toolbox stub
    (the dispatch in WIRE-3 picks the matching right-pane
    toolbox class; for WIRE-2 the dock is present as an empty
    widget holder so the layout is correct).
  - 2-pane shell: `QSplitter` (or equivalent) host that
    splits the document + toolbox.

Tests are AST-source structural (mirroring T-NEW-167..170
pattern). `nchantdoffice/nchantdoffice.py` cannot be
imported in the test environment because `import pyqt` etc.
boot Qt and write configs at module load. AST inspection +
string-pattern searches are the only safe path.
"""

import ast
from pathlib import Path


NCHANTDOFFICE_PATH = (
    Path(__file__).parents[1] / "nchantdoffice/nchantdoffice.py"
)


def _source() -> str:
    return NCHANTDOFFICE_PATH.read_text()


def _class_source(name: str) -> str:
    """Return the source of a top-level class."""
    tree = ast.parse(_source())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(
        f"{name!r} class not found in {NCHANTDOFFICE_PATH}"
    )


def _find_class(name: str) -> ast.ClassDef:
    tree = ast.parse(_source())
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(
        f"{name!r} class not found in {NCHANTDOFFICE_PATH}"
    )


def _method_source(class_name: str, method_name: str) -> str:
    cls = _find_class(class_name)
    for body_node in cls.body:
        if (
            isinstance(body_node, ast.FunctionDef)
            and body_node.name == method_name
        ):
            return ast.unparse(body_node)
    raise AssertionError(
        f"{method_name!r} method not found in {class_name}"
    )


def _has_method(class_name: str, method_name: str) -> bool:
    try:
        _method_source(class_name, method_name)
        return True
    except AssertionError:
        return False


def test_class_exists():
    """`NchantdDocumentStandaloneWindow` is a top-level class in
    `nchantdoffice/nchantdoffice.py`.
    """
    src = _source()
    tree = ast.parse(src)
    names = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
    assert "NchantdDocumentStandaloneWindow" in names, (
        f"T-NEW-169 WIRE-2: `NchantdDocumentStandaloneWindow` "
        f"class must be defined in `nchantdoffice/nchantdoffice.py`. "
        f"Found classes: {names}."
    )


def test_subclasses_qmainwindow():
    """The class subclasses `QMainWindow`.

    Per DECIDE-2 (ii), the standalone window is a full 2-pane
    shell. `QMainWindow` is the Qt primitive that gives us the
    central-widget slot + dock-widget slots for free, which is
    exactly what the right-side toolbox needs.

    We accept any base containing `QMainWindow` (so e.g.
    `nchantrs.widgets.applications.NchantdMainWindow` which is
    itself a `QMainWindow` subclass is acceptable).
    """
    cls = _find_class("NchantdDocumentStandaloneWindow")
    base_names = [
        ast.unparse(base) for base in cls.bases
    ]
    qmainwindow_present = any(
        "QMainWindow" in name for name in base_names
    )
    assert qmainwindow_present, (
        f"T-NEW-169 WIRE-2: `NchantdDocumentStandaloneWindow` "
        f"must subclass `QMainWindow` (or a subclass of it). "
        f"Found bases: {base_names}. The Qt `QMainWindow` "
        f"primitive gives us the central-widget + dock-widget "
        f"slots we need for the 2-pane layout."
    )


def test_constructor_takes_dispatch_args():
    """`__init__` accepts `(parent, document_type, preload_path=None)`.

    The operator-set dispatch passes the parsed dict through to
    `run({mode, type, path})` (WIRE-1). The standalone window's
    `__init__` must consume the same trio: parent (optional),
    document_type (one of script/notebook/image/form), and the
    optional preload_path. The `preload_path` defaults to None.
    """
    src = _method_source(
        "NchantdDocumentStandaloneWindow", "__init__"
    )
    required = ["document_type", "preload_path"]
    missing = [r for r in required if r not in src]
    assert not missing, (
        f"T-NEW-169 WIRE-2: `__init__` must accept "
        f"`document_type` and `preload_path` parameters (the "
        f"WIRE-1 dispatch's `type` and `path` keys). Missing: "
        f"{missing}. Source: {src[:300]}"
    )


def test_init_widget_method_exists():
    """`initWidget(self)` lives on the class (consistent with the
    nchantrs+nchantdoffice lifecycle: `initModel` -> `initView`
    -> `initWidget`).
    """
    assert _has_method(
        "NchantdDocumentStandaloneWindow", "initWidget"
    ), (
        "T-NEW-169 WIRE-2: `initWidget` method must exist on "
        "`NchantdDocumentStandaloneWindow`. The init pattern in "
        "this codebase always calls initWidget().show() after "
        "construction; missing the method breaks the launch "
        "contract."
    )


def test_init_view_method_exists():
    """`initView(self)` lives on the class (consistent with the
    nchantrs+nchantdoffice lifecycle). It sets the central
    widget + dock widget layout.
    """
    assert _has_method(
        "NchantdDocumentStandaloneWindow", "initView"
    ), (
        "T-NEW-169 WIRE-2: `initView` method must exist on "
        "`NchantdDocumentStandaloneWindow`. The init pattern "
        "calls initView() from inside initWidget(); missing "
        "the method breaks the launch contract."
    )


def test_init_widget_calls_init_view():
    """`initWidget` body invokes `self.initView()` (or
    `self.initView(cfg)`).

    Per the nchantrs+nchantdoffice init pattern, initWidget
    orchestrates initModel + initView. The bridge shape
    `initWidget -> initView` is the convention everywhere else
    in this file.
    """
    src = _method_source(
        "NchantdDocumentStandaloneWindow", "initWidget"
    )
    has_init_view_call = (
        "self.initView" in src
        or "initView()" in src
    )
    assert has_init_view_call, (
        "T-NEW-169 WIRE-2: `initWidget` body must call "
        "`self.initView()` (with or without a cfg argument). "
        "Without this call the central widget + dock layout "
        "is never built and the standalone window is just a "
        "bare QMainWindow with no children."
    )


def test_init_view_sets_central_widget():
    """`initView` body invokes `setCentralWidget(...)`.

    The 2-pane shell needs the document on the left (central
    widget) and the toolbox on the right (dock widget). The
    `setCentralWidget` call is what makes the document the
    main content area; without it, the document is a non-Qt
    child widget that doesn't render properly inside the
    QMainWindow.
    """
    src = _method_source(
        "NchantdDocumentStandaloneWindow", "initView"
    )
    has_central_set = "setCentralWidget" in src
    assert has_central_set, (
        "T-NEW-169 WIRE-2: `initView` body must call "
        "`self.setCentralWidget(...)` so the document widget "
        "is the main content area. Without this the standalone "
        "window has no rendered central area."
    )


def test_init_view_attaches_dock_for_toolbox():
    """`initView` body invokes `addDockWidget(...)` (right dock).

    The 2-pane shell needs a right-side dock for the toolbox.
    `QMainWindow.addDockWidget(Qt.RightDockWidgetArea, ...)` is
    the canonical call.
    """
    src = _method_source(
        "NchantdDocumentStandaloneWindow", "initView"
    )
    has_dock = "addDockWidget" in src
    assert has_dock, (
        "T-NEW-169 WIRE-2: `initView` body must call "
        "`self.addDockWidget(...)` (typically with "
        "`Qt.RightDockWidgetArea` for the right-side toolbox). "
        "Without this the right-side toolbox has nowhere to "
        "live and the 2-pane layout collapses to 1 pane."
    )


def test_dispatch_dict_reference_present():
    """A `DOCUMENT_TYPE_DISPATCH` dict-like literal exists with
    the 4 type names as keys (script, notebook, image, form).

    WIRE-2 only ships the placeholder dispatch (type name
    recognized but no real class lookup). WIRE-3 fills in the
    actual class references.
    """
    src = _source()
    has_dispatch = (
        "DOCUMENT_TYPE_DISPATCH" in src
        or "DOC_TYPE_DISPATCH" in src
        # an inline dict literal with all 4 type names also works
        or all(
            t in src for t in ("'script'", '"script"',
                               "'notebook'", '"notebook"',
                               "'image'", '"image"',
                               "'form'", '"form"')
        )
    )
    assert has_dispatch, (
        "T-NEW-169 WIRE-2: a `DOCUMENT_TYPE_DISPATCH` (or "
        "equivalent) dict literal must reference all 4 doc "
        "types: script, notebook, image, form. The class-name "
        "fill-in lands in WIRE-3; WIRE-2 just needs the dict "
        "shape in place."
    )


def test_constructor_stores_dispatch_keys():
    """The `__init__` body stores `document_type` and
    `preload_path` on the instance so subsequent methods
    (initView) can read them.
    """
    src = _method_source(
        "NchantdDocumentStandaloneWindow", "__init__"
    )
    has_type_attr = "self.document_type" in src
    has_path_attr = "self.preload_path" in src
    assert has_type_attr and has_path_attr, (
        f"T-NEW-169 WIRE-2: `__init__` body must store "
        f"`self.document_type = document_type` and "
        f"`self.preload_path = preload_path` so initView can "
        f"read them. Found self.document_type={has_type_attr}, "
        f"self.preload_path={has_path_attr}."
    )
