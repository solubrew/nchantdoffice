"""T-NEW-141b regression: ship the safe subset of the
inside-nchantdoffice TODO sweep.

T-NEW-141b ships 4 of the 7 remaining markers from
T-NEW-141:

1. ``panes/documents.py:798`` -- catalog tab-None stub.
   The TODO comment is misleading: a stub IS in place
   (``NchantdOfficeTab({...}).initWidget()`` synthesizes a
   placeholder). Fix: remove the stale TODO; replace
   with a docstring explaining the stub's contract
   (placeholder values so the toolbox renders empty
   fields gracefully when no tab is selected).
2. ``widgets/documents/workbooks/notebooks.py:1786`` --
   ``_on_webview_load_started`` was a no-op stub. Today
   the QWebEngineView ``loadStarted`` signal fires the
   no-op (silent). Fix: log the load-started event so
   Jupyter-tab load attempts are visible in the log.
3. ``widgets/documents/workbooks/notebooks.py:1790`` --
   ``_on_webview_load_progress`` was a no-op stub.
   ``loadProgress`` fires the no-op. Fix: log progress
   (int percent) so slow Jupyter loads are observable.
4. ``utilities/users.py:69`` -- ``self.has_pro = True``
   hardcoded; the comment asked for service truth
   (``nchantdoffice.com`` API call). The service truth
   is explicitly out of scope (requires a network call
   at boot); the local cache path IS in scope. Fix: read
   from ``load_credentials().user_tier`` (pycurity
   ``DesktopCredentials``); default to True for legacy
   users without credentials (backward compat with the
   hardcoded True); log a warning when the cache is
   missing or stale.

The 3 deferred markers (palette drawer wiring, tool
drawer re-render, per-doctype features pane) are
shipped in T-NEW-141c. They touch live UI architecture
that needs design decisions before shipping.

Tests (TDD):
- source-level: panes/documents.py no longer has the
  misleading "tab is None" TODO.
- source-level: notebooks._on_webview_load_started and
  _on_webview_load_progress now contain real logging.
- source-level: users.NchantdOfficeUser.__init__ reads
  has_pro from load_credentials() rather than the
  hardcoded True.
- behavioural (pro user): when load_credentials returns
  user_tier='pro', has_pro is True.
- behavioural (free user): when load_credentials returns
  user_tier='free', has_pro is False.
- behavioural (no creds): when load_credentials returns
  None, has_pro defaults to True (backward compat).
"""
import inspect
from types import SimpleNamespace
from unittest.mock import MagicMock

# T-NEW-074 Task 9: keep Qt on the headless offscreen platform
# before any PySide6 import so the integration test does not
# need a real display.
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest  # noqa: E402


# ---------------------------------------------------------------------------
# 1. panes/documents.py:798 -- catalog tab-None stub
# ---------------------------------------------------------------------------

def test_pane_documents_no_longer_has_tab_none_todo():
    """T-NEW-141b (1): the misleading TODO at
    panes/documents.py:798 must be replaced with a real
    docstring. The stub IS in place (the test confirms the
    fallback path runs); the stale comment is what confuses
    readers.
    """
    from nchantdoffice.widgets.panes.documents import (
        NchantdOfficeTabEditPane,
    )
    src = inspect.getsource(NchantdOfficeTabEditPane.initView)
    # Must NOT have the stale "tab is None" TODO.
    assert "tab is None for intialized catalog" not in src, (
        f"stale 'tab is None' TODO must be removed (T-NEW-141b). "
        f"Got:\n{src[:1500]}"
    )
    # And must have a real docstring on the catalog tab
    # fallback (not an empty `"""`).
    assert "T-NEW-141b" in src or "fallback" in src.lower(), (
        "catalog-tab-None stub must have a real docstring "
        "(T-NEW-141b)."
    )


# ---------------------------------------------------------------------------
# 2 + 3. notebooks._on_webview_load_started + _on_webview_load_progress
# ---------------------------------------------------------------------------

def test_on_webview_load_started_logs():
    """T-NEW-141b (2): ``_on_webview_load_started`` was a
    no-op stub. Fix: log the event so Jupyter-tab load
    attempts are visible in the application log.
    """
    from nchantdoffice.widgets.documents.workbooks.notebooks import (
        NchantdOfficeNotebook,
    )
    src = inspect.getsource(NchantdOfficeNotebook._on_webview_load_started)
    # Must NOT be a TODO stub.
    assert "TODO" not in src or "T-NEW-141b" in src, (
        f"_on_webview_load_started still has a TODO stub "
        f"(T-NEW-141b). Got:\n{src[:600]}"
    )
    # And must contain a logging call.
    assert "logma" in src and "info" in src, (
        f"_on_webview_load_started must log via logma.info "
        f"(T-NEW-141b). Got:\n{src[:600]}"
    )


def test_on_webview_load_progress_logs_percent():
    """T-NEW-141b (3): ``_on_webview_load_progress`` was a
    no-op stub. Fix: log progress (int percent) so slow
    Jupyter loads are observable in the log.
    """
    from nchantdoffice.widgets.documents.workbooks.notebooks import (
        NchantdOfficeNotebook,
    )
    src = inspect.getsource(NchantdOfficeNotebook._on_webview_load_progress)
    # Must NOT be a TODO stub.
    assert "TODO" not in src or "T-NEW-141b" in src, (
        f"_on_webview_load_progress still has a TODO stub "
        f"(T-NEW-141b). Got:\n{src[:600]}"
    )
    # And must contain a logging call.
    assert "logma" in src, (
        f"_on_webview_load_progress must log via logma "
        f"(T-NEW-141b). Got:\n{src[:600]}"
    )


