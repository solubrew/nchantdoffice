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
from os.path import dirname, join, exists

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma

from nchantdoffice.widgets.documents.atnrg.browsers.browsers import NchantdOfficeWebBrowser
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from pyffice.notebooks.notebooks import PyfficeNotebook
from nchantdoffice.agents.agents import NchantdOfficeAgent

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "notebooks.yaml")
pxcfg = {}


class NchantdOfficeNotebook(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Notebook", self, cfg)
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeNotebook")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        # self.document = PyfficeNotebook()
        self.agent = NchantdOfficeAgent()

    def initModel(self):
        """"""
        super().initModel()
        self.document = self.app.model.codex.init_notebook()
        self.document.load_document()
        self.context_menu.get_menu("context.document.notebook")
        # need to control the python environment that is being used to run the jupyter notebook
        # limit the ability to connect with items in the nchantdoffice application
        #
        cmd = ["jupyter", "notebook", "--no-browser", "--NotebookApp.token=''", "--port=8888"]
        self.agent.run(cmd)
        return self

    def initView(self, cfg=None):
        """"""
        if not cfg:
            cfg = {}
        if "buttons" not in cfg:
            cfg["buttons"] = {}
        cfg["buttons"][1] = {"action": "restart_server"}
        cfg["buttons"][2] = {"action": "stop_server"}
        cfg["buttons"][6] = "_insert_stretch"
        cfg["buttons"][7] = {"action": "open_local"}
        super().initView(cfg)
        cfg = {"url": "http://localhost:8888", "is_app": True}
        self.browser = NchantdWebViewer(self, cfg).initView()
        self.layout.addWidget(self.browser)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def init_drawer_document_config(self):
        """"""
        items = {}
        return items

    def init_drawer_selection_config(self):
        """"""
        items = {}
        return items

    def init_drawer_object_config(self):
        """"""
        items = {}
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_selection_config()
        self.toolbox_config[300]["items"] = self.init_drawer_object_config()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
