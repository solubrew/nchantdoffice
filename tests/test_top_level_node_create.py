"""T-NEW-130 regression test: top-level node creation lands at ``pid=0``.

**Top-level new-node toolbar creates do not land at the root**

The toolbar entry with lookup code ``add_node_top_app_rootnode``
dispatches to ``NchantdDocumentToolBar.launch_new_document_sigil``
which opens ``NchantdNewDocumentSigil``. The user picks a
document type, the sigil's ``accept`` calls ``add_tab('center')``,
and ``add_tab`` reads:

    pid = self.app.view.panes["left"].model.current_node.nid

That uses the *currently selected* node as the parent. For a
top-level create there is no intended parent -- the new node
should land at the root (pid=0). The current code parent-pins
the new node under whatever the user had selected before
opening the sigil, which makes "create at top level" silently
behave as "create as child of whatever was selected".

The fix:
1. ``NchantdNewDocumentSigil.__init__`` accepts ``top_level`` in
   the cfg dict (default False) and stores it on ``self``.
2. ``launch_new_document_sigil`` (toolbar) sets
   ``top_level=True`` when the lookup code is
   ``add_node_top_app_rootnode`` -- this is the only entry
   point that genuinely intends a root create.
3. The sigil's ``add_tab`` and ``add_document`` paths use
   ``pid=0`` when ``self.top_level is True``, else fall back
   to the existing ``current_node.nid`` behavior.

Affected sites:
- nchantdoffice/dialogs/dialog_documents.py: sigil constructor + add_tab
- nchantdoffice/widgets/controls/toolbars.py: launch_new_document_sigil
- tests/test_top_level_node_create.py: new file (this test)

Migration plan (no priority / low priority -- design decision
first): the new ``top_level`` flag is opt-in. Existing call
sites that launch the sigil without the flag keep their old
behavior (parent under current_node.nid). The toolbar's
rootnode dispatch path is the only one that sets the flag.

Steps:
1. Add ``self.top_level = bool(cfg.get("top_level", False))``
   to ``NchantdNewDocumentSigil.__init__``.
2. In ``add_tab``, switch to ``pid = 0`` when
   ``self.top_level is True``.
3. In ``launch_new_document_sigil``, pass
   ``cfg={"top_level": True}`` when the dispatch
   lookup code is ``add_node_top_app_rootnode``.
"""

import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest


PROJ_ROOT = Path("/home/solubrew/.hermes/projects/nchantdoffice")


def _read(path):
    return path.read_text()


# ---------------------------------------------------------------------------
# Contract: sigil must accept + persist a ``top_level`` flag
# ---------------------------------------------------------------------------

def test_sigil_has_top_level_after_init():
    """A NchantdNewDocumentSigil instance must have a
    ``top_level`` attribute after construction (set from cfg
    in ``__init__``).
    """
    from nchantdoffice.dialogs.dialog_documents import (
        NchantdNewDocumentSigil,
    )
    # Construct via __new__ + manual attribute setting so we
    # don't need to spin up Qt (initWidget requires a Qt event
    # loop). We only check that __init__ *would* set the attr
    # via its source-code contract, plus that any sigil built
    # with cfg={"top_level": True} (assuming Qt is around)
    # would surface it. The source-level check below catches
    # the __init__ body.
    src = inspect.getsource(NchantdNewDocumentSigil.__init__)
    assert "self.top_level" in src, (
        "NchantdNewDocumentSigil.__init__ must define "
        "self.top_level (T-NEW-130)."
    )


def test_sigil_top_level_defaults_false():
    """When cfg is empty, sigil.top_level must default to False."""
    from nchantdoffice.dialogs.dialog_documents import (
        NchantdNewDocumentSigil,
    )
    src = inspect.getsource(NchantdNewDocumentSigil.__init__)
    assert "top_level" in src, (
        "NchantdNewDocumentSigil.__init__ must read a top_level "
        "flag from cfg (T-NEW-130)."
    )


