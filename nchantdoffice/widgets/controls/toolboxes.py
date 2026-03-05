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
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantrs.widgets.controls.toolboxes import NchantdToolBox
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.media.editors.editors import NchantdEntryBox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.panes.panes import NchantdPane
from nchantdoffice.widgets.panes.search import NchantdLLMQueryPane, NchantdWebSearchPane, NchantdApplicationSearchPane
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "toolboxes.yaml")


class NchantdOfficeApplicationToolBox(NchantdToolBox):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeApplicationToolBox"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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
        self.add_node = NchantdButton(self, cfg).initWidget()
        self.add_drawer_item(self.add_node, 0, 0)
        return self

    def add_settings_drawer(self):
        """"""
        return self

    def add_tabs_drawer(self):
        """"""
        cfg = {"action": "add_tab"}
        self.add_tab = NchantdButton(self, cfg).initWidget()
        self.add_drawer_item(self.add_tab, 0, 0)
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

    def init_drawer_node(self):
        """"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.config.dikt["toolbox"][10].get("items", {})
        cnt = 0
        return self

    def init_drawer_tabs(self):
        """"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.config.dikt["toolbox"][20].get("items", {})
        cnt = 0
        return self

    def init_drawer_tools(self):
        """"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.config.dikt["toolbox"][30].get("items", {})
        cnt = 0
        return self

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.config.dikt["toolbox"][0]["items"] = self.init_drawer_application()
        # self.config.dikt["toolbox"][10]["items"] = self.init_drawer_node()
        # self.config.dikt["toolbox"][20]["items"] = self.init_drawer_tabs()
        # self.config.dikt["toolbox"][30]["items"] = self.init_drawer_tools()
        
        # Connect signals for dynamic toolbox population
        self._connect_pane_signals()
        return self

    def _connect_pane_signals(self):
        """Connect to signals from other panes for dynamic toolbox updates"""
        # Connect to toolbar document_created signal
        if hasattr(self.app.view, 'toolbar') and hasattr(self.app.view.toolbar, 'document_created'):
            self.app.view.toolbar.document_created.connect(self._on_document_created)
        
        # Connect to tree document_selected signal  
        if hasattr(self.app.view, 'panes') and hasattr(self.app.view.panes, 'left'):
            tree = self.app.view.panes['left'].tree if hasattr(self.app.view.panes['left'], 'tree') else None
            if tree and hasattr(tree, 'document_selected'):
                tree.document_selected.connect(self._on_document_selected)
        
        # Connect to tabs current_document_changed signal
        if hasattr(self.app.view, 'panes') and hasattr(self.app.view.panes, 'center'):
            tabs = self.app.view.panes['center'].tabs if hasattr(self.app.view.panes['center'], 'tabs') else None
            if tabs and hasattr(tabs, 'current_document_changed'):
                tabs.current_document_changed.connect(self._on_document_changed)
    
    def _on_document_created(self, doc_type):
        """Handle new document created from toolbar"""
        logma.info(f"Toolbox: Document created - {doc_type}")
        # Get document class and populate toolbox with its tools
        doc_class = self._get_document_class_for_type(doc_type)
        if doc_class and hasattr(doc_class, 'get_pyffice_tools'):
            tools = doc_class.get_pyffice_tools()
            self._populate_tools_drawer(tools)
    
    def _on_document_selected(self, document):
        """Handle document selected from tree"""
        if document and isinstance(document, NchantdOfficeDocument):
            logma.info(f"Toolbox: Document selected - {document.PYTYPE}")
            if hasattr(document, 'get_pyffice_tools'):
                tools = document.get_pyffice_tools()
                self._populate_tools_drawer(tools)
    
    def _on_document_changed(self, document):
        """Handle active document changed in tabs"""
        if document and isinstance(document, NchantdOfficeDocument):
            logma.info(f"Toolbox: Document changed - {document.PYTYPE}")
            if hasattr(document, 'get_pyffice_tools'):
                tools = document.get_pyffice_tools()
                self._populate_tools_drawer(tools)
    
    def _get_document_class_for_type(self, doc_type):
        """Get document class for a given type string"""
        from nchantdoffice.widgets.documents.calendars import NchantdOfficeCalendar
        from nchantdoffice.widgets.documents.filesystems import NchantdOfficeFileSystem
        
        type_map = {
            'calendar': NchantdOfficeCalendar,
            'filesystem': NchantdOfficeFileSystem,
            'document': NchantdOfficeDocument,
        }
        return type_map.get(doc_type, NchantdOfficeDocument)
    
    def _populate_tools_drawer(self, tools):
        """Populate the tools drawer with tools from document's get_pyffice_tools()"""
        if not tools:
            return
        
        # Ensure tools drawer exists
        if 30 not in self.config.dikt["toolbox"]:
            self.config.dikt["toolbox"][30] = {"items": {}}
        
        items = self.config.dikt["toolbox"][30].get("items", {})
        cnt = 0
        
        for tool in tools:
            default_action = {"action": "insert_object", "type": "custom"}
            if cnt not in items:
                items[cnt] = default_action
            
            cfg = {
                "text": tool.get('label', 'Tool'),
                "action": tool.get('id', 'tool'),
                "layout": "horizontal",
                "size": ["auto", 30],
                "handler": getattr(self, f"cmd_{tool.get('method', 'noop')}", self.cmd_noop),
            }
            tool_button = NchantdButton(self, cfg).initWidget()
            items[cnt]["widget"] = tool_button
            cnt += 1
        
        self.config.dikt["toolbox"][30]["items"] = items
        logma.info(f"Toolbox: Populated {len(tools)} tools")
    
    def cmd_noop(self, event, *args, **kwargs):
        """No-op command placeholder"""
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
