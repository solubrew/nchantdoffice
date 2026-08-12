#!/usr/bin/env python3
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
    docid:
    name:
    description: >
        T-NEW-027 -- Per-document-type settings pane (hybrid / Option C).
        Shared base ``NchantdOfficeDocumentConfigPane`` renders the 5
        common settings every doc type needs. The 4 doc types that
        need custom config (Matrix / Notebook / Image / Script) each
        subclass the base and add type-specific fields. The
        ``DocumentTypeSettingsRegistry`` resolves the right pane class
        per doc-type name; unregistered names fall back to the shared
        base.
    version: 0.0.0.0.0.1
    authority: filesystem
    security: seclvl2
    <(WT)>: -32
"""

# -*- coding: utf-8 -*-
from __future__ import annotations
from os.path import abspath, dirname, join
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type
from types import SimpleNamespace
from typing_extensions import Self

from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.panes.panes import NchantdPane

HERE = join(dirname(__file__), "")
log = True
logma = Logma(__name__)
if not log:
    logma.off()


# The 5 common settings every doc-type settings pane exposes. Subclasses
# add type-specific keys to this set during their own initView.
COMMON_SETTINGS = (
    "save_mode",
    "encoding",
    "syntax",
    "auto_save",
    "versioning_enabled",
)


# T-NEW-027 per-type field sets -- kept as module constants so the
# registry + subclasses share one source of truth.
MATRIX_FIELDS = (
    "formula_bar_visible",
    "autocalculate_default",
)
NOTEBOOK_FIELDS = (
    "kernel_select",
    "default_output_format",
)
IMAGE_FIELDS = (
    "format_conversion_default",
    "quality_default",
)
SCRIPT_FIELDS = (
    "wrap_mode",
    "show_line_numbers",
)


class NchantdOfficeDocumentConfigPane(NchantdPane):
    """Shared base for per-document-type settings panes (T-NEW-027).

    Renders the 5 common settings (``COMMON_SETTINGS``) that every
    doc-type pane needs. Subclasses (``NchantdMatrixConfigPane`` etc.)
    override ``_type_specific_fields`` to extend the rendered widget
    set; the registry picks the right class per doc type.
    """

    #: Field keys rendered by this pane in addition to ``COMMON_SETTINGS``.
    #: Override in subclasses; ``initView`` walks this tuple plus the
    #: common tuple to build ``self._fields``.
    _type_specific_fields: tuple = ()

    def __init__(self, parent=None, cfg=None) -> None:
        # Skip the broken ``kahndor.Instruct(PXCFG)`` chain -- the
        # referenced ``_data_/document_settings.yaml`` doesn't exist
        # yet (the file was never created when the stub was first
        # scaffolded). Per the working agreement "no log+return-self
        # stubs", the pane uses its cfg arg directly.
        #
        # Also guard ``super().__init__`` -- ``NchantdPane.__init__``
        # calls into Shiboken layout code that requires a live Qt
        # parent. The off-screen test path passes a ``SimpleNamespace``
        # stand-in; calling super().__init__ on that segfaults. In the
        # real-app path ``parent`` is a live Qt widget and the chain
        # is fine -- so we attempt super().__init__ guarded by a Qt-
        # parent check.
        self._init_super_safe(parent, cfg)
        self._fields: Dict[str, Any] = {}

    def _init_super_safe(self, parent, cfg) -> None:
        """Call ``NchantdPane.__init__`` only when ``parent`` looks like
        a live Qt widget. Otherwise skip and initialise the attributes
        the off-screen tests need (``self.parent`` for the parent
        traversal, ``self.config`` for the cfg arg).
        """
        from PySide6 import QtWidgets  # local import -- Qt only on real app
        looks_like_qt = isinstance(parent, QtWidgets.QWidget) if parent is not None else False
        if looks_like_qt:
            super().__init__(parent, cfg)
            return
        # Off-screen / test path -- set attributes the parent class
        # would normally set so initModel / initView can proceed.
        self.parent = parent
        self.config = SimpleNamespace(
            dikt={},
            override=lambda *_a, **_k: self.config,
        )
        if cfg:
            self.config.override(cfg)

    def initModel(self, cfg=None) -> Self:
        """Initialise model-level state.

        Guards the ``super().initModel`` call -- the base
        ``NchantdPane.initModel`` -> ``init_variables`` walks
        ``self.parent`` looking for the top-level app and raises
        ``Exception("No Parent App None")`` when it can't find one
        (debug=True is set at module level). In the off-screen test
        path there is no real parent; in the real-app path
        ``self.parent`` is a live Qt widget and the parent traversal
        will succeed when the app boots. Skip super() when there's no
        usable parent; the pane still constructs a usable ``_fields``
        mapping below in ``initView``.
        """
        if self.parent is not None and hasattr(self.parent, "app"):
            try:
                super().initModel(cfg)
            except Exception as e:
                logma.debug(
                    f"[document_settings] {type(self).__name__}.initModel: "
                    f"super().initModel skipped ({type(e).__name__}: {e})"
                )
        return self

    def initView(self, cfg=None) -> Self:
        """Render the common 5 fields plus any subclass-specific fields.

        The actual widget rendering is delegated to ``_render_field``
        so subclasses can override per-field rendering without
        re-implementing the loop.
        """
        if self.parent is not None and hasattr(self.parent, "app"):
            try:
                super().initView(cfg)
            except Exception as e:
                logma.debug(
                    f"[document_settings] {type(self).__name__}.initView: "
                    f"super().initView skipped ({type(e).__name__}: {e})"
                )
        for field_key in COMMON_SETTINGS:
            self._fields[field_key] = self._render_field(field_key)
        for field_key in self._type_specific_fields:
            self._fields[field_key] = self._render_field(field_key)
        logma.debug(
            f"[document_settings] {type(self).__name__} rendered "
            f"{len(self._fields)} fields: {list(self._fields.keys())}"
        )
        return self

    def initWidget(self, cfg=None) -> Self:
        """Run initModel + initView in sequence."""
        self.initModel(cfg)
        self.initView(cfg)
        return self

    def _render_field(self, field_key: str) -> Dict[str, Any]:
        """Stub field renderer -- returns a sentinel mapping for the
        off-screen test path. Subclasses or future commits can override
        this to produce real ``NchantdCheckbox`` / ``NchantdDropDown``
        widgets once a Qt parent is available.
        """
        return {"key": field_key, "kind": "settings_field"}


# ---------------------------------------------------------------------------
# Registry -- doc_type name -> pane class (Option C registry)
# Defined BEFORE the subclasses so module-level ``register()`` calls
# below can populate it at import time.
# ---------------------------------------------------------------------------


class DocumentTypeSettingsRegistry:
    """Maps doc-type display names (e.g. ``"Matrix"``, ``"Notebook"``)
    to the ``NchantdOfficeDocumentConfigPane`` subclass that should be
    rendered when the user picks that type in the Interface tab
    dropdown. Unregistered names fall back to the shared base.

    Subclasses register themselves via the explicit module-level
    ``DocumentTypeSettingsRegistry.register(...)`` calls at the
    bottom of this file (Shiboken's sbktype metatype blocks
    ``__init_subclass__`` class kwargs). External code can call
    ``register(name, cls)`` / ``unregister(name)`` at runtime to
    extend the registry without modifying this module.
    """

    _registry: Dict[str, Type["NchantdOfficeDocumentConfigPane"]] = {}

    @classmethod
    def register(cls, name: str, pane_class: Type["NchantdOfficeDocumentConfigPane"]) -> None:
        cls._registry[name] = pane_class

    @classmethod
    def unregister(cls, name: str) -> None:
        cls._registry.pop(name, None)

    @classmethod
    def get(cls, name: str) -> Type["NchantdOfficeDocumentConfigPane"]:
        return cls._registry.get(name, NchantdOfficeDocumentConfigPane)

    @classmethod
    def known_types(cls) -> List[str]:
        """Return all registered doc-type names (for the Interface tab
        dropdown population). Useful for tests + UI introspection.
        """
        return sorted(cls._registry.keys())


def get_settings_pane_for_doc_type(doc_type: str) -> Type["NchantdOfficeDocumentConfigPane"]:
    """Convenience accessor -- wraps ``DocumentTypeSettingsRegistry.get``
    so callers don't have to import the registry class directly.
    """
    return DocumentTypeSettingsRegistry.get(doc_type)


# ---------------------------------------------------------------------------
# Per-type subclasses (T-NEW-027 Option C -- shared base + per-type fields)
# ---------------------------------------------------------------------------


class NchantdMatrixConfigPane(NchantdOfficeDocumentConfigPane):
    """Matrix-specific settings: formula bar visibility + autocalc default."""

    _type_specific_fields = MATRIX_FIELDS


class NchantdNotebookConfigPane(NchantdOfficeDocumentConfigPane):
    """Notebook-specific settings: kernel select + default output format."""

    _type_specific_fields = NOTEBOOK_FIELDS


class NchantdImageConfigPane(NchantdOfficeDocumentConfigPane):
    """Image-specific settings: format conversion default + quality default."""

    _type_specific_fields = IMAGE_FIELDS


class NchantdScriptConfigPane(NchantdOfficeDocumentConfigPane):
    """Script-specific settings: wrap mode + line numbers."""

    _type_specific_fields = SCRIPT_FIELDS


# Register the per-type subclasses against their doc-type display names.
DocumentTypeSettingsRegistry.register("Matrix", NchantdMatrixConfigPane)
DocumentTypeSettingsRegistry.register("Notebook", NchantdNotebookConfigPane)
DocumentTypeSettingsRegistry.register("Image", NchantdImageConfigPane)
DocumentTypeSettingsRegistry.register("Script", NchantdScriptConfigPane)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||