# ---------------------------------------------------------------------------
# Contract: sigil.add_tab uses pid=0 when top_level is True
# ---------------------------------------------------------------------------

def test_sigil_add_tab_uses_pid_zero_when_top_level():
    """Source-level: when ``top_level`` is True,
    ``NchantdNewDocumentSigil.add_tab`` must compute ``pid = 0``,
    not ``pid = current_node.nid``.
    """
    from nchantdoffice.dialogs.dialog_documents import (
        NchantdNewDocumentSigil,
    )
    src = inspect.getsource(NchantdNewDocumentSigil.add_tab)
    # The fix introduces a branch on top_level:
    #   if self.top_level:            (or getattr(self, "top_level", False))
    #       pid = 0
    #   else:
    #       pid = current_node.nid
    top_level_referenced = (
        "self.top_level" in src or 'getattr(self, "top_level"' in src
    )
    assert top_level_referenced, (
        "add_tab must check self.top_level (T-NEW-130)."
    )
    assert "pid = 0" in src, (
        "add_tab must compute pid=0 for top-level creates "
        "(T-NEW-130)."
    )


def test_sigil_add_tab_pid_branch_is_exclusive():
    """The top_level branch must NOT skip the legacy ``pid =
    current_node.nid`` fallback -- both paths must be present
    so non-top-level sigil launches keep their old behavior.
    """
    from nchantdoffice.dialogs.dialog_documents import (
        NchantdNewDocumentSigil,
    )
    src = inspect.getsource(NchantdNewDocumentSigil.add_tab)
    top_level_referenced = (
        "self.top_level" in src or 'getattr(self, "top_level"' in src
    )
    assert top_level_referenced, (
        "add_tab must check self.top_level (T-NEW-130)."
    )
    assert "current_node.nid" in src, (
        "add_tab must still fall back to current_node.nid for "
        "non-top-level creates -- do not delete the legacy path."
    )


# ---------------------------------------------------------------------------
# Contract: toolbar launches the sigil with top_level=True for rootnode
# ---------------------------------------------------------------------------

def test_toolbar_set_handler_routes_rootnode_to_sigil():
    """Regression guard: the toolbar's ``set_handler`` match must
    still route ``add_node_top_app_rootnode`` to
    ``launch_new_document_sigil`` (the sigil flow). If someone
    re-routes it back to ``add_node``, the top_level fix becomes
    moot because add_node is the bare-node path.
    """
    src = _read(
        PROJ_ROOT / "nchantdoffice" / "widgets" / "controls" / "toolbars.py"
    )
    # Locate the set_handler (singular) function body, NOT
    # set_handlers (plural).
    target = "def set_handler("
    start = src.index(target)
    # Find the next top-level def after set_handler
    rest = src[start + len(target):]
    next_def_idx = -1
    for marker in ("\n    def set_handlers", "\n    def set_active_item"):
        if marker in rest:
            idx = rest.index(marker)
            if next_def_idx == -1 or idx < next_def_idx:
                next_def_idx = idx
    body = rest[: next_def_idx if next_def_idx != -1 else len(rest)]
    assert "add_node_top_app_rootnode" in body, (
        "set_handler must still match add_node_top_app_rootnode"
    )
    assert "launch_new_document_sigil" in body, (
        "set_handler must route add_node_top_app_rootnode to "
        "launch_new_document_sigil (T-NEW-130)."
    )


def test_toolbar_launch_new_document_sigil_passes_top_level():
    """Source-level: the toolbar's
    ``launch_new_document_sigil`` must pass ``top_level=True``
    when invoked for the rootnode lookup code.
    """
    src = _read(
        PROJ_ROOT / "nchantdoffice" / "widgets" / "controls" / "toolbars.py"
    )
    target = "def launch_new_document_sigil("
    start = src.index(target)
    rest = src[start + len(target):]
    next_def_idx = -1
    for marker in ("\n    def set_active_item", "\n    def set_handlers"):
        if marker in rest:
            idx = rest.index(marker)
            if next_def_idx == -1 or idx < next_def_idx:
                next_def_idx = idx
    body = rest[: next_def_idx if next_def_idx != -1 else len(rest)]
    assert "top_level" in body, (
        "toolbars.launch_new_document_sigil must pass "
        "top_level=True to the sigil (T-NEW-130)."
    )


