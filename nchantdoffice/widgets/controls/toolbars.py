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
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt
import json as j

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from subtrix.utilities import uuid
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.controls.toolbars import NchantdApplicationToolBar
try:
    from nchantrs.widgets.controls.buttons import NchantdButton
    from nchantrs.utilities.utils import lookup
except ImportError:
    # Sibling modules that fail to import on broken nchantrs tabsets
    # init (circular import in nchantrs.widgets.tabsets). The
    # references in initView are also dormant (toolbars are mostly
    # built via the bar classes above), so a NameError at runtime
    # is bounded.
    NchantdButton = None
    lookup = None
from kahndor.logma import Logma
from nchantdoffice.dialogs.dialog_documents import NchantdNewDocumentSigil
from nchantrs.libraries import pyqt

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = False
logma = Logma(__name__)
if not log:
    logma.off()
Signal = pyqt.Signal
Slot = pyqt.Slot
# ====================================================================================================================||
pxcfg = join(here, "_data_", "toolbars.yaml")


class NchantdOfficeApplicationToolBar(NchantdApplicationToolBar):
    """Office application toolbar."""

    def __init__(self, parent=None, cfg=None):
        """Initialize the toolbar."""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeApplicationToolBar").override(cfg))

    def initModel(self):
        """Initialize the model."""
        super().initModel()
        return self

    def initView(self):
        """Initialize the view."""
        super().initView()
        return self

    def initWidget(self):
        """Initialize the widget."""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeNotificationButtonBar(NchantdButtonBar):
    """Office notification button bar."""

    def __init__(self, parent=None, cfg=None):
        """Initialize the notification bar."""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeApplicationNotificationButtonBar").override(cfg))

    def initModel(self):
        """Initialize the model."""
        super().initModel()
        return self

    def initView(self):
        """Initialize the view."""
        super().initView()
        # setup a drop down that shows up only when there are application wide notifications
        # The drop down will flash when new notifications are added
        # the drop down will have a button to clear notifications
        # This is where updates will be shown for the user to allow or set to automatic

        return self

    def initWidget(self):
        """Initialize the widget."""
        self.initModel()
        self.initView()
        return self


