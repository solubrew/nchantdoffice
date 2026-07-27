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
        """Initialize the model.

        T-062: ``init_variables()`` is kept as a separate call
        (rather than inlined) because the parent class's
        ``super().initModel()`` requires ``self.app`` to be
        set first - the current init order is:

          1. ``self.init_variables()`` - reads the app reference
          2. Read document types from the model
          3. ``super().initModel(...)`` - assumes ``self.app`` is set

        Inlining the variables would re-order these and break
        downstream callers. The redundancy is preserved as a
        guardrail until the parent class is updated.
        """
        self.init_variables()
        self.document_types = self.app.model.get_document_types()
        self.document_types = self.app.model.get_document_types()
        logma.info(f"Document Types {self.document_types}")
        # self.document_types.drop_duplicates(subset=["name_txt", "widget_txt", "parameters_dict"], inplace=True)
        self.document_types = self.document_types[self.document_types["quick_launch_bit"] == 1]
        self.document_types.sort_values(by=["file_type_txt", "sequence_int", "document_txt", "name_txt"], inplace=True)
        self.document_types.reset_index(drop=True, inplace=True)
        self.set_handlers()
        super().initModel(self.document_types)
        return self

    def _resolve_db_alias(self):
        """T-064: resolve the active database alias.

        Reads ``self.app.model.instance.db`` first, then
        ``self.app.model.config.dikt['db_alias']``, then falls
        back to the legacy ``"db"`` literal.

        Returns the chosen alias string.
        """
        try:
            if hasattr(self, "app") and self.app is not None:
                model = getattr(self.app, "model", None)
                if model is not None:
                    instance = getattr(model, "instance", None)
                    if instance is not None and hasattr(instance, "db"):
                        alias = instance.db
                        if alias:
                            return alias
                    if hasattr(model, "config") and hasattr(model.config, "dikt"):
                        profile_alias = model.config.dikt.get("db_alias")
                        if profile_alias:
                            return profile_alias
        except Exception as e:
            logma.error(f"[toolbars] _resolve_db_alias failed: {e}", exc_info=True)
        return "db"

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
        # T-063: registry-based widget lookup. The widget class
        # is resolved from the ``app_document_type`` registry
        # via ``_resolve_widget_from_registry`` rather than via
        # the legacy hard-coded ``widget_txt`` from the action
        # action. Falls back to ``widget_txt`` only when the
        # registry returns nothing.
        lookup_code = cfg["lookup_code_txt"]
        widget = args[0]["action"].action.get("widget_txt")
        # T-063: route through self.app.model so the registry helper
        # (defined on NchantdOfficeCloakModel) is the single source of
        # truth for widget-class lookup. Falls back to the legacy
        # widget_txt when the registry is unreachable or missing.
        widget = self.app.model._resolve_widget_from_registry(lookup_code, widget)
        logma.info(f"Widget {widget}")
        # T-064: db goes through MultiInstance adapter
        db = self._resolve_db_alias()
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
        # T-065: combine add_document + add_tab into a single
        # launch_document call (the unified entry point in
        # model). Preserves the existing setCurrentIndex /
        # updateTabs behaviour so callers don't have to change.
        launcher = getattr(self.app.model, "launch_document", None)
        if callable(launcher):
            try:
                launcher(document=document, did=did, pid=pid, pos=pos,
                          widget=widget, params=params, doc_type=doc_type,
                          tabset="center", db=db)
            except Exception as e:
                logma.error(f"[toolbars] launch_document failed: {e}", exc_info=True)
                # Fall back to the legacy two-step path
                self.app.model.add_document(document, did, pid, pos, widget, params, doc_type, "center", db, True)
        else:
            self.app.model.add_document(document, did, pid, pos, widget, params, doc_type, "center", db, True)
        self.app.view.panes["left"].tree.model.current_node.updateTabs("center")
        self.app.view.panes["center"].setCurrentIndex(pos)

        # Emit signal that document was created
        self.document_created.emit(doc_type)
        return self

    def add_node(self, signal=None, *args, **kwargs):
        """Add a new node."""
        cfg = args[0]["action"].action
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

    def add_note(self, signal=None, *args, **kwargs):
        """Add a new note.

        T-066: when multiple notes are open we now increment the
        y-position by 25px per existing note so each new note
        opens below the previous one rather than overlapping.
        """
        logma.info(f"[toolbars] Launch Note {signal}")
        cfg = args[0]["action"].action
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        # T-066: count existing notes for this pid and offset
        existing = 0
        try:
            tabsdata = self.app.view.panes["center"].model.tabsdata or []
            for tab in tabsdata:
                if tab.get("pid") == pid and tab.get("type") == "note":
                    existing += 1
        except Exception as e:
            logma.error(f"[toolbars] add_note tab count failed: {e}", exc_info=True)
        base_x = 1287
        base_y = 125
        offset_y = existing * 25
        pos = {"x": base_x, "y": base_y + offset_y}
        name = "{" + str(dt.datetime.now()) + "}"
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
        """Set the active item."""
        #TODO implement method
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
