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
from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot
# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from subtrix.utilities import uuid
from nchantrs.libraries import pyqt
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.controls.toolbars import NchantdApplicationToolBar
from ogma.logma import Logma
from nchantdoffice.dialogs.documents import NchantdNewDocumentSigil
from nchantdoffice.widgets.documents import NchantdOfficeDocument

# Import Pyffice types for type hints
try:
    from pyffice import PyfficeDocument
except ImportError:
    PyfficeDocument = None


# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "toolbars.yaml")
pxcfg = {}


class NchantdOfficeApplicationToolBar(NchantdApplicationToolBar):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeApplicationToolBar"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeNotificationButtonBar(NchantdButtonBar):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeApplicationNotificationButtonBar")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        # setup a drop down that shows up only when there are application wide notifications
        # The drop down will flash when new notifications are added
        # the drop down will have a button to clear notifications
        # This is where updates will be shown for the user to allow or set to automatic

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdNewDocumentToolBar(NchantdButtonBar):
    """""Far left toolbar - creates new documents and emits signals"""
    
    # Signals for document lifecycle
    document_created = Signal(str)  # Emitted when new document created (doc_type string)
    document_opened = Signal(object)  # Emitted when document opened (NchantdOfficeDocument instance)
    
    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdNewDocumentToolBar"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.actions = None
        self.document_types = None

    def initModel(self):
        """"""
        self.document_types = self.app.model.get_document_types()
        # self.document_types.drop_duplicates(subset=["name_txt", "widget_txt", "parameters_dict"], inplace=True)
        self.document_types = self.document_types[self.document_types["quick_launch_bit"] == 1]
        self.document_types.sort_values(by=["file_type_txt", "sequence_int", "document_txt", "name_txt"], inplace=True)
        self.document_types.reset_index(drop=True, inplace=True)
        self.set_handlers()
        super().initModel(self.document_types)
        return self

    def initView(self):
        """"""
        cfg = {"layout": "vertical"}
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_document(self, signal=None, *args, **kwargs):
        """"""
        cfg = args[0]["action"].action
        if isinstance(cfg["parameters_dict"], str):
            cfg["parameters_dict"] = j.loads(cfg["parameters_dict"].replace("'", '"'))
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        pos = len(self.app.view.panes["center"].model.tabsdata)
        code = cfg["lookup_code_txt"][-len(cfg["lookup_code_txt"]) + cfg["lookup_code_txt"].rfind("_") + 1 :]
        did = uuid()
        name = f"{code.lower().replace(' ', '')} {did[-5:]}"
        widget = args[0]["action"].action["widget_txt"]
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
        """"""
        cfg = args[0]["action"].action
        name = uuid()[-5:]
        tree = "left"
        logma.info(f"Lookup Code {cfg['lookup_code_txt']}")
        logma.info(f"PID {self.app.view.panes[tree].tree.model.current_node.pid}")
        logma.info(f"Current Node {self.app.view.panes[tree].tree.model.current_node}")
        pos = 0
        if cfg["lookup_code_txt"] == "add_node_top_app_rootnode":
            pid = 0
        elif cfg["lookup_code_txt"] in ("add_node_sibling_app_siblingnode"):
            pid = self.app.view.panes[tree].tree.model.current_node.pid
            pos = int(self.app.view.panes[tree].tree.model.current_node.position) + 1
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
        """"""
        logma.info(f"Launch Note {signal}")
        cfg = args[0]["action"].action
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        pos = {"x": 1287, "y": 125}
        # TODO: if there are multiple notes then the position will need to increment
        name = "{" + str(dt.datetime.now()) + "}"
        document = {"name": name, "widget": "NchantdOfficeNote"}
        self.app.model.add_note(document, pid, pos, cfg)
        self.app.view.panes["center"].launch_note(cfg)
        return self

    def launch_new_document_sigil(self, signal=None, *args, **kwargs):
        """"""
        logma.info(f"Launch the Sigil")
        # cfg = {"documents": self.document_types}
        cfg = {}
        sigil = NchantdNewDocumentSigil("Test", self, cfg).initWidget()
        return self

    def set_active_item(self):
        """"""
        return self

    def set_actions(self, actions=None):
        """"""
        if actions is None:
            actions = self.actions
        self.actions = {
            i: {"action": x["action_txt"], "handler": x["handler"]}
            for i, x in enumerate(actions.to_dict(orient="records"))
        }
        return self

    def set_handlers(self):
        """"""
        self.set_active_item()
        self.document_types["handler"] = self.document_types["action_txt"].apply(self.set_handler)
        return self

    def set_handler(self, value):
        """"""
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
        return self


class NchantdCellFormattingToolBar(NchantdButtonBar):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdCellFormattingToolBar")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        for seq, action in self.config.dikt.get("actions", {}).items():
            self.buttons[action] = NchantdButton(self, lookup(self.app, action)).initWidget()
            self.layout.addWidget(self.buttons[action])
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdDataFormattingToolBar(NchantdButtonBar):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdTextFormattingToolBar")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdTextFormattingToolBar(NchantdButtonBar):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdTextFormattingToolBar")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