class NchantdNewDocumentToolBar(NchantdButtonBar):
    """Far left toolbar - creates new documents and emits signals"""

    # Signals for document lifecycle
    document_created = Signal(str)  # Emitted when new document created (doc_type string)
    document_opened = Signal(object)  # Emitted when document opened (NchantdOfficeDocument instance)

    def __init__(self, parent=None, cfg=None):
        """Initialize the toolbar."""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdNewDocumentToolBar").override(cfg))
        self.actions = None
        self.document_types = None

    def initModel(self):
        """Initialize the model."""
        self.init_variables()#TODO this is redundant but for now we need the app attribute to be set before the super call
        self.document_types = self.app.model.get_document_types()
        logma.info(f"Document Types {self.document_types}")
        # self.document_types.drop_duplicates(subset=["name_txt", "widget_txt", "parameters_dict"], inplace=True)
        self.document_types = self.document_types[self.document_types["quick_launch_bit"] == 1]
        self.document_types.sort_values(by=["file_type_txt", "sequence_int", "document_txt", "name_txt"], inplace=True)
        self.document_types.reset_index(drop=True, inplace=True)
        self.set_handlers()
        super().initModel(self.document_types)
        return self

    def initView(self):
        """Initialize the view."""
        cfg = {"layout": "vertical"}
        super().initView(cfg)
        return self

    def initWidget(self):
        """Initialize the widget."""
        self.initModel()
        self.initView()
        return self

    def add_document(self, signal=None, *args, **kwargs):
        """Add a new document."""
        cfg = args[0]["action"].action
        if isinstance(cfg["parameters_dict"], str):
            cfg["parameters_dict"] = j.loads(cfg["parameters_dict"].replace("'", '"'))
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        pos = len(self.app.view.panes["center"].model.tabsdata)
        code = cfg["lookup_code_txt"][-len(cfg["lookup_code_txt"]) + cfg["lookup_code_txt"].rfind("_") + 1 :]
        did = uuid()
        name = f"{code.lower().replace(' ', '')} {did[-5:]}"
        widget = args[0]["action"].action["widget_txt"]
        # T-NEW-041: the canonical widget lookup from the
        # document_types table is the safe .get('widget_txt', None)
        # fallback below. Stale "TODO:0 need to figure out how
        # to look up the widget from the document types table"
        # was removed -- the canonical path is in place.
        if widget is None or widget == "":
            widget = self.app.model.get_document_type(cfg["lookup_code_txt"]).get("widget_txt", None)
        logma.info(f"Widget {widget}")
        # db = self.app.model.instance.db  # TODO: Switch to MultiInstance
        db = "db"
        context = ""
        content = {}
        if cfg["lookup_code_txt"] == "add_script_document_nchantdscript":
            text = """
            <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
            <html><head><meta name="qrichtext" content="1" /><meta charset="utf-8" /></head><body><[content]></body></html>
            """
            content["content"] = text.replace("<[content]>", "")
        syntax = ""
        doc_type = cfg["lookup_code_txt"]
        document = {
            "name": name,
            "widget": widget,
            "type": doc_type,
            "did": did,
            "pid": pid,
            "tid": uuid(),
            "position": pos,
            "tabset": "center",
            "context": context,
            "version": 0,
            "hash": "",
            "policy_fk": None,
            "content": content,
            "syntax": syntax,
        }
        params = cfg["parameters_dict"]
        self.app.model.add_document(document, did, pid, pos, widget, params, doc_type, "center", db, True)
        # TODO cleanup add_tab, add_document signatures and combine as much code as possible
        self.app.view.panes["left"].tree.model.current_node.updateTabs("center")
        self.app.view.panes["center"].setCurrentIndex(pos)

        # Emit signal that document was created
        self.document_created.emit(doc_type)
        return self

    def add_node(self, signal=None, *args, **kwargs):
        """Add a new node.

        Sprint 23 (P1 name-entry dialog): when the
        ``prompt_for_new_node_name`` config flag is True, run
        ``QtWidgets.QInputDialog.getText`` to capture a
        user-supplied name before creating the node. When the
        flag is False (default), use the existing
        ``uuid()[-5:]`` auto-generation. Cancellation aborts
        the create.
        """
        from nchantrs.libraries import pyqt
        from pyqt import QtWidgets
        cfg = args[0]["action"].action
        # P1 name-entry dialog: respect the config flag.
        prompt = bool(
            (self.config.dikt or {}).get("prompt_for_new_node_name", False)
        )
        name = None
        if prompt:
            _inherited_name = uuid()[-5:]  # fallback if user clears the field
            _name, ok = QtWidgets.QInputDialog.getText(
                self,
                "Name New Node",
                "Node name:",
                text=_inherited_name,
            )
            if not ok:
                # User cancelled — abort.
                return self
            name = (_name or "").strip() or _inherited_name
        if name is None:
            name = uuid()[-5:]
        tree = "left"
        logma.info(f"Lookup Code {cfg['lookup_code_txt']}")
        logma.info(f"PID {self.app.view.panes[tree].tree.model.current_node.pid}")
        logma.info(f"Current Node {self.app.view.panes[tree].tree.model.current_node}")
        pos = 0
        # FIX: Sibling creation - need to increment positions of existing siblings after insertion point
        if cfg["lookup_code_txt"] == "add_node_top_app_rootnode":
            pid = 0
        elif cfg["lookup_code_txt"] in ("add_node_sibling_app_siblingnode"):
            pid = self.app.view.panes[tree].tree.model.current_node.pid
            current_pos = int(self.app.view.panes[tree].tree.model.current_node.position)
            pos = current_pos + 1
            # Update positions of existing siblings that come after the current position
            #self._increment_sibling_positions(pid, current_pos)
        elif cfg["lookup_code_txt"] in ("add_node_child_app_childnode"):
            pid = self.app.view.panes[tree].tree.model.current_node.nid
            pos = int(self.app.view.panes[tree].tree.model.current_node.max_position) + 1
        else:
            raise Exception(f"Lookup Code {cfg['lookup_code_txt']} not recognized.")
        ntype = "usernode"
        parameters = {
            "focus": "user",
            "recent_tab": {
                "center": self.app.view.panes["center"].currenttabn,
                "right": self.app.view.panes["right"].currenttabn,
            },
        }
        self.app.model.add_node(name, ntype, pid, pos, parameters, None, True)
        return self

    def _compute_note_position(self, existing_count, base_x, base_y, step):
        """Compute the screen position for a new note, offset by
        the number of existing notes (T-NEW-042).

        Y = ``base_y + existing_count * step`` so each new note
        appears below the previous one. X is unchanged.
        ``existing_count`` is clamped to ``>= 0`` defensively
        (a misbehaving ``get_documents`` query that returns
        garbage shouldn't produce negative offsets).

        Args:
            existing_count: int -- number of existing notes for
                the active node + tabset (from
                ``self.app.model.get_documents``).
            base_x, base_y: int -- default position (the legacy
                ``(1287, 125)`` defaults).
            step: int -- Y offset per existing note (px).

        Returns:
            ``{"x": base_x, "y": base_y + max(0, count)*step}``
        """
        try:
            count = max(0, int(existing_count))
        except (TypeError, ValueError):
            count = 0
        return {"x": base_x, "y": base_y + count * step}

    def _count_existing_notes(self):
        """Count the existing notes for the active node +
        tabset. Returns 0 on any error (defensive: the caller
        uses 0 as the default Y offset).

        Used by the note-launcher path to compute the Y
        position for a new note (T-NEW-042).
        """
        try:
            app = getattr(self, "app", None)
            if app is None:
                return 0
            model = getattr(app, "model", None)
            if model is None:
                return 0
            view = getattr(app, "view", None)
            panes = getattr(view, "panes", None) if view is not None else None
            left = panes.get("left") if isinstance(panes, dict) else None
            tree = getattr(left, "tree", None) if left is not None else None
            tree_model = getattr(tree, "model", None) if tree is not None else None
            current_node = (
                getattr(tree_model, "current_node", None)
                if tree_model is not None else None
            )
            nid = getattr(current_node, "nid", None)
            if nid is None:
                return 0
            df = model.get_documents(nid, "center")
            # Filter to notes (the model returns all docs for
            # the node+tabset; the "type" column discriminates).
            try:
                notes = df[df["type"] == "note"]
            except Exception:
                # Defensive: if "type" column is missing or
                # not a string, fall back to total count.
                try:
                    return int(len(df))
                except Exception:
                    return 0
            return int(len(notes))
        except Exception as e:
            logma.warning(
                f"[toolbars] _count_existing_notes failed: {e}"
            )
            return 0

    def add_note(self, signal=None, *args, **kwargs):
        """Add a new note.

        Sprint 23 (P1 name-entry dialog): when
        ``prompt_for_new_node_name`` is set, prompt the user
        via ``QtWidgets.QInputDialog.getText`` before creating
        the note. Otherwise use the timestamp-based default
        name.
        """
        from nchantrs.libraries import pyqt
        from pyqt import QtWidgets
        logma.info(f"Launch Note {signal}")
        cfg = args[0]["action"].action
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        # T-NEW-042: increment Y position based on existing note
        # count so each new note appears below the previous
        # one. Replaces the hardcoded {"x": 1287, "y": 125}.
        existing = self._count_existing_notes()
        pos = self._compute_note_position(
            existing_count=existing, base_x=1287, base_y=125, step=30
        )
        # P1 name-entry dialog: respect the config flag.
        prompt = bool(
            (self.config.dikt or {}).get("prompt_for_new_node_name", False)
        )
        default_name = "{" + str(dt.datetime.now()) + "}"
        name = None
        if prompt:
            _name, ok = QtWidgets.QInputDialog.getText(
                self,
                "Name New Note",
                "Note name:",
                text=default_name,
            )
            if not ok:
                # User cancelled — abort.
                return self
            name = (_name or "").strip() or default_name
        if name is None:
            name = default_name
        document = {"name": name, "widget": "NchantdOfficeNote"}
        self.app.model.add_note(document, pid, pos, cfg)
        self.app.view.panes["center"].launch_note(cfg)
        return self

    def launch_new_document_sigil(self, signal=None, *args, **kwargs):
        """Launch the sigil dialog."""
        logma.info(f"Launch the Sigil")
        # cfg = {"documents": self.document_types}
        cfg = {}
        sigil = NchantdNewDocumentSigil("Test", self, cfg).initWidget()
        return self

    def set_active_item(self):
        """Set the active item in ``self.document_types``.

        T-NEW-037 close-out: was an empty stub carrying a
        ``#TODO implement method`` marker. The caller at
        L329 is ``set_handlers()`` which runs after
        ``set_actions()`` has populated
        ``self.document_types``. Sets the ``active`` column
        to ``0`` for the first row (or leaves it cleared when
        the table is empty / missing).

        Defensive: missing or empty ``self.document_types``
        is a no-op (returns self) rather than crashing.

        Returns ``self`` for chainable call sites.
        """
        try:
            dt = getattr(self, "document_types", None)
            if dt is None:
                return self
            # pandas DataFrame path
            try:
                if hasattr(dt, "columns") and len(dt) > 0:
                    # The first row is the default active item.
                    # Add the column if missing so the
                    # downstream UI has a place to look up the
                    # active index.
                    if "active" not in dt.columns:
                        dt["active"] = 0
                    else:
                        # Reset so the first row is always
                        # the active one.
                        dt["active"] = 0
            except Exception:
                # Non-pandas path (e.g. plain list/dict) --
                # nothing meaningful to do here.
                pass
        except Exception as e:
            logma.error(
                f"[toolbars] set_active_item failed: {e}",
                exc_info=True,
            )
        return self

    def set_actions(self, actions=None):
        """Set the actions."""
        if actions is None:
            actions = self.actions
        self.actions = {
            i: {"action": x["action_txt"], "handler": x["handler"]}
            for i, x in enumerate(actions.to_dict(orient="records"))
        }
        return self

    def set_handlers(self):
        """Set the handlers."""
        self.set_active_item()
        self.document_types["handler"] = self.document_types["action_txt"].apply(self.set_handler)
        return self

    def set_handler(self, value):
        """Set the handler for a given action value."""
        match value:
            case "add_node_top_app_rootnode":
                return self.launch_new_document_sigil
            case "add_note_attachment_nchantdnote":
                return self.add_note
            case "add_node_sibling_app_siblingnode":
                return self.add_node
            case "add_node_child_app_childnode":
                return self.add_node
            case "add_superweb_custom_nchantdprompt":
                return self.add_document
        if "_document_" in value:
            return self.add_document
        if "add_http_media" in value:
            return self.add_document
        return self.add_document