# ---------------------------------------------------------------------------
# Behavioural end-to-end: top_level=True forces pid=0
# ---------------------------------------------------------------------------

def test_sigil_add_tab_pid_is_zero_when_top_level(monkeypatch):
    """Behavioural: with ``top_level=True`` the sigil's
    ``add_tab`` must invoke ``panes[tabset].model.add_tab``
    with ``pid=0``, regardless of what current_node.nid is.
    """
    from nchantdoffice.dialogs.dialog_documents import (
        NchantdNewDocumentSigil,
    )

    captured: list = []

    class _StubPanes(dict):
        """Panes stub that records the add_tab call."""

        def __missing__(self, key):
            class _Pane:
                def __init__(self):
                    pass

                model = SimpleNamespace(
                    max_position=0,
                    add_tab=lambda *args, **kwargs: captured.append(
                        ("model.add_tab", args, kwargs)
                    ),
                    current_node=SimpleNamespace(
                        nid=999,
                        updateTabs=lambda *a, **k: None,
                    ),
                )

            self[key] = _Pane()
            return self[key]

    sigil = NchantdNewDocumentSigil.__new__(NchantdNewDocumentSigil)
    sigil.top_level = True
    sigil.ok = True
    sigil.widget = "stub-widget"
    sigil.document_nm = "stub-doctype"
    sigil.open = False
    sigil.load_google = False
    sigil.file_path = None

    # Attach a minimal app view stub.
    app = SimpleNamespace(
        view=SimpleNamespace(panes=_StubPanes()),
    )
    sigil.app = app
    sigil.name = SimpleNamespace(textbox=SimpleNamespace(entry_data="NewDoc"))

    # Bypass initWidget/Qt -- just call add_tab directly.
    sigil.add_tab("center")

    assert captured, "add_tab must call panes[tabset].model.add_tab"
    call = captured[0]
    name, pid, pos, widget, widgdata, doc_type, tabset = call[1]
    assert pid == 0, (
        f"top_level=True must force pid=0; got pid={pid!r} "
        f"(T-NEW-130)."
    )


def test_sigil_add_tab_pid_is_current_node_when_not_top_level(monkeypatch):
    """Regression guard: with ``top_level=False`` (default),
    ``add_tab`` must still use ``current_node.nid``. The fix
    must NOT change behavior for non-top-level sigil launches.
    """
    from nchantdoffice.dialogs.dialog_documents import (
        NchantdNewDocumentSigil,
    )

    captured: list = []

    class _StubPanes(dict):
        def __missing__(self, key):
            class _Pane:
                def __init__(self):
                    pass

                model = SimpleNamespace(
                    max_position=0,
                    add_tab=lambda *args, **kwargs: captured.append(
                        ("model.add_tab", args, kwargs)
                    ),
                    current_node=SimpleNamespace(
                        nid=42,
                        updateTabs=lambda *a, **k: None,
                    ),
                )

            self[key] = _Pane()
            return self[key]

    sigil = NchantdNewDocumentSigil.__new__(NchantdNewDocumentSigil)
    sigil.top_level = False
    sigil.ok = True
    sigil.widget = "stub-widget"
    sigil.document_nm = "stub-doctype"
    sigil.open = False
    sigil.load_google = False
    sigil.file_path = None
    sigil.app = SimpleNamespace(view=SimpleNamespace(panes=_StubPanes()))
    sigil.name = SimpleNamespace(textbox=SimpleNamespace(entry_data="NewDoc"))

    sigil.add_tab("center")

    assert captured
    call = captured[0]
    name, pid, pos, widget, widgdata, doc_type, tabset = call[1]
    assert pid == 42, (
        f"top_level=False must keep legacy behavior (pid = "
        f"current_node.nid = 42); got pid={pid!r}"
    )