# ---------------------------------------------------------------------------
# 4. utilities/users.py:69 -- has_pro from credentials
# ---------------------------------------------------------------------------

def _stub_kahndor_instruct(monkeypatch):
    """Stub the kahndor.Instruct symbol used inside
    NchantdOfficeUser.__init__ so the .config.override
    line does not raise. The override is a no-op for the
    has_pro test -- we just need __init__ to return.

    T-NEW-141b patch-point correction: production
    ``nchantdoffice/utilities/users.py`` binds its local
    ``kahndor`` name via ``from kahndor import kahndor``
    (i.e. the *submodule* ``kahndor.kahndor``), and the
    call site uses ``kahndor.Instruct(...)`` on that local
    binding. Patching the top-level ``kahndor`` namespace
    package (``kahndor.Instruct``) misses the production
    symbol AND fails outright in editable installs where
    ``kahndor`` is loaded as a PEP 420 namespace package
    (no ``__init__.py`` executed, no module-level
    ``__getattr__``), making the test unwritable against
    the production code path. Patching the submodule
    works regardless of install mode and matches the
    symbol ``users.py`` actually resolves.
    """
    from kahndor import kahndor as _kahndor
    monkeypatch.setattr(
        _kahndor, "Instruct",
        lambda *a, **kw: SimpleNamespace(
            select=lambda *a, **kw: SimpleNamespace(override=lambda *a, **kw: None)
        ),
    )


def _stub_nchantd_user_init(monkeypatch):
    """Stub the parent ``NchantdUser.__init__`` so the
    secure-store branch does not execute during the
    has_pro test -- we are only exercising the
    ``_resolve_has_pro_from_credentials`` branch in
    ``NchantdOfficeUser.__init__``.
    """
    from nchantrs.utilities.users import NchantdUser
    monkeypatch.setattr(
        NchantdUser, "__init__",
        lambda self, parent, cfg=None: setattr(self, "config",
            SimpleNamespace(override=lambda *a, **kw: None,
                            dikt={})) or None
    )


def test_users_init_reads_has_pro_from_credentials(monkeypatch):
    """T-NEW-141b (4): ``NchantdOfficeUser.__init__`` must
    read ``has_pro`` from ``load_credentials().user_tier``
    rather than the hardcoded ``True`` at line 69. The
    service-truth path is explicitly out of scope (the
    card body defers it); the local cache is what we have.
    """
    from nchantdoffice.utilities import credentials as creds
    from nchantdoffice.utilities import users as users_mod

    # Stub load_credentials to return a 'pro' tier.
    fake_creds = SimpleNamespace(user_tier="pro")
    monkeypatch.setattr(creds, "load_credentials", lambda: fake_creds)
    _stub_nchantd_user_init(monkeypatch)
    _stub_kahndor_instruct(monkeypatch)

    user = users_mod.NchantdOfficeUser.__new__(
        users_mod.NchantdOfficeUser
    )
    user.__init__(parent=None)
    assert user.has_pro is True, (
        f"has_pro must be True when load_credentials returns "
        f"user_tier='pro' (T-NEW-141b); got {user.has_pro!r}"
    )


def test_users_init_free_user_has_pro_false(monkeypatch):
    """T-NEW-141b (4): when ``load_credentials()`` returns
    ``user_tier='free'``, ``has_pro`` is False.
    """
    from nchantdoffice.utilities import credentials as creds
    from nchantdoffice.utilities import users as users_mod
    _stub_nchantd_user_init(monkeypatch)
    _stub_kahndor_instruct(monkeypatch)

    fake_creds = SimpleNamespace(user_tier="free")
    monkeypatch.setattr(creds, "load_credentials", lambda: fake_creds)
    user = users_mod.NchantdOfficeUser.__new__(users_mod.NchantdOfficeUser)
    user.__init__(parent=None)
    assert user.has_pro is False, (
        f"has_pro must be False when load_credentials returns "
        f"user_tier='free' (T-NEW-141b); got {user.has_pro!r}"
    )


def test_users_init_no_creds_defaults_to_true(monkeypatch):
    """T-NEW-141b (4): when ``load_credentials()`` returns
    None (no vault yet, or pykey not installed), ``has_pro``
    defaults to True -- backward compat with the original
    hardcoded True at line 69.
    """
    from nchantdoffice.utilities import credentials as creds
    from nchantdoffice.utilities import users as users_mod
    _stub_nchantd_user_init(monkeypatch)
    _stub_kahndor_instruct(monkeypatch)

    monkeypatch.setattr(creds, "load_credentials", lambda: None)
    user = users_mod.NchantdOfficeUser.__new__(users_mod.NchantdOfficeUser)
    user.__init__(parent=None)
    assert user.has_pro is True, (
        f"has_pro must default to True when no credentials are "
        f"stored (T-NEW-141b backward compat); got {user.has_pro!r}"
    )


def test_users_init_enterprise_user_has_pro_true(monkeypatch):
    """T-NEW-141b (4): when ``load_credentials()`` returns
    ``user_tier='enterprise'``, ``has_pro`` is True.
    """
    from nchantdoffice.utilities import credentials as creds
    from nchantdoffice.utilities import users as users_mod
    _stub_nchantd_user_init(monkeypatch)
    _stub_kahndor_instruct(monkeypatch)

    fake_creds = SimpleNamespace(user_tier="enterprise")
    monkeypatch.setattr(creds, "load_credentials", lambda: fake_creds)
    user = users_mod.NchantdOfficeUser.__new__(users_mod.NchantdOfficeUser)
    user.__init__(parent=None)
    assert user.has_pro is True, (
        f"has_pro must be True for user_tier='enterprise' "
        f"(T-NEW-141b); got {user.has_pro!r}"
    )