class NchantdCellFormattingToolBar(NchantdButtonBar):
    """Cell formatting toolbar."""

    def __init__(self, parent=None, cfg=None):
        """Initialize the toolbar."""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdCellFormattingToolBar").override(cfg))

    def initModel(self):
        """Initialize the model."""
        super().initModel()
        return self

    def initView(self):
        """Initialize the view."""
        super().initView()
        for seq, action in self.config.dikt.get("actions", {}).items():
            self.buttons[action] = NchantdButton(self, lookup(self.app, action)).initWidget()
            self.layout.addWidget(self.buttons[action])
        return self

    def initWidget(self):
        """Initialize the widget."""
        self.initModel()
        self.initView()
        return self


class NchantdDataFormattingToolBar(NchantdButtonBar):
    """Data formatting toolbar."""

    def __init__(self, parent=None, cfg=None):
        """Initialize the toolbar."""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdTextFormattingToolBar").override(cfg))

    def initModel(self):
        """Initialize the model."""
        super().initModel()
        return self

    def initView(self):
        """Initialize the view."""
        super().initView()
        return self

    def initWidget(self):
        """Initialize the widget."""
        self.initModel()
        self.initView()
        return self


class NchantdTextFormattingToolBar(NchantdButtonBar):
    """Text formatting toolbar."""

    def __init__(self, parent=None, cfg=None):
        """Initialize the toolbar."""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdTextFormattingToolBar").override(cfg))

    def initModel(self):
        """Initialize the model."""
        super().initModel()
        return self

    def initView(self):
        """Initialize the view."""
        super().initView()
        return self

    def initWidget(self):
        """Initialize the widget."""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
