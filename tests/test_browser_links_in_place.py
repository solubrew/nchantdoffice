"""Regression: ``NchantdOfficeWebBrowser.initView`` must enable
``links_in_place=True`` on the embedded ``NchantdWebViewer``.

Bug: link clicks that triggered Qt's default ``createWindow`` handling
(target=_blank / window.open) returned ``None`` from
``QWebEnginePage.createWindow``, so the popup was silently dropped and
the user saw the click "bounce back" — the page never changed. With
``links_in_place=True`` set anywhere in the page → engine → viewer
config chain, ``NchantdWebEnginePage.createWindow`` returns a
``_RedirectCapturePage`` that loads the URL in the current view
(nchantrs/widgets/browsers/pages.py:46).

These tests cover the wiring from ``initView`` → ``cfg["links_in_place"]``
so a future refactor can't silently drop the flag again.

Tests are pure-Python: no QApplication, no QtWebEngine process spawn
(offscreen render crashes the test runner with SIGSEGV on this image).
"""
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from nchantdoffice.widgets.documents.atnrg.browsers import (
    NchantdOfficeWebBrowser,
)


def _bare_browser(url="http://example.com/"):
    """Build a NchantdOfficeWebBrowser with the bare attrs initView touches.

    Avoids running ``__init__`` (which would pull in the full app model
    graph and likely crash in the test runner).
    """
    b = NchantdOfficeWebBrowser.__new__(NchantdOfficeWebBrowser)
    b.config = SimpleNamespace(dikt={})
    b.viewer = None
    b.app = SimpleNamespace(model=SimpleNamespace(codex=MagicMock()))
    # initView → get_active_url → self.active_page.document.active_url.active_url
    b.active_page = SimpleNamespace(
        document=SimpleNamespace(active_url=SimpleNamespace(active_url=url)),
    )
    # initView → populate_document
    b.populate_document = MagicMock()
    # initView → init_toolbox
    b.init_toolbox = MagicMock()
    # initView → self.layout.addWidget(self.viewer)
    # ``QWidget.layout`` is a builtin method by default; replace with
    # a fake QLayout that supports addWidget + setSpacing + setContentsMargins.
    b.layout = MagicMock()
    # initView → super().initView (NchantdOfficeDocument); skip it.
    super_initView = MagicMock()
    with patch.object(
        NchantdOfficeDocument := NchantdOfficeWebBrowser.__mro__[1],
        "initView",
        super_initView,
    ):
        pass
    b._super_initView_patch = super_initView
    return b


def _run(b, cfg=None):
    """Run the real ``initView`` with NchantdWebViewer + super().initView stubbed.

    Returns the cfg dict that initView passed to NchantdWebViewer.
    """
    captured = {}

    def fake_webviewer(parent_arg, cfg_arg):
        captured["cfg"] = cfg_arg
        v = MagicMock()
        v.initWidget = MagicMock()
        return v

    with patch(
        "nchantdoffice.widgets.documents.atnrg.browsers.NchantdWebViewer",
        side_effect=fake_webviewer,
    ), patch.object(
        NchantdOfficeWebBrowser.__mro__[1],
        "initView",
        return_value=None,
    ):
        NchantdOfficeWebBrowser.initView.__get__(b)(cfg=cfg)
    return captured["cfg"]


def test_initView_sets_links_in_place_default_true():
    """``cfg=None`` (no caller override) → links_in_place=True.

    Primary regression guard: a future commit that accidentally removes
    the default will fail this test.
    """
    b = _bare_browser()
    cfg = _run(b, cfg=None)
    assert cfg.get("links_in_place") is True, (
        f"initView should default links_in_place=True so popup/window.open "
        f"link clicks are redirected to the current view (nchantrs "
        f"_RedirectCapturePage) instead of being dropped by Qt's default "
        f"createWindow handling, which presents as a bounce-back. "
        f"Got cfg={cfg!r}"
    )


def test_initView_respects_caller_links_in_place_false():
    """Caller can opt out by passing ``links_in_place=False`` explicitly."""
    b = _bare_browser()
    cfg = _run(b, cfg={"links_in_place": False})
    assert cfg.get("links_in_place") is False, (
        f"caller-supplied links_in_place=False must be respected (the "
        f"default is True, but the .get(default, True) pattern only "
        f"applies when the key is missing). Got cfg={cfg!r}"
    )


def test_initView_preserves_other_cfg_keys():
    """Other cfg keys the caller passes should not be clobbered."""
    b = _bare_browser()
    cfg = _run(b, cfg={"some_other_key": "preserve_me"})
    assert cfg.get("some_other_key") == "preserve_me", (
        f"initView must not strip cfg keys the caller passed. Got cfg={cfg!r}"
    )
    assert cfg.get("links_in_place") is True, (
        f"default links_in_place=True should still be set when other "
        f"caller keys are present. Got cfg={cfg!r}"
    )



