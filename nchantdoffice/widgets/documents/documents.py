# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
        docid:
        name:
        description: >
        version: 0.0.0.0.0.0
        authority: filesystem
        security: seclvl2
        <(WT)>: -32
"""

# -*- coding: utf-8 -*
from __future__ import annotations

# ======================================Standard Library Modules======================================================||
from os.path import dirname, join
from copy import deepcopy
import json as j

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.managers import NchantdManager
from kahndor.logma import Logma
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantdoffice.widgets.panes.documents import NchantdOfficeTabEditPane, NchantdOfficeNoteEditPane
from nchantdoffice.widgets.panes.documents import NchantdOfficeNodeEditPane
from nchantdoffice.widgets.tabs import NchantdOfficeTab

# T-NEW-XXX: NchantdOfficeNote is imported inside ``set_notes``
# (below) to avoid a circular import with
# ``nchantdoffice.widgets.documents.media.notes``.
from pyffice.document import PyfficeDocument
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.controls.buttons import NchantdButton
from typing import Any, Iterator, Self

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
debug = True
log = False
if not log:
    logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "documents.yaml")


class NchantdOfficeDocumentMixin:
    """Nchantd Office Document contains elements to create virtual documents to be stored. This is primarily to handle
    storage and generally will equate to what is shown in a tab"""

    def init_variables(self, name=None) -> Self:
        """ """
        super().init_variables()
        # self.app = pyqt.QApplication.instance()
        self.button_bar = None
        self.context = None
        self.document = None
        self.document_name = name
        self.document_editor = None
        self.document_initialized = False
        self.document_toolbar = None
        self.document_type = "base"
        self.data = None
        self.file_path = None
        self.file_type = None
        self.toolbox = None
        self.toolbox_config = None
        # T-NEW-003 (save_mode toggle): default to ``"file_path"`` so
        # brand-new documents behave the way they did before the
        # toggle (the external file is the source of truth, the DB
        # row records the file_path reference). The toggle lives in the
        # TabEdit Pane of the Document Config Drawer; ``set_save_mode``
        # updates this attribute AND persists it on the document's
        # config so it round-trips through ``cmd_open_local_file``.
        self.save_mode = "file_path"
        self.has_pro = (
            getattr(self.app.model.user, "has_pro", False)
            if self.app and self.app.model and self.app.model.user
            else False
        )

    def initModel(self, cfg=None, objects=None) -> Self:
        """ """
        super().initModel(cfg)  # Pass through usage even though the Mixin has no permeate parent class
        self.toolbox_config = self.config.dikt.get("toolbox", None)
        # T-NEW-003: thread ``self.file_path`` from the canonical sources
        # in priority order:
        #   1. ``self.document.file_path`` when a Pyffice document is
        #      already attached (this is what ``PyfficeDocument.set_file_path``
        #      sets after a real ``open_file`` round-trip).
        #   2. ``self.config.dikt["file_path"]`` for new-document create
        #      paths where the on-disk file does not exist yet and
        #      ``PyfficeDocument.set_file_path`` is a no-op.
        doc_path = getattr(getattr(self, "document", None), "file_path", None)
        cfg_path = self.config.dikt.get("file_path", None)
        self.set_file_path(doc_path or cfg_path)
        # T-NEW-003: thread ``save_mode`` so it round-trips across
        # save/load. Priority:
        #   1. ``self.document.config.dikt["save_mode"]`` if the
        #      Pyffice document carries a persisted value.
        #   2. ``self.config.dikt["save_mode"]`` for new documents
        #      whose Pyffice config hasn't been written yet.
        #   3. Default ``"file_path"`` for legacy documents that pre-
        #      date the toggle.
        doc_cfg = getattr(getattr(self, "document", None), "config", None)
        doc_save_mode = None
        if doc_cfg is not None and hasattr(doc_cfg, "dikt"):
            doc_save_mode = doc_cfg.dikt.get("save_mode")
        cfg_save_mode = self.config.dikt.get("save_mode")
        self.save_mode = doc_save_mode or cfg_save_mode or "file_path"
        self.data = {}
        self.context_menu_name = "context.document"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        # Fix: Enable context menu policy for right-click to work
        self.setContextMenuPolicy(pyqt.Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        super().initView(cfg)
        if self.config.dikt.get("default_toolbar", True):
            self.init_toolbar(cfg)
        self.init_toolbox()
        return self

    def initWidget(self, pos=0) -> Self:
        """ """
        self.initModel()
        self.initView()
        return self

    def align_left(self, selection="") -> Self:
        """Align text selection to the left within the document editor."""
        if self.document_editor is not None:
            cursor = self.document_editor.textCursor()
            fmt = pyqt.QTextBlockFormat()
            fmt.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)
            cursor.mergeBlockFormat(fmt)
            self.on_document_changed()
        return self

    def align_center(self, selection="") -> Self:
        """Align text selection to the center within the document editor."""
        if self.document_editor is not None:
            cursor = self.document_editor.textCursor()
            fmt = pyqt.QTextBlockFormat()
            fmt.setAlignment(pyqt.Qt.AlignmentFlag.AlignCenter)
            cursor.mergeBlockFormat(fmt)
            self.on_document_changed()
        return self

    def align_right(self, selection="") -> Self:
        """Align text selection to the right within the document editor."""
        if self.document_editor is not None:
            cursor = self.document_editor.textCursor()
            fmt = pyqt.QTextBlockFormat()
            fmt.setAlignment(pyqt.Qt.AlignmentFlag.AlignRight)
            cursor.mergeBlockFormat(fmt)
            self.on_document_changed()
        return self

    def cmd_cancel(self) -> Self:
        """Cancel current document operation and revert unsaved changes."""
        if hasattr(self, "document_editor") and self.document_editor is not None:
            self.document_editor.setText("")
        if hasattr(self, "app") and self.app:
            self.app.model.has_changed = False
        return self

    def cmd_delete_tab(self, event, *args, **kwargs) -> None:
        """"""
        self.app.model.delete_tab(self)

    def cmd_open_local_file(self, event=None, *args, **kwargs) -> Self:
        """"""
        cfg = {}
        self.open_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.open_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
        return self

    def cmd_node_edit(self, event=None, *args, **kwargs) -> Self:
        """Open the node editor for the current document's tree node."""
        if hasattr(self, "app") and self.app:
            if hasattr(self.app.view, "panes") and "left" in self.app.view.panes:
                tree = getattr(self.app.view.panes["left"], "tree", None)
                if tree and hasattr(tree, "model") and tree.model.current_node:
                    node = tree.model.current_node
                    cfg = {"node": node, "document": self.document}
                    editor = NchantdOfficeNodeEditPane(self, cfg)
                    editor.initWidget()
        return self

    def cmd_redo(self, event=None, *args, **kwargs) -> Self:
        """Redo the last undone action in the document editor."""
        if self.document_editor is not None:
            doc = self.document_editor.document()
            if doc.isRedoAvailable():
                doc.redo()
        return self

    def cmd_show_pane_left(self, event=None, *args, **kwargs) -> Self:
        """"""
        if self.app.view.panes["left"].isHidden():
            self.app.view.panes["left"].show()
        else:
            self.app.view.panes["left"].hide()
        return self

    def cmd_show_pane_right(self, event=None, *args, **kwargs) -> Self:
        """"""
        if self.app.view.panes["right"].isHidden():
            self.app.view.panes["right"].show()
        else:
            self.app.view.panes["right"].hide()
        return self

    def cmd_tag_edit(self, event=None, *args, **kwargs) -> Self:
        """Open tag editor for the current document."""
        if hasattr(self, "app") and self.app and hasattr(self.app, "model"):
            tags = getattr(self.document, "tags", []) if self.document else []
            cfg = {"tags": tags, "document": self.document}
            editor = NchantdOfficeNoteEditPane(self, cfg)
            editor.initWidget()
            self.on_document_changed()
        return self

    def cmd_undo(self, event=None, *args, **kwargs) -> Self:
        """Undo the last action in the document editor."""
        if self.document_editor is not None:
            doc = self.document_editor.document()
            if doc.isUndoAvailable():
                doc.undo()
        return self

    def cmd_save_tab(self, event=None, *args, **kwargs) -> None:
        """ "" """
        self.save()

    def create_data_table(self) -> "DataFrame":
        """"""
        df = DataFrame()
        return df

    def defocus(self) -> Self:
        """Remove focus from the document widget and trigger save if needed."""
        if self.document_editor is not None:
            self.document_editor.clearFocus()
        self.on_lost_focus()
        return self

    def export_document(self) -> Self:
        """Export a single selected document to an external file of the selected format."""
        if self.document is None:
            logma.warning("No document to export")
            return self
        file_path, selected_filter = pyqt.QFileDialog.getSaveFileName(
            self, "Export Document", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            doc_data = self.document.to_dict() if hasattr(self.document, "to_dict") else str(self.document.content)
            with open(file_path, "w", encoding="utf-8") as f:
                j.dump(doc_data, f, indent=2, default=str)
            logma.info(f"Exported document to {file_path}")
        return self

    def get_bytes(self) -> bytes:
        """Return document content as bytes for storage or transmission."""
        if self.document is None:
            return bytes()
        content = self.document.content if hasattr(self.document, "content") else ""
        if isinstance(content, bytes):
            return content
        if isinstance(content, str):
            return content.encode("utf-8")
        return j.dumps(content, default=str).encode("utf-8")

    def get_primary_key(self) -> Self:
        """"""
        self.primary_key = self.app.model.get_primary_key(self.uuid)
        return self.primary_key

    def import_document(self) -> Self:
        """Import a document from an external file."""
        file_path, _ = pyqt.QFileDialog.getOpenFileName(
            self, "Import Document", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()
            try:
                doc_data = j.loads(raw)
            except j.JSONDecodeError:
                doc_data = {"content": raw, "format": "text"}
            if self.document is not None and hasattr(self.document, "content"):
                self.document.content = doc_data.get("content", raw)
            self.on_document_changed()
            logma.info(f"Imported document from {file_path}")
        return self

    def init_drawer(self, name) -> dict[str, Any]:
        """Initialize a named drawer section in the toolbox."""
        if self.toolbox_config is None:
            self.toolbox_config = {}
        drawer_id = None
        for key, drawer in self.toolbox_config.items():
            if isinstance(drawer, dict) and drawer.get("name") == name:
                drawer_id = key
                break
        if drawer_id is None:
            drawer_id = max(self.toolbox_config.keys(), default=-1) + 1
            self.toolbox_config[drawer_id] = {"name": name, "items": {}}
        drawer = self.toolbox_config[drawer_id]
        if "items" not in drawer:
            drawer["items"] = {}
        return drawer

    def init_toolbar(self, cfg=None) -> Self:
        """"""
        if cfg is None:
            cfg = {}
        # Ensure we have app reference - try to get it from parent if not set
        # if not hasattr(self, "app") or self.app is None:
        #     if hasattr(self, "parent") and self.parent is not None:
        #         self.app = getattr(self.parent, "app", None)
        _buttons = {
            0: {"action": "show_pane_left", "handler": self.cmd_show_pane_left},
            # DEBUG the open file dialog is not respecting close/cancel commands
            100: {"action": "open_local", "handler": self.cmd_open_local_file},
            101: {
                # T-NEW-038: pick the action that matches the
                # document's storage location. For internal
                # (SQLite) docs the action table maps to the
                # database-save icon; for external (file on disk)
                # the legacy save.svg icon. The legacy hard-coded
                # "save" is preserved for unknown / missing docs.
                "action": self._save_action(self.document),
                "handler": self.cmd_save_tab,
            },
            # PUSH to 0.0.3 150: {"action": "redo", "handler": self.cmd_redo},
            # PUSH to 0.0.3 200: {"action": "undo", "handler": self.cmd_undo},
            400: {"action": "cancel", "handler": self.cmd_delete_tab},
            1000: {"action": "show_pane_right", "handler": self.cmd_show_pane_right},
        }
        buttons = (
            kahndor.Instruct(self.config.get("buttons", {})).override(_buttons).override(cfg.get("buttons", {})).dikt
        )
        # T-037: per-document-type pro-feature routing. The
        # ``profile`` dropdown is populated dynamically from the
        # document type's registered pro-feature set rather than
        # being a hard-coded single "default" option.
        if self.has_pro:
            profile_options = self._get_pro_profile_options()
            cfg = {
                "label": "Profile",
                "layout": "horizontal",
                "size": [10, 20],
                "drop_down": {"size": [100, 20]},
                "options": self._get_pro_profile_options(),
            }
            self.profile_select_entry = NchantdDropDown(self, cfg).initWidget()
            buttons[1] = {"name": "get_pro", "widget": self.profile_select_entry}
        else:
            # Sprint 28: deferred import to break the
            # nchantdoffice.widgets.documents.documents <-> .advertisements
            # import cycle. advertisements.advertisements already
            # imports NchantdOfficeDocument from this module.
            from nchantdoffice.widgets.advertisements import (
                NchantdOfficeAdTab,
            )

            cfg = {
                "text": "Get Pro",
                # Wire the toolbar "Get Pro" button to the
                # same navigation the Ad tab uses
                # (``NchantdOfficeAdTab.redirect_to_get_pro``).
                # The helper resolves
                # ``app.view.panes["left"].tree.view`` (the
                # NchantdTreeView wrapper) and calls
                # ``set_current_node`` to actually update the
                # center tabset.
                "handler": (lambda *a, _self=self, **k: NchantdOfficeAdTab.redirect_to_get_pro(_self.app)),
                "height": 24,
                # T-NEW-134 followup: dark orange (``#FF8C00``) instead
                # of green. Orange reads as an upsell / offer (the
                # universal ecommerce conversion color -- Stripe,
                # Shopify, GitHub Pro all use it); green reads as
                # success / approved which doesn't carry the same
                # "click me, you're paying for this" intent. White
                # text on the saturated fill keeps the contrast
                # legible at the toolbar's 24px height.
                "background_color": "#FF8C00",
            }
            self.profile_select_entry = NchantdButton(self, cfg).initWidget()
            # T-NEW-134: the cfg sets ``background_color`` but the
            # upstream ``NchantdButton.initView`` doesn't read it
            # (the key is dead config). Apply the color via
            # ``setStyleSheet`` so the rendered button is visibly
            # orange. Pair with white text for legibility on the
            # saturated fill.
            self._apply_bg_color(
                self.profile_select_entry,
                cfg.get("background_color"),
            )
            buttons[1] = {"name": "get_pro_features", "widget": self.profile_select_entry}
        cfg = {"layout": "horizontal", "justify": "right"}
        buttons = {k: buttons[k] for k in sorted(buttons)}
        self.document_toolbar = NchantdButtonBar(self, cfg).initWidget(buttons)
        self.document_toolbar.setFixedHeight(30)
        self.layout.addWidget(self.document_toolbar)
        return self

    def init_toolbox(self, cfg=None) -> Self:
        """"""
        self.config.override(cfg)
        if self.toolbox_config is None:
            self.toolbox_config = self.app.model.toolbox_config.get("document", None)
        if self.toolbox_config is None:
            logma.warning("No toolbox config found for document, using empty default")
            self.toolbox_config = {}
        logma.info(f"Toolbox Config {self.toolbox_config.keys()}")
        self.toolbox_config[50]["items"] = self.init_drawer_file_config()
        return self

    def init_drawer_file_config(self) -> dict[str, Any]:
        """"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.toolbox_config[50].get("items", {})
        try:
            cnt = 0
            if cnt not in items:
                items[cnt] = default_action
            cfg = {"layout": "horizontal"}
            self.node_edit_pane = NchantdOfficeNodeEditPane(self, cfg)
            items[cnt]["widget"] = self.node_edit_pane
            cnt += 1
        except Exception as e:
            logma.warning(f"Nchantd Office Node Edit Pane failed {e}")
        try:
            if cnt not in items:
                items[cnt] = default_action
            cfg = {"layout": "horizontal"}
            self.tab_edit_pane = NchantdOfficeTabEditPane(self, cfg)
            items[cnt]["widget"] = self.tab_edit_pane
            cnt += 1
        except Exception as e:
            logma.warning(f"Nchantd Office Tab Edit Pane failed {e}")
        # PUSH to 0.0.3
        # if cnt not in items:
        #     items[cnt] = default_action
        # cfg = {"layout": "horizontal", "handler": self.cmd_tag_edit}
        # self.note_edit_pane = NchantdOfficeNoteEditPane(self, cfg)
        # items[cnt]["widget"] = self.note_edit_pane
        # cnt += 1
        return items

    def lock_page(self) -> Self:
        """Lock the current document page to prevent editing."""
        if self.document_editor is not None:
            self.document_editor.setReadOnly(True)
        if self.document is not None and hasattr(self.document, "locked"):
            self.document.locked = True
        return self

    def on_document_changed(self) -> Self:
        """

        when there is a change to the document but the changes into the local cache for easier undo/redo logic
        when a document loses focus the changes will be transferred from the local cache to the save process

        :return:
        """
        self.app.model.has_changed = True
        return self

    def on_gain_focus(self) -> Self:
        """Update document when it gains focus to reflect any edits made elsewhere."""
        if self.document is not None and hasattr(self.app, "model"):
            stored = self.app.model.get_document(self.document.did) if hasattr(self.app.model, "get_document") else None
            if stored is not None and hasattr(stored, "content"):
                if self.document_editor is not None:
                    self.document_editor.setPlainText(str(stored.content))
        self.setFocus()
        return self

    def on_lost_focus(self) -> Self:
        """Save document when focus is lost, based on user settings."""
        auto_save = self.config.dikt.get("auto_save_on_blur", True) if hasattr(self, "config") else True
        if auto_save and self.document is not None:
            if self.document_editor is not None and hasattr(self.document, "content"):
                self.document.content = self.document_editor.toPlainText()
            self.save_internal()
        return self

    def register(self) -> Self:
        """"""
        self.app.model.store.register_document(self.document)
        return self

    def save(self, path=None, format_=None, encrypt=False) -> Self:
        """
        Save method saves the current document in its most recent format ie internal or external file saving
        this can be different than a store_document command

        :return:
        """
        if self.document is None:
            return self
        # PII / secrets guard: log metadata only, never the payload body
        # or stored content blob.
        try:
            content = self.document.content if self.document is not None else None
        except Exception:
            content = None
        if isinstance(content, (dict, list, str, bytes, int, float, type(None))):
            content_repr = type(content).__name__
        else:
            content_repr = "unknown"
        logma.info(
            f"Save Content type={content_repr} "
            f"keys={list(content.keys())[:5] if isinstance(content, dict) else 'n/a'}"
        )
        logma.info(f"Save Path {path}")
        # Guard for widgets that fundamentally don't support file_path-based saving
        # (e.g., JournalEditor doesn't have this attribute at all).
        # Only skip if the attribute literally doesn't exist - NOT if it's None.
        # Widgets like browsers should still save to DB even without file_path.
        if not hasattr(self, "file_path"):
            logma.debug("[documents] save_app: no file_path attribute, skipping app-level save")
            return self
        if path is not None:
            self.set_file_path(path)
            if hasattr(self.document, "set_file_path"):
                self.document.set_file_path(path)
            else:
                self.document.file_path = path
        elif self.file_path is None:
            self.file_path = getattr(self.document, "file_path", None)
        # Note: we intentionally allow saving to DB even when file_path is None.
        # Widgets like browsers save content to DB without a file_path.
        if not hasattr(self, "app") or self.app is None or not hasattr(self.app, "view"):
            return self
        if self.app.view.panes["left"].tree.model.current_node is None:
            return self
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        logma.info(f"Save PID {pid}")
        if self.app.view.panes["center"].model.current_tab is None:
            return self
        pos = self.app.view.panes["center"].model.current_tab.position
        logma.info(f"Save Pos {pos}")
        logma.info(f"Save DID {self.document.did}")
        # T-NEW-012 followup: invoke the widget's ``get_content()``
        # so subclass overrides (e.g. NchantdOfficeWebBrowser,
        # NchantdOfficeNotebook) populate ``self.document.content``
        # before persistence. Previously the mixin went straight
        # to ``store_document`` which serialised the (often stale
        # or empty) ``self.document.content`` directly, so the
        # Browser/Notebook overrides were never actually used on
        # save. The single-window ``get_content()`` here restores
        # the canonical "widget -> set_content -> save" flow.
        try:
            widget_content = self.get_content()
        except Exception as e:
            widget_content = None
            logma.error(f"[documents] save: get_content failed: {e}", exc_info=True)
        if widget_content and self.document is not None:
            try:
                self.document.set_content(widget_content)
            except Exception as e:
                logma.error(f"[documents] save: set_content failed: {e}", exc_info=True)
        # T-NEW-003 (35c050e4 working form): always write the
        # external file (when file_path is set) AND always write
        # the DB row. The two writes serve different purposes —
        # the file is the user-edited source of truth, the DB
        # row carries ``doc_media_content.content_enc64_txt``
        # which lets the document be recovered if the on-disk
        # file is deleted/moved and lets the doc be queried via
        # SQL. Skipping the DB write (the save_mode="file_path"
        # behaviour added in H60) leaves ``content_enc64_txt``
        # empty and breaks the reopen path when the external
        # file is unavailable.
        self.document.save(self.file_path)  # increments versions and (internal encryption..future)
        # T-NEW-039: the doc_media syntax sync now lives in
        # ``NchantdOfficeCloakModel.store_document`` (T-NEW-024)
        # -- a single ``UPDATE doc_media SET syntax_txt = ? WHERE
        # did = ?`` is now part of the canonical save path. No
        # more widget-side ``update_doc_media_syntax`` call -
        # the model owns the write.
        self.app.model.store_document(self.document)
        return self

    def save_app(self, path=None, format_=None, encrypt=False) -> Self:
        """
        Full-text save path for app_media documents. Persists
        ``self.document`` via ``self.document.save(path)`` (which
        increments the version and writes the body) and then calls
        ``self.app.model.store_document(self.document, True)`` so
        the row lands in ``app_doc_content`` / ``app_media_content``
        (the ``True`` flag means "store to app_doc", NOT
        ``doc_media_content``).

        **Why this method exists alongside ``super().save()``:**

        - ``super().save()`` (inherited from NchantdOfficeDocument)
          persists the same document via the *doc_media_content*
          path. That is the correct path for a normal document
          (browser tab, script, image, etc.).
        - ``save_app()`` is the correct path for documents that
          the user wants to save as **app-scoped content** rather
          than doc-scoped content. The journal is the canonical
          example: a journal entry is owned by the application
          (Home / Journal / Settings root), not by a single doc
          tab, so it must live in ``app_media_content`` -- never
          in ``doc_media_content``.

        **Do NOT call both ``super().save()`` and ``self.save_app()``**
        on the same document. The two paths write to different
        tables but the same model object, and dedupe is by
        (pUUID, version) across the `_content` tables. A
        double-write would either land two rows that reference
        the same content or, worse, push the wrong payload to
        the wrong table (the live T-NEW-079 regression: the
        journal save once called ``super().save()`` and put
        ordinary file-handle strings into ``doc_media_content``,
        which is not the journal's table).

        **Callers (the canonical pattern):**

        - ``NchantdOfficeJournalEditor.save()`` -- the journal is
          an app_media document. It calls ``self.save_app()``
          only -- that is the entire save contract. Per the user
          directive in commits ``9e74486`` / ``cb6ebb9``, the
          ``super().save()`` call was removed because it persisted
          to ``doc_media_content`` (the wrong table for a journal
          entry), and the try/except wrappers around
          ``save_app()`` and ``_parse_entry()`` were also removed
          so a save_app failure propagates to the Qt event loop
          instead of being silently dropped. The result: any
          failure in the journal save path is loud, not silent,
          and the user's text is never lost to a swallowed
          exception.
        - ``NchantdOfficeJournalAppendEditor.add_entry()`` -- the
          inner append editor's ``add_entry`` method mirrors the
          new entry to BOTH ``self.parent.pages`` (the editor's
          in-memory alias) AND ``self.parent.document.pages``
          (the persisted Pyffice document). The second write is
          what makes the entry land in
          ``app_media_content.content_enc64_txt`` via the outer
          ``save()`` chain. Without the document mirror the entry
          was in memory only and lost on reopen -- see
          commit ``374c6eb`` and
          ``tests/test_journal_add_entry_mirrors_to_document.py``.
        - ``NchantdOfficeWebBrowser.save()`` -- the browser is
          also an app_media document. ``save_app()`` writes the
          full URL + page payload to ``app_media_content`` so a
          reopen can restore the page.

        **PII / secrets guard (defensive):** the logger records
        only the content type and top-level keys, never the
        payload body.

        **Returns self** for chainable callers.
        """
        if self.document is None:
            return self
        # PII / secrets guard: log metadata only, never the payload body
        # or stored content blob.
        try:
            content = self.document.content if self.document is not None else None
        except Exception:
            content = None
        if isinstance(content, (dict, list, str, bytes, int, float, type(None))):
            content_repr = type(content).__name__
        else:
            content_repr = "unknown"
        logma.info(
            f"Save Content type={content_repr} "
            f"keys={list(content.keys())[:5] if isinstance(content, dict) else 'n/a'}"
        )
        logma.info(f"Save Path {path}")
        # Guard for widgets that fundamentally don't support file_path-based saving
        # (e.g., JournalEditor doesn't have this attribute at all).
        # Only skip if the attribute literally doesn't exist - NOT if it's None.
        # Widgets like browsers should still save to DB even without file_path.
        # if not hasattr(self, "file_path"):
        #     logma.debug("[documents] save_app: no file_path attribute, skipping app-level save")
        #     return self
        if path is not None:
            self.set_file_path(path)
            if hasattr(self.document, "set_file_path"):
                self.document.set_file_path(path)
            else:
                self.document.file_path = path
        elif self.file_path is None:
            self.file_path = getattr(self.document, "file_path", None)
        # Note: we intentionally allow saving to DB even when file_path is None.
        # Widgets like browsers save content to DB without a file_path.
        if not hasattr(self, "app") or self.app is None or not hasattr(self.app, "view"):
            return self
        if self.app.view.panes["left"].tree.model.current_node is None:
            return self
        # pid = self.app.view.panes["left"].tree.model.current_node.nid
        # logma.info(f"Save PID {pid}")
        # if self.app.view.panes["center"].model.current_tab is None:
        #     return self
        # pos = self.app.view.panes["center"].model.current_tab.position
        # logma.info(f"Save Pos {pos}")
        # logma.info(f"Save DID {self.document.did}")
        # try:
        #     widget_content = self.get_content()
        # except Exception as e:
        #     widget_content = None
        #     logma.error(f"[documents] save: get_content failed: {e}", exc_info=True)
        # if widget_content and self.document is not None:
        #     try:
        #         self.document.set_content(widget_content)
        #     except Exception as e:
        #         logma.error(f"[documents] save: set_content failed: {e}", exc_info=True)
        self.document.save(self.file_path)  # increments versions and (internal encryption..future)
        self.app.model.store_document(self.document, True)  # True stors to app_doc
        return self

    def set_save_mode(self, mode) -> Self:
        """Update ``self.save_mode`` and persist it on the document config.

        Called by the TabEdit Pane checkbox handler. Returns ``self``
        for chainable callers.

        ``mode`` must be one of ``"file_path"``, ``"to_dict"``, or
        ``"both"``. Unknown values are rejected with a warning and
        the existing ``save_mode`` is preserved (so a typo in the
        UI doesn't silently change behaviour).
        """
        valid = {"file_path", "to_dict", "both"}
        if mode not in valid:
            logma.warning(
                f"[documents] set_save_mode: rejected unknown mode={mode!r}; "
                f"expected one of {sorted(valid)}; keeping existing {self.save_mode!r}"
            )
            return self
        self.save_mode = mode
        # Persist on the widget config so it round-trips.
        if hasattr(self, "config") and hasattr(self.config, "dikt"):
            self.config.dikt["save_mode"] = mode
        # Persist on the Pyffice document config too — the document
        # round-trips through ``PyfficeDocument.to_dict()`` /
        # ``load_document()`` and the TabEdit pane reads it back
        # across sessions.
        doc_cfg = getattr(getattr(self, "document", None), "config", None)
        if doc_cfg is not None and hasattr(doc_cfg, "dikt"):
            doc_cfg.dikt["save_mode"] = mode
        logma.info(f"[documents] save_mode set to {mode!r}")
        return self

    def save_external(self) -> Self:
        """Save document to an external file path."""
        if self.document is None:
            return self
        if self.file_path is None:
            file_path, _ = pyqt.QFileDialog.getSaveFileName(
                self, "Save Document", "", "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
            )
            if not file_path:
                return self
            self.set_file_path(file_path)
        doc_data = (
            self.document.to_dict() if hasattr(self.document, "to_dict") else {"content": str(self.document.content)}
        )
        with open(self.file_path, "w", encoding="utf-8") as f:
            j.dump(doc_data, f, indent=2, default=str)
        logma.info(f"Saved external document to {self.file_path}")
        return self

    def save_internal(self) -> Self:
        """Persist the active Pyffice document through the model API."""
        self.app.model.store_document(self.document)
        return self

    def save_as(self, name, path=None) -> Self:
        """Create a copy of the document under a new name and optional path."""
        if self.document is None:
            logma.warning("save_as called with no document")
            return self
        if path is None:
            path = dirname(self.path) if self.path else getattr(self.app, "base_path", "")
        target_path = join(path, name)
        doc_dict = self.document.to_dict() if hasattr(self.document, "to_dict") else {"content": str(self.document)}
        doc_dict["path"] = target_path
        if hasattr(self.app, "model") and hasattr(self.app.model, "store_document"):
            self.app.model.store_document(doc_dict)
        logma.info(f"Document saved as {target_path}")
        self.path = target_path
        return self

    def save_copy_as(self, name, path=None) -> Self:
        """Create a copy of the document without changing the current document state."""
        if self.document is None:
            logma.warning("save_copy_as called with no document")
            return self
        if path is None:
            path = dirname(self.path) if self.path else getattr(self.app, "base_path", "")
        target_path = join(path, name)
        doc_dict = self.document.to_dict() if hasattr(self.document, "to_dict") else {"content": str(self.document)}
        doc_dict["path"] = target_path
        doc_dict["did"] = None
        doc_dict.pop("uuid", None)
        if hasattr(self.app, "model") and hasattr(self.app.model, "store_document"):
            self.app.model.store_document(doc_dict)
        logma.info(f"Document copy saved as {target_path}")
        return self

    def set_file_path(self, path) -> Self:
        """ """
        self.file_path = path
        return self

    # def store_document(self):
    #     """"""
    #     self.app.model.store.store_document(self.document)
    #     return self

    def take_snapshot(self) -> str | None:
        """Capture a PNG snapshot of the current document widget.

        T-038: grabs the document_editor's pixmap via QWidget.grab()
        and saves it to ``self.snapshot_path`` (or a temp file when
        no path is set). Returns ``self.snapshot_path`` on success,
        ``None`` on failure.
        """
        try:
            target = (
                getattr(self, "document_editor", None) or getattr(self, "browser", None) or getattr(self, "image", None)
            )
            if target is None or not hasattr(target, "grab"):
                logma.warning("[documents] take_snapshot: no grabbable widget")
                return None
            pixmap = target.grab()
            if pixmap is None or pixmap.isNull():
                logma.warning("[documents] take_snapshot: pixmap is null")
                return None
            path = getattr(self, "snapshot_path", None) or (
                self.config.dikt.get("snapshot_path") if hasattr(self, "config") else None
            )
            if not path:
                import os, tempfile

                path = os.path.join(tempfile.gettempdir(), "nchantdoffice_snapshot.png")
            if pixmap.save(path, "PNG"):
                self.snapshot_path = path
                logma.info(f"[documents] take_snapshot: saved {path}")
                return path
            logma.warning(f"[documents] take_snapshot: failed to save pixmap to {path}")
            return None
        except Exception as e:
            logma.error(f"[documents] take_snapshot failed: {e}", exc_info=True)
            return None

    def unlock_page(self) -> Self:
        """Unlock the current document page to allow editing."""
        if self.document_editor is not None:
            self.document_editor.setReadOnly(False)
        if self.document is not None and hasattr(self.document, "locked"):
            self.document.locked = False
        return self

    def update_document(self) -> Self:
        """Refresh the current document state from the underlying store."""
        if self.document is None or not hasattr(self.document, "did"):
            return self
        if not hasattr(self.app, "model"):
            return self
        stored = self.app.model.get_document(self.document.did) if hasattr(self.app.model, "get_document") else None
        if stored is None:
            return self
        if self.document_editor is not None and hasattr(stored, "content"):
            self.document_editor.setPlainText(str(stored.content))
        if hasattr(stored, "to_dict"):
            for key, value in stored.to_dict().items():
                if hasattr(self.document, key) and key not in ("did", "uuid"):
                    setattr(self.document, key, value)
        return self

    def update_document_page(self, page_num) -> Self:
        """Update display/state for a specific document page.
        NOTE: this codebase currently uses a single-page editor; multi-page support
        is a future feature. For page_num == 0 (current), we refresh from store; for
        any other page_num we log a warning until multi-page support lands.
        """
        if page_num == 0:
            return self.update_document()
        logma.warning(f"update_document_page({page_num}) called but multi-page support is not implemented")
        return self

    @staticmethod
    def _apply_bg_color(button, color) -> None:
        """T-NEW-134 helper: apply a background color to a
        button via ``setStyleSheet`` so the rendered button is
        visibly tinted.

        Accepts either a named CSS color (``"orange"``,
        ``"red"``, ...) or a hex string (``"#FF8C00"``). Pairs
        the background with ``color: white`` for contrast on
        saturated fills -- an orange Get Pro button without a
        contrasting text is hard to read.

        The T-NEW-134 cfg ships dark orange (``#FF8C00``)
        because orange is the universal ecommerce upsell
        color (Stripe / Shopify / GitHub Pro all use it);
        green reads as success / approved which doesn't carry
        the same conversion intent.

        No-op when ``color`` is None / empty / whitespace --
        missing config must never apply an empty stylesheet
        (which Qt would otherwise log as a malformed rule).
        """
        if not color:
            return
        if not isinstance(color, str) or not color.strip():
            return
        # Normalize: strip whitespace, pass through verbatim
        # (Qt accepts both CSS named colors and hex literals).
        css_color = color.strip()
        stylesheet = f"QPushButton {{ background-color: {css_color}; " f"color: white; }}"
        try:
            button.setStyleSheet(stylesheet)
        except Exception as e:
            logma.warning(f"[documents] _apply_bg_color: setStyleSheet " f"failed for color={css_color!r}: {e}")

    def _store_document(self) -> Self:
        """"""
        document = self.document.to_dict()
        self.app.model.store_document(document)
        return self

    def _show_context_menu(self, pos) -> Self:
        """"""
        # Re-initialize context menu to ensure it's fresh
        if self.context_menu is None:
            self.initialize_context_menu(self.context_menu_name)
        if self.context_menu is not None:
            global_pos = self.mapToGlobal(pos)
            self.context_menu.exec(global_pos)
        return self


class NchantdOfficeDocument(NchantdOfficeDocumentMixin, NchantdOfficeTab):
    """ ""Document base class - implements PyfficeDocument for all document types"""

    PYTYPE = "document"  # Default Pyffice type

    def __init__(self, name, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDocument").override(cfg))
        self.name = name
        self.document = None
        self.did = None
        self.notes = None

    @classmethod
    def get_pyffice_tools(cls) -> list[Any]:
        """Get toolbox tools based on Pyffice document type"""
        return []  # Override in subclasses

    def initModel(self, cfg=None) -> Self:
        """"""
        self.init_variables(self.name)
        self.config.override(
            {"settings": self.app.model.settings.document.get(self.document_type, self.get_default_settings())}
        )
        super().initModel(cfg)
        self.document = self.app.model.codex.init_document({"document": self.config.get("document", {})})
        self.document.set_location("internal")
        logma.json({"document": self.config.dikt.get("document", {})})
        return self

    def get_default_settings(self) -> dict[str, Any]:
        """"""
        return {}

    def initView(self, cfg=None) -> Self:
        """"""
        super().initView(cfg)
        self.set_notes(self.config.dikt.get("notes", []))
        if self.document.location == "external":
            self.open_file(self.document.file_path)
        elif self.document.location == "internal":
            self.populate_data()
        # PUSH to 0.0.3
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        else:
            logma.info(f"Location {self.document.location}")
            if debug:
                raise Exception("Internal and Cloud locations not supported yet")
            self.document.location = "internal"
            self.populate_data()
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def add_automation(self) -> Self:
        """"""
        super().add_automation()
        return self

    def append_note(self, note) -> Self:
        """"""
        note.set_sequence(len(self.notes))
        self.notes.append(note)
        return self

    def close_tab(self, tab=None) -> Self:
        """"""
        super().close_tab(tab)
        return self

    def export_file(self) -> None:
        """"""
        super().export_file()

    def focusOutEvent(self, event=None, *args, **kwargs):
        """"""
        super().focusOutEvent(event, args, kwargs)
        self.save()

    def get_content_internal(self) -> dict[str, Any]:
        """"""
        return {}

    def get_content(self, content=None, location="external") -> dict[str, Any]:
        """"""
        content = content or {}
        content["file_path"] = self.document.file_path
        content["location"] = self.document.location
        if self.document.location == "internal":
            content["internal"] = self.get_content_internal()
        return content

    def get_version(self) -> int:
        """returns the current version of the document"""
        return self.config.dikt.get("version", 1)

    def get_supports_versions(self) -> dict[str, Any]:
        """returns true if the document supports versions"""
        response = {"pyffice": self.config.dikt.get("supports_pyffice_versions", False)}
        return response

    def import_file(self) -> None:
        """"""
        super().import_file()

    def init_toolbar(self, cfg=None) -> Self:
        """"""
        super().init_toolbar(cfg)
        return self

    def init_toolbox(self, cfg=None) -> Self:
        """"""
        super().init_toolbox(cfg)
        return self

    def jump_to_account_tab(self) -> Self:
        """Switch the central tab area to the Account/Settings tab.

        Delegates to ``self.app.view.switch_to_account_tab`` which holds
        the actual tab-routing logic. Returns ``self`` for chainable
        call sites.
        """
        view = getattr(self, "app", None)
        if view is not None and hasattr(view, "view"):
            account_switch = getattr(view.view, "switch_to_account_tab", None)
            if account_switch is not None:
                return account_switch()
        return self

    def lock_view(self) -> Self:
        """"""
        super().lock_view()
        return self

    def open(self) -> Self:
        """Open the document for editing. If no document is set, attempt to load from the current node."""
        if self.document is None and hasattr(self, "app") and hasattr(self.app, "view"):
            tree = getattr(self.app.view.panes.get("left", {}), "tree", None)
            if tree and hasattr(tree, "model") and tree.model.current_node:
                node = tree.model.current_node
                if hasattr(node, "document") and node.document is not None:
                    self.set_document(node.document)
                    if self.document_editor is not None and hasattr(self.document, "content"):
                        self.document_editor.setPlainText(str(self.document.content))
        return self

    def open_cloud(self, path) -> None:
        """"""
        # PUSH to 0.0.3 - implement opening of cloud based documents like .gsheet, etc

    def open_file(self, file, _populate_document=True, _save=True) -> None:
        """"""
        if file is None:
            file = self.file_path
            if file is None:
                return
        self.set_file_path(file)
        self.document.open_file(file)  # The Pyffice document is not connected directly with the viewable pdf render
        self.document.set_location("external")
        if _populate_document:
            self.populate_document()
        if _save:
            self.save()

    def open_local(self) -> Self:
        """Trigger the local file open dialog."""
        return self.cmd_open_local_file()

    def open_remote(self) -> Self:
        """Open a document from a remote source URL."""
        if not hasattr(self.app, "model") or not hasattr(self.app.model, "open_remote"):
            logma.warning("open_remote not available on this model")
            return self
        try:
            doc = self.app.model.open_remote()
            if doc is not None:
                self.set_document(doc)
                if self.document_editor is not None and hasattr(doc, "content"):
                    self.document_editor.setPlainText(str(doc.content))
                logma.info(f'Remote document opened: {getattr(doc, "did", "unknown")}')
        except Exception as e:
            logma.error(f"Failed to open remote document: {e}")
        return self

    def populate_data(self, data=None) -> Self:
        """T-NEW-141: populate the in-memory document cache for an
        internal-location tab.

        Sets the document location to ``"internal"`` and triggers
        a save so the editor content is round-tripped through the
        doc_media / app_media_content table. The ``data`` arg is
        accepted for parity with the ``populate_data`` contract
        used by other doc subclasses (scripts, pdfs, images,
        etc.) but is not consumed here -- the document's own
        state is the source of truth.

        TODO: refactor

        """
        # self.document.set_location("internal")
        # self.save()
        return self

    def populate_document(self, file=None) -> Self:
        """"""
        self.save()
        return self

    def save(self) -> Self:
        """"""
        self.document = self.document or PyfficeDocument({})
        if self.document.location is None:
            self.document.set_location("internal")
        self.document.set_content(self.get_content())
        super().save()
        return self

    def set_document(self, document) -> Self:
        """"""
        self.document = document
        return self

    def set_notes(self, notes) -> Self:
        """"""
        # T-NEW-XXX: deferred import to break a circular import
        # with notes.py (which imports from documents.py).
        from nchantdoffice.widgets.documents.media.notes import (
            NchantdOfficeNote,
        )

        self.notes = [NchantdOfficeNote(self, note).initWidget() for note in notes]
        return self

    def unlock_view(self) -> Self:
        """"""
        super().unlock_view()
        return self

    @staticmethod
    def _save_action(document) -> str:
        """Return the save action name for a document (T-NEW-038).

        When the document's location is ``"internal"`` (stored
        in the NchantdOffice SQLite database), the action
        name is ``save_database`` -- the nchantrs action table
        (applicationmodels.yaml:609) maps that to the
        ``database-save`` icon. For ``"external"`` (or any
        unknown / missing location), the action stays the
        legacy ``save`` (icon: ``save.svg``).

        Defensive: missing document, missing location
        attribute, or non-string location all fall back to
        the legacy ``save`` action rather than raising.

        Args:
            document: the document instance, or ``None``
                when the helper is called before a document
                is open (e.g. from a static UI binding).

        Returns:
            ``"save_database"`` for internal documents,
            ``"save"`` otherwise.
        """
        if document is None:
            return "save"
        try:
            location = getattr(document, "location", None)
        except Exception:
            return "save"
        if not isinstance(location, str):
            return "save"
        if location == "internal":
            return "save_database"
        return "save"


class NchantdOfficeDocumentManager(NchantdOfficeDocumentMixin, NchantdManager):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config = (
            kahndor.Instruct(pxcfg).select("NchantdOfficeDocumentManager").override(parent.config).override(cfg)
        )
        self.name = "NchantdOfficeDocumentManager"

    def initModel(self, cfg=None) -> Self:
        """"""
        self.init_variables(self.name)
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
        """"""
        super().initView(cfg)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        return self

    def init_toolbox(self) -> None:
        """"""
        super().init_toolbox()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
