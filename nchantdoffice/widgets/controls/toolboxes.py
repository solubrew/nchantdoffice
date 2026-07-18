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

# ======================================3rd Party Library Modules=====================================================||
from shutil import copyfile

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantrs.widgets.controls.toolboxes import NchantdToolBox
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.media.editors.editors import NchantdEntryBox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.panes.panes import NchantdPane

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "toolboxes.yaml")


class NchantdApplicationSearchPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdApplicationSearchPane").override(cfg))
        self.handler = self.config.dikt.get("handler", None)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        options = ["This Tab", "This Node", "This Instance", "Journal", "Web", "LLM"]
        cfg = {"label": "Search Focus", "layout": "horizontal", "options": options}
        self.search_area_select = NchantdDropDown(self, cfg).initWidget()
        self.layout.addWidget(self.search_area_select)
        cfg = {
            "layout": "vertical",
            "size": ["auto", 100],
        }
        self.application_search_entry = NchantdEntryBox(self, cfg).initWidget()
        logma.info(f"application_search_entry {self.application_search_entry.size().height()}")
        self.application_search_entry.setMinimumHeight(self.application_search_entry.size().height())
        self.layout.addWidget(self.application_search_entry)
        cfg = {"text": "Run Search", "layout": "horizontal"}
        self.search_button = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.search_button)
        cfg = {
            "layout": "vertical",
            "size": ["auto", 450],
        }
        self.application_response_area = NchantdEntryBox(self, cfg).initWidget()
        self.application_response_area.setMinimumHeight(cfg["size"][1])
        self.layout.addWidget(self.application_response_area)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdLLMQueryPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdLLMQueryPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        options = ["Open Ai", "Grok", "Gemini", "Claude"]
        cfg = {"label": "Set Default LLM", "layout": "horizontal", "options": options}
        self.default_llm_engine_select = NchantdDropDown(self, cfg).initWidget()
        self.layout.addWidget(self.default_llm_engine_select)
        cfg = {
            "label": "Query Model: ",
            "layout": "vertical",
            "options": options,
            "size": ["auto", 150],
        }
        self.llm_query_entry = NchantdEntryBox(self, cfg).initWidget()
        self.layout.addWidget(self.llm_query_entry)
        cfg = {"text": "Query", "layout": "horizontal"}
        self.search_llm_button = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.search_llm_button)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdWebSearchPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdWebSearchPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        options = ["Google", "DuckDuckGo", "Bing", "Yahoo", "Yandex", "PreSearch", "Shodan"]
        cfg = {"label": "Set Default Search", "layout": "horizontal", "options": options}
        self.default_search_engine_select = NchantdDropDown(self, cfg).initWidget()
        self.layout.addWidget(self.default_search_engine_select)
        cfg = {
            "label": "Search Web: ",
            "layout": "vertical",
            "options": options,
            "size": ["auto", 50],
        }
        self.application_search_entry = NchantdEntryBox(self, cfg).initWidget()
        self.layout.addWidget(self.application_search_entry)
        cfg = {"text": "Search Web", "layout": "horizontal"}
        self.search_web_button = NchantdButton(self, cfg).initWidget()
        self.layout.addWidget(self.search_web_button)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# TODO: implement search panes
