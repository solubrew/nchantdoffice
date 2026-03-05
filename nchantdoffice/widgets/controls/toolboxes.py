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
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantrs.widgets.controls.toolboxes import NchantdToolBox
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.media.editors.editors import NchantdEntryBox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.panes.panes import NchantdPane
from nchantdoffice.widgets.panes.search import NchantdLLMQueryPane, NchantdWebSearchPane, NchantdApplicationSearchPane
from nchantdoffice.widgets.menus.context_manager import ToolboxContextMenuMixin

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
# logma.off()  # Disabled - causes dialog issues (P0 fix)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "toolboxes.yaml")


class NchantdOfficeApplicationToolBox(ToolboxContextMenuMixin, NchantdToolBox):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeApplicationToolBox"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        
        # Initialize context menu mixin for toolbox
        ToolboxContextMenuMixin.__init__(self)
        
        # Search functionality
        self.search_input = None
        self._original_items = []
        self._search_results = []

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
        
        # Initialize search
        self._init_search()
        
        return self

    def _init_search(self):
        """Initialize search functionality for toolbox"""
        # Create search input widget at the top
        from nchantrs.widgets.media.editors.editors import NchantdEntryBox
        from nchantrs.widgets.controls.buttons import NchantdButton
        
        # Store original toolbox items for search
        self._original_items = []
        self._search_results = []
        
        logma.info("Toolbox search initialized")
    
    def search_toolbox(self, query):
        """Search toolbox items by query.
        
        Args:
            query: Search string to match against toolbox item labels
            
        Returns:
            List of matching toolbox items
        """
        if not query:
            return self._original_items
        
        query_lower = query.lower()
        results = []
        
        for item in self._original_items:
            # Search in label, tooltip, and id
            label = getattr(item, 'text', '').lower()
            tooltip = getattr(item, 'toolTip', lambda: '')().lower()
            item_id = getattr(item, 'id', '').lower() if hasattr(item, 'id') else ''
            
            if (query_lower in label or 
                query_lower in tooltip or 
                query_lower in item_id):
                results.append(item)
        
        self._search_results = results
        return results
    
    def on_search_text_changed(self, text):
        """Handle search text input change.
        
        Args:
            text: The search query text
        """
        if not text:
            self._clear_search()
            return
        
        # Store original if not stored
        if not self._original_items:
            self._collect_original_items()
        
        # Perform search
        results = self.search_toolbox(text)
        self._display_search_results(results)
        
        logma.info(f"Search '{text}' found {len(results)} results")
    
    def _collect_original_items(self):
        """Collect all toolbox items for searching"""
        self._original_items = []
        for i in range(self.count()):
            widget = self.widget(i)
            if widget and widget != getattr(self, 'search_widget', None):
                self._original_items.append(widget)
    
    def _display_search_results(self, results):
        """Display filtered search results.
        
        Args:
            results: List of matching toolbox items to display
        """
        # Hide all original items first
        for item in self._original_items:
            item.setVisible(False)
        
        # Show matching items
        for result in results:
            result.setVisible(True)
    
    def _clear_search(self):
        """Clear search and restore all items"""
        # Restore all items
        for item in self._original_items:
            item.setVisible(True)
        
        self._search_results = []

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
        """""Node drawer - actions for tree nodes"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.config.dikt.get("node_toolbox", {}).get("10", {}).get("items", {})
        cnt = 0
        
        # Node actions
        cfg = {"layout": "horizontal"}
        buttons = {
            0: {"action": "add_node", "label": "Add Node", "icon": "plus"},
            1: {"action": "delete_node", "label": "Delete", "icon": "trash"},
            2: {"action": "rename_node", "label": "Rename", "icon": "edit"},
        }
        buttons = condor.Instruct(buttons).override(cfg).dikt
        self.node_buttonbar = NchantdButtonBar(self, cfg).initWidget(buttons)
        items[cnt] = {"widget": self.node_buttonbar}
        cnt += 1
        
        # Node navigation
        cfg = {"layout": "horizontal"}
        buttons = {
            0: {"action": "move_up", "label": "Move Up", "icon": "arrow-up"},
            1: {"action": "move_down", "label": "Move Down", "icon": "arrow-down"},
            2: {"action": "move_left", "label": "Move Left", "icon": "arrow-left"},
            3: {"action": "move_right", "label": "Move Right", "icon": "arrow-right"},
        }
        buttons = condor.Instruct(buttons).override(cfg).dikt
        self.node_nav_bar = NchantdButtonBar(self, cfg).initWidget(buttons)
        items[cnt] = {"widget": self.node_nav_bar}
        
        return items

    def init_drawer_tabs(self):
        """""Tabs drawer - actions for tab management"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.config.dikt.get("node_toolbox", {}).get("20", {}).get("items", {})
        cnt = 0
        
        # Tab actions
        cfg = {"layout": "horizontal"}
        buttons = {
            0: {"action": "new_tab", "label": "New Tab", "icon": "plus"},
            1: {"action": "close_tab", "label": "Close", "icon": "close"},
            2: {"action": "duplicate_tab", "label": "Duplicate", "icon": "copy"},
        }
        buttons = condor.Instruct(buttons).override(cfg).dikt
        self.tabs_buttonbar = NchantdButtonBar(self, cfg).initWidget(buttons)
        items[cnt] = {"widget": self.tabs_buttonbar}
        cnt += 1
        
        # Tab organization
        cfg = {"layout": "horizontal"}
        buttons = {
            0: {"action": "tile_tabs", "label": "Tile", "icon": "grid"},
            1: {"action": "cascade_tabs", "label": "Cascade", "icon": "stack"},
            2: {"action": "next_tab", "label": "Next", "icon": "arrow-right"},
            3: {"action": "prev_tab", "label": "Prev", "icon": "arrow-left"},
        }
        buttons = condor.Instruct(buttons).override(cfg).dikt
        self.tabs_org_bar = NchantdButtonBar(self, cfg).initWidget(buttons)
        items[cnt] = {"widget": self.tabs_org_bar}
        
        return items

    def init_drawer_tools(self):
        """""Tools drawer - utilities and settings"""
        default_action = {"action": "insert_object", "type": "custom"}
        items = self.config.dikt.get("node_toolbox", {}).get("30", {}).get("items", {})
        cnt = 0
        
        # Tools actions
        cfg = {"layout": "horizontal"}
        buttons = {
            0: {"action": "record_macro", "label": "Record", "icon": "record"},
            1: {"action": "play_macro", "label": "Play", "icon": "play"},
            2: {"action": "stop_macro", "label": "Stop", "icon": "stop"},
        }
        buttons = condor.Instruct(buttons).override(cfg).dikt
        self.tools_buttonbar = NchantdButtonBar(self, cfg).initWidget(buttons)
        items[cnt] = {"widget": self.tools_buttonbar}
        cnt += 1
        
        # Settings
        cfg = {"layout": "horizontal"}
        buttons = {
            0: {"action": "preferences", "label": "Settings", "icon": "settings"},
            1: {"action": "shortcuts", "label": "Shortcuts", "icon": "keyboard"},
            2: {"action": "customize", "label": "Customize", "icon": "customize"},
        }
        buttons = condor.Instruct(buttons).override(cfg).dikt
        self.settings_buttonbar = NchantdButtonBar(self, cfg).initWidget(buttons)
        items[cnt] = {"widget": self.settings_buttonbar}
        
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.config.dikt["toolbox"][0]["items"] = self.init_drawer_application()
        
        # Initialize node, tabs, and tools drawers if node_toolbox exists
        if "node_toolbox" in self.config.dikt:
            self.config.dikt["node_toolbox"][10]["items"] = self.init_drawer_node()
            self.config.dikt["node_toolbox"][20]["items"] = self.init_drawer_tabs()
            self.config.dikt["node_toolbox"][30]["items"] = self.init_drawer_tools()
        
        # Create a drawer for Pyffice document-specific tools
        self._init_pyffice_drawer()
        
        return self
    
    def _init_pyffice_drawer(self):
        """Initialize the Pyffice document tools drawer"""
        # This drawer will be populated when a document is selected
        # Store reference for dynamic updates
        self.pyffice_drawer_items = {}
        self.current_pyffice_tools = []
        
    def on_document_changed(self, document):
        """Handle document change - populate toolbox with document-specific tools.
        
        This method should be called when:
        - A new document is created (from toolbar)
        - A document is selected in the tree (left pane)
        - The active tab changes (center pane)
        
        Args:
            document: The active NchantdOfficeDocument widget
        """
        if document is None:
            return
            
        # Get Pyffice tools from the document
        if hasattr(document, 'get_pyffice_tools'):
            tools = document.get_pyffice_tools()
            self.current_pyffice_tools = tools
            logma.info(f"Loaded {len(tools)} tools for document type: {type(document).__name__}")
            self._populate_pyffice_drawer(tools)
        elif hasattr(document, 'PYTYPE') and document.PYTYPE is not None:
            # Fallback: try to get tools from PYTYPE class
            pyftype = document.PYTYPE
            if hasattr(pyftype, 'get_pyffice_tools'):
                tools = pyftype.get_pyffice_tools()
                self.current_pyffice_tools = tools
                logma.info(f"Loaded {len(tools)} tools from PYTYPE: {pyftype.__name__}")
                self._populate_pyffice_drawer(tools)
        else:
            logma.info(f"Document {type(document).__name__} has no get_pyffice_tools method")
    
    def _populate_pyffice_drawer(self, tools):
        """Populate the Pyffice tools drawer with the given tools.
        
        Args:
            tools: List of tool dictionaries with 'id', 'icon', 'label', 'method'
        """
        # Create button bar for Pyffice tools
        if not tools:
            return
            
        cfg = {"layout": "vertical", "justify": "left"}
        buttons = {}
        for i, tool in enumerate(tools):
            tool_id = tool.get('id', f'tool_{i}')
            tool_label = tool.get('label', tool_id)
            tool_method = tool.get('method', '')
            buttons[i] = {
                "action": tool_id,
                "label": tool_label,
                "icon": tool.get('icon', 'gear'),
                "handler": getattr(self, f'cmd_{tool_method}', None) if tool_method else None
            }
        
        buttons = condor.Instruct(buttons).override(cfg).dikt
        
        # Create or update the button bar
        if hasattr(self, 'pyffice_buttonbar'):
            # Update existing
            self.pyffice_buttonbar.initWidget(buttons)
        else:
            # Create new
            self.pyffice_buttonbar = NchantdButtonBar(self, cfg).initWidget(buttons)
            # Add to toolbox if drawer exists
            if 40 in self.config.dikt.get("toolbox", {}):
                self.config.dikt["toolbox"][40]["items"][0] = {"widget": self.pyffice_buttonbar}
    
    def cmd_run(self):
        """Run script/document"""
        logma.info("Run")
        return self
    
    def cmd_debug(self):
        """Debug script/document"""
        logma.info("Debug")
        return self
    
    def cmd_open_terminal(self):
        """Open terminal"""
        logma.info("Terminal")
        return self
    
    def cmd_format_code(self):
        """Format code"""
        logma.info("Format")
        return self
    
    def cmd_find_replace(self):
        """Find and replace"""
        logma.info("Find Replace")
        return self
    
    def cmd_spell_check(self):
        """Spell check"""
        logma.info("Spell Check")
        return self
    
    def cmd_word_count(self):
        """Word count"""
        logma.info("Word Count")
        return self
    
    def cmd_export_document(self):
        """Export document"""
        logma.info("Export")
        return self
    
    def on_document_created(self, doc_type):
        """Handle new document created from toolbar.
        
        Args:
            doc_type: The type of document created (e.g., 'add_script_document_nchantdscript')
        """
        logma.info(f"New document created in toolbox: {doc_type}")
        # Get the widget from the center pane
        center = None
        if hasattr(self.app, 'view') and hasattr(self.app.view, 'panes'):
            center = self.app.view.panes.get("center")
        
        if center:
            # Get the current widget
            widget = center.currentWidget()
            if widget:
                self.on_document_changed(widget)
    
    # Chart-specific commands
    def cmd_set_data_source(self):
        """Set chart data source"""
        logma.info("Set Data Source")
        return self
    
    def cmd_change_type(self):
        """Change chart type"""
        logma.info("Change Type")
        return self
    
    def cmd_apply_style(self):
        """Apply chart style"""
        logma.info("Apply Style")
        return self
    
    def cmd_toggle_legend(self):
        """Toggle legend"""
        logma.info("Toggle Legend")
        return self
    
    def cmd_edit_title(self):
        """Edit title"""
        logma.info("Edit Title")
        return self
    
    def cmd_configure_axes(self):
        """Configure axes"""
        logma.info("Configure Axes")
        return self
    
    def cmd_edit_series(self):
        """Edit series"""
        logma.info("Edit Series")
        return self
    
    def cmd_export_chart(self):
        """Export chart"""
        logma.info("Export Chart")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