# TODO: correct spacing of Node Configuration Drawer to tighten up the Node Pane and Tab Pane
class NchantdOfficeApplicationToolBox(NchantdToolBox):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeApplicationToolBox").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView()
        return self

    def add_documents_drawer(self):
        """"""
        return self

    def add_node_drawer(self):
        """"""
        cfg = {"action": "add_node"}
        # self.add_node = NchantdButton(self, cfg).initWidget()
        # self.add_drawer_item(self.add_node, 0, 0)
        return self

    def add_settings_drawer(self):
        """"""
        return self

    def add_tabs_drawer(self):
        """"""
        cfg = {"action": "add_tab"}
        # self.add_tab = NchantdButton(self, cfg).initWidget()
        # self.add_drawer_item(self.add_tab, 0, 0)
        return self

    def add_tools_drawer(self):
        """"""
        return self

    def build_toolbox(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["toolbox"] = self.config.dikt.get("toolbox", {})
        logma.info(f"cfg {cfg}")
        self.init_toolbox()
        super().build_toolbox(cfg)
        return self

    def cmd_application_search_pane(self, event, *args, **kwargs):
        """"""

    def cmd_create_new_instance(self, event, *args, **kwargs):
        """"""
        self.app.model.create_new_instance()
        return self

    def cmd_duplicate_instance(self, event, *args, **kwargs):
        """"""
        # create new instance
        # copy over user items from the initial database to the new instance database
        return self

    def cmd_export_instance(self, event, *args, **kwargs):
        """"""
        # restrict to selecting a folder
        if self.app.user.use_library:
            self.local_directory = self.app.model.library_path
            return self
        cfg = {}
        self.save_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_directory = self.open_file_sigil.file_selected
        return self

    def cmd_import_instance(self, event, *args, **kwargs):
        """"""
        cfg = {}
        self.open_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.open_file_sigil.file_selected
        return self

    def cmd_llm_query_pane(self, event, *args, **kwargs):
        """"""
        return self

    def cmd_import_local_file(self, event=None, *args, **kwargs):
        """"""
        cfg = {}
        self.import_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.import_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
            elif self.local_file.endswith((".py", ".xml", ".txt", ".md", ".html", ".htm")):
                self.app.model.import_text(self.local_file)
            elif self.local_file.endswith(".pdf"):
                self.app.model.import_pdf(self.local_file)
            elif self.local_file.endswith(".docx"):
                pass
            elif self.local_file.endswith((".json", ".yaml", ".yml")):
                if "Sessions - " in self.local_file:
                    self.app.model.import_web_session(self.local_file)
                else:
                    self.app.model.import_text(self.local_file)
            elif self.local_file.endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                self.app.model.import_image(self.local_file)
            elif self.local_file.endswith(".gif"):
                pass
            else:
                self.app.model.import_text(self.local_file)
                # raise Exception(f"Unknown File {self.local_file}")
        return self

    def cmd_open_instance(self, event, *args, **kwargs):
        """"""
        cfg = {}
        self.import_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.import_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".pyof"):
                # TODO: implement loading new nchantd office instance
                # self.cmd_open_instance(local_file=self.local_file)
                raise Exception(f"File Type not yet implemented {self.local_file}")
            else:
                raise Exception(f"Unknown File {self.local_file}")
        return self

    def cmd_open_local_file(self, event=None, *args, **kwargs):
        """"""
        cfg = {}
        self.import_file_sigil = NchantdFileOpenSigil("open_local_document", self, cfg).initWidget()
        self.local_file = self.import_file_sigil.file_selected
        if self.local_file is not None:
            if self.local_file.endswith(".ctd"):
                self.app.model.import_cherrytree(self.local_file)
            elif self.local_file.endswith((".py", ".xml", ".txt", ".md", ".html", ".htm")):
                self.app.model.import_text(self.local_file)
            elif self.local_file.endswith(".pdf"):
                self.app.model.import_pdf(self.local_file)
            elif self.local_file.endswith(".docx"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith((".json", ".yaml", ".yml")):
                if "Sessions - " in self.local_file:
                    self.app.model.import_web_session(self.local_file)
                else:
                    self.app.model.import_text(self.local_file)
            elif self.local_file.endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                self.app.model.import_image(self.local_file)
            elif self.local_file.endswith(".gif"):
                pass
            elif self.local_file.endswith(".csv"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
                # self.app.model.import_csv(self.local_file)
            elif self.local_file.endswith(".xlsx"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".xls"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".ods"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".odt"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".odp"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".ods"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".odg"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".odf"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".odc"):
                raise Exception(f"File Type not yet implemented {self.local_file}")
            elif self.local_file.endswith(".pyof"):
                # TODO: implement loading new nchantd office instance
                # self.cmd_open_instance(local_file=self.local_file)
                raise Exception(f"File Type not yet implemented {self.local_file}")
            else:
                self.app.model.import_text(self.local_file)
                # raise Exception(f"Unknown File {self.local_file}")
        return self

    def cmd_save_instance(self, event, *args, **kwargs):
        """"""
        cfg = {}
        self.save_file_sigil = NchantdFileOpenSigil("save_local_document", self, cfg).initWidget()
        self.local_file = self.save_file_sigil.file_selected
        if self.local_file is not None:
            # run update cmds for all changes
            if self.app.has_library:
                if self.app.model.is_saved:
                    self.app.model.copy_database()

                    # swap connection string to new path
                    # clear document data from base application file
                else:
                    pass
            else:
                pass
            # create new database
            # populate doc data
            pass
        return self

    def cmd_web_search_pane(self, event, *args, **kwargs):
        """"""
        return self

    def get_llm_engines(self):
        """"""
        options = ["Open Ai", "Grok", "Gemini", "Claude"]
        return options

    def get_search_engines(self):
        """"""
        options = ["Google", "DuckDuckGo", "Bing", "Yahoo", "Yandex", "PreSearch", "Shodan"]
        return options

    def init_drawer_application(self):
        """"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.config.dikt["toolbox"][0].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "text": "Save Document",
            "action": "insert_object",
            "layout": "horizontal",
            "size": ["auto", 30],
            "actions": {
                0: {"action": "new_instance", "type": "", "handler": self.cmd_create_new_instance},
                1: {"action": "open_instance", "type": "", "handler": self.cmd_open_local_file},
                2: {"action": "import_instance", "type": "", "handler": self.cmd_import_local_file},
                3: {"action": "duplicate_instance", "type": "", "handler": self.cmd_duplicate_instance},
                # 3: {"action": "save_instance", "type": "", "handler": self.cmd_save_instance},
                # 5: {"action": "export_instance", "type": "", "handler": self.cmd_export_instance},
            },
        }
        self.document_buttonbar = NchantdButtonBar(self, cfg)
        items[cnt]["widget"] = self.document_buttonbar
        cnt += 1
        # if cnt not in items:
        #     items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        # cfg = {
        #     "layout": "horizontal",
        #     "handler": self.cmd_web_search_pane,
        #     "label": "Set Default Search",
        #     "options": self.get_search_engines(),
        # }
        # self.default_search_select = NchantdDropDown(self, cfg)
        # items[cnt]["widget"] = self.default_search_select
        # cnt += 1
        # if cnt not in items:
        #     items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        # cfg = {
        #     "layout": "horizontal",
        #     "handler": self.cmd_web_search_pane,
        #     "label": "Set Default LLM",
        #     "options": self.get_llm_engines(),
        # }
        # self.default_llm_select = NchantdDropDown(self, cfg)
        # items[cnt]["widget"] = self.default_llm_select
        # cnt += 1
        # if cnt not in items:
        #     items[cnt] = {"action": "insert_generic_action", "type": "dropdown"}
        # cfg = {"layout": "vertical", "handler": self.cmd_application_search_pane}
        # self.application_search_pane = NchantdApplicationSearchPane(self, cfg)
        # items[cnt]["widget"] = self.application_search_pane
        # cnt += 1
        return items

    def refresh_for_document(self, document):
        """Refresh toolbox drawer items for the active document/tab context.

        Called by NchantdOfficeTabSet.on_tab_focus() when the focused center
        document changes. Clears existing items and rebuilds them via
        init_drawer_application() without destroying the toolbox instance.
        """
        # RESOLVED [toolbox-stale-box]: build_toolbox() always creates a brand-new
        # QToolBox and adds it to this widget's layout. Without removing the old
        # one first, the previous drawers stay on screen and the toolbox appears to
        # "hold" the prior document's drawers when the active document changes.
        # clear() empties the old box and removes it from the layout; deleteLater()
        # disposes of the orphaned box widget. Fixed in commit 355fa85 alongside the
        # wrong-target fix in NchantdOfficeTabSet.on_tab_focus().
        old_box = self.box
        self.clear()
        if old_box is not None:
            old_box.deleteLater()

        # Clear existing toolbox drawer items in reverse order to avoid index shifts
        items = self.config.dikt["toolbox"][0].get("items", {})
        for idx in sorted(items.keys(), reverse=True):
            if idx in items:
                widget = items[idx].get("widget")
                if widget and hasattr(widget, "deleteLater"):
                    widget.deleteLater()
                del items[idx]

        # Rebuild drawer items for the new document context
        self.config.dikt["toolbox"][0]["items"] = self.init_drawer_application()

        # Rebuild toolbox UI without destroying the toolbox instance
        super().build_toolbox({"toolbox": self.config.dikt.get("toolbox", {})})
        return self

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.config.dikt["toolbox"][0]["items"] = self.init_drawer_application()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
