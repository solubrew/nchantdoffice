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
from nchantrs.utilities.utils import lookup
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.panes.catalogs import NchantdNewNodePane
from nchantrs.dialogs.files import NchantdFileOpenSigil
from nchantdoffice.dialogs.imports import NchantdGoogleDriveSigil
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxGroup, NchantdCheckbox
from nchantrs.widgets.controls.radios import NchantdRadioButtonGroup
from pyffice.web.url import PyfficeURL
from kahndor.logma import Logma
from subtrix.utilities import uuid

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
logma.off()

# ====================================================================================================================||
pxcfg = join(here, "_data_", "new.yaml")


class NchantdOfficeNewDocumentPane(NchantdNewNodePane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNewDocumentPane").override(cfg))
        self.connect_gfile = None
        self.open_file = None
        self.file_path = None
        self.import_file = None
        self.unique_options = None
        self.multiple_options = None
        self.file_path_label = None

    def initModel(self):
        """"""
        super().initModel()

        return self

    def initView(self):
        """
        :param file_type:
        :return:
        """
        logma.info(f"Ran")
        super().initView()
        # if self.active_item is not None:
        #     self.update_pane(self.active_item)
        return self

    def accept(self, action=None, app=None, params=None):
        """
        :return:
        """
        logma.info("New Document Accept")
        self.ok = True
        super().accept()
        self.unshow_file_path()
        self.update_pane()
        return self

    def add_document(self, tabset, widgdata=None, db="db"):
        """"""
        logma.info(f"Widgdata {widgdata}")
        if widgdata is None:
            widgdata = self.active_item.action.action["parameters_dict"]
            logma.info(f"Widgdata {widgdata}")
        if self.ok:
            name = self.tab_name_entry.textbox.entry_data
            pid = self.app.view.panes["left"].tree.model.current_node.nid
            self.app.view.panes[tabset].model.max_position += 1
            pos = self.app.view.panes[tabset].model.max_position
            document_nm = self.active_item.document_nm
            widget = self.active_item.widget
            # widgdata = kahndor.Instruct().override(widgdata).dikt
            # if self.active_item.selected_unique_option is not None:
            #     if self.active_item.selected_unique_option.get("widget_code", None):
            #         widget = lookup_widget(self.active_item.selected_unique_option["widget_code"])
            did = self.active_item.did
            context = ""
            content = {}
            syntax = ""
            doc_type = self.active_item.action.action["lookup_code_txt"]
            if "add_http_media" in doc_type:
                logma.info(f"Widgdata {widgdata}")
                link = PyfficeURL(self.active_item.params)
                link.load_unit()
                content = link.to_dict()
                code = self.active_item.params.get("url_code", None)
                if code is None:
                    code = self.active_item.params.get("file_type", None)
                content["unit"]["original_path"] = self.app.model.get_link(code)
                logma.info(f"Content {content}")
            document = {
                "name": name,
                "description": "",
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
            self.app.model.add_document(document, did, pid, pos, widget, widgdata, doc_type, tabset, db, True)
            self.app.view.panes["left"].tree.model.current_node.updateTabs(tabset)
        return self

    def add_node(self, tree="left", widgdata=None):
        """"""
        super().add_node(tree, widgdata)
        return self

    def add_note(self):
        """"""
        name = self.active_item.name
        pid = self.app.view.panes["left"].tree.model.current_node.nid
        position = self.app.view.gui.set_position("right")
        widgdata = {}
        self.app.model.add_note(name, pid, position, widgdata)
        return self

    def add_subtree(self):
        """"""
        super().add_subtree()
        # mass create one or more nodes and associated tabs
        # use this for import of cherrytree
        # use this for research subtree
        """
        """
        d = {
            "unique_options": [
                {"name": "Decade"},
                {"name": "Year"},
                {"name": "Month"},
                {"name": "Week"},
                {"name": "Day"},
            ]
        }
        return self

    def add_tab(self, tabset, widgdata=None):
        """"""
        if widgdata is None:
            widgdata = {}
        # widgdata["doc_type"] = self.active_item.document_nm
        if self.active_item.document_txt in ("http", "api"):
            for key, item in self.active_item.params.items():
                logma.info(f"Key {key} Item {item}")
                widgdata[key] = item
            # widgdata["url_code"] = self.active_item.params.get("url_code", None)
            # widgdata["is_app"] = self.active_item.params.get("is_app", None)
        # TODO: how to integrate various formats across tools for specific tool types like a local file to open excel
        #  and a web app for google sheets...there is value to keeping that interaction native to the google sheet instead
        #  of automatically downloading and converting to a local version but how to integrate this switching
        # if self.load_google:
        #     # TODO create a load google dialog mimic file open dialog but connect to google drive using a browser/api
        #     widgdata["url"] = self.active_item.file_path.file_selected
        if self.open:
            widgdata["path"] = self.file_path.file_selected
        super().add_tab(tabset, widgdata)
        # TODO: develop the widget_code override based on unique options selections
        # how to implement subtree adds or multi tabs like creating a source tab for each web browser tab
        return self

    def add_research_subtree(self, topic):
        """"""
        subtree = self.config.dikt["subtrees"]["research"]["dstruct"]["<topic>"]["nodes"]
        details = {"<[topic]>": topic}
        for key, val in subtree.items():
            self.add_node(key)
            if val == "tabs":
                for tab in subtree[key]:
                    self.add_tab(tab)

    def add_bulk_node(self):
        """"""
        # TODO implement method

    def add_bulk_tab(self):
        """"""
        # TODO implement method

    def load_document(self):
        """"""
        self.document_obj = self.widget.open(self.active_item.file_path)
        return self

    def open_file_sigil(self, name=None, app=None, cfg=None):
        """"""
        file_sigil = NchantdFileOpenSigil("open", self.parent, self.config.override(cfg))
        self.file_path = file_sigil.initWidget()
        if self.file_path.file_selected:
            self.show_file_path()
            self.load_google = False
        return self

    def open_google_drive_viewer(self, name=None, app=None, cfg=None):
        """"""
        gdrive_sigil = NchantdGoogleDriveSigil(self.parent, self.config.override(cfg))
        self.gdrive_path = gdrive_sigil.initWidget()
        if self.ok:
            self.gdrive_path.file_selected
            self.show_file_path()
            self.load_google = True
        return self

    def show_checkboxes(self):
        """"""
        # TODO implement method
        return self

    def show_file_path(self):
        """"""
        logma.info(f"File Path {self.file_path.file_selected}")
        cfg = {"text": self.file_path.file_selected, "readonly": True, "size": [600, 0]}
        self.file_path_label = NchantdLabel(self, self.config.override(cfg)).initWidget()
        self.left_side_layout.addWidget(self.file_path_label)
        # self.add_field(self.file_path_label)
        # need to load the file and determine if there are multiple pages/tabs like an excel file
        # if there are then a selection list is presented for each page/tab
        self.open = True
        self.new = False
        return self

    def unshow_file_path(self):
        """"""
        if self.file_path_label is not None:
            self.left_side_layout.removeWidget(self.file_path_label)
            self.file_path_label.setParent(None)
            self.file_path_label.deleteLater()
            self.file_path_label = None
            self.open = False
            self.new = True
        return self

    def show_google_drive_button(self):
        """"""
        if self.connect_gfile is not None:
            return self
        gdocs = {
            "script": "docs",
            "matrix": "sheets",
            "image": "drive",
            "form": "forms",
            "pdf": "drive",
            "notebook": "drive",
            "video": "drive",
        }
        gtype = gdocs.get(self.active_item.document_txt, None)
        if gtype is None:
            self.unshow_google_drive_button()
            # raise Exception(f"Google Doc Type Not Supported {self.active_item.document_nm}")
        command = f"load_google_{gtype}"
        self.config.override({"buttons": {command: lookup(self.app, command)}})
        self.config.dikt["action"] = self.config.dikt["buttons"][command]["lookup_code_txt"]

        self.connect_gfile = NchantdButton(self, self.config.dikt["buttons"][command]).initWidget()
        self.connect_gfile.set_handler(self.open_google_drive_viewer, self.config.dikt)
        self.document_buttons_layout.addWidget(self.connect_gfile)
        return self

    def show_import_file_button(self):
        """"""
        if self.import_file is not None:
            return self
        self.app.model.has_library = True
        if self.app.model.has_library:
            command = f"import_{self.active_item.file_type}"
            self.config.override({"buttons": {command: lookup(self.app, command)}})
            self.config.dikt["action"] = self.config.dikt["buttons"][command]["lookup_code_txt"]
            self.import_file = NchantdButton(self, self.config.dikt["buttons"][command]).initWidget()
            self.import_file.set_handler()
            self.document_buttons_layout.addWidget(self.import_file)
        return self

    def show_local_drive_button(self):
        """"""
        if self.open_file is not None:
            return self
        logma.info(f"Action open_{self.active_item.file_type}")
        self.open_file = NchantdButton(self, {"action": f"open_{self.active_item.file_type}"}).initWidget()
        params = self.config
        self.open_file.set_handler(self.open_file_sigil, params)
        self.document_buttons_layout.addWidget(self.open_file)
        return self

    def show_multiple_options(self):
        """"""
        if self.multiple_options is not None:
            return self
        logma.info(f"Multiple Options {self.active_item.multi_options}")
        cfg = {"text": "Select Parameters", "multiple_options": [x["name"] for x in self.active_item.multi_options]}
        self.multiple_options = NchantdCheckboxGroup(self, cfg)
        self.multiple_options.initWidget()
        self.center_layout.addWidget(self.multiple_options)

    def show_radio_buttons(self):
        """"""
        if self.unique_options is not None:
            return self
        logma.info(f"Unique Options {self.active_item.unique_options}")
        cfg = {"text": "Select Option", "unique_options": [x["name"] for x in self.active_item.unique_options]}
        self.unique_options = NchantdRadioButtonGroup(self, cfg)
        self.unique_options.initWidget()
        self.center_layout.addWidget(self.unique_options)
        return self

    def unshow_local_drive_button(self):
        """"""
        if self.open_file is not None:
            self.document_buttons_layout.removeWidget(self.open_file)
            self.open_file.setParent(None)
            self.open_file.deleteLater()
            self.open_file = None

    def unshow_google_drive_button(self):
        """

        :return:
        """
        if self.connect_gfile is not None:
            self.document_buttons_layout.removeWidget(self.connect_gfile)
            self.connect_gfile.setParent(None)
            self.connect_gfile.deleteLater()
            self.connect_gfile = None
        return self

    def unshow_import_file_button(self):
        """"""
        if self.import_file is not None:
            self.document_buttons_layout.removeWidget(self.import_file)
            self.import_file.setParent(None)
            self.import_file.deleteLater()
            self.import_file = None
        return self

    def unshow_unique_options(self):
        """"""
        if self.unique_options is not None:
            self.center_layout.removeWidget(self.unique_options)
            self.unique_options.setParent(None)
            self.unique_options.deleteLater()
            self.unique_options = None

    def unshow_muliple_options(self):
        """"""
        if self.multiple_options is not None:
            self.center_layout.removeWidget(self.multiple_options)
            self.multiple_options.setParent(None)
            self.multiple_options.deleteLater()
            self.multiple_options = None

    def update_checkboxes(self):
        """"""
        if self.active_item.has_multiple_options:
            self.show_checkboxes()
        return self

    def update_file_buttons(self):
        """"""
        logma.info(f"Update File Buttons {self.active_item.has_google_options}")
        if self.active_item.has_google_options:
            self.show_google_drive_button()
        else:
            self.unshow_google_drive_button()
        if self.active_item.has_local_options:
            self.show_local_drive_button()
            self.show_import_file_button()
        else:
            self.unshow_local_drive_button()
            self.unshow_import_file_button()
        return self

    def update_pane(self):
        """
                TODO: set default pane handlers to create root node
            update_pane populates the buttons with new handlers
            show document type in the top entry of the pane
            tab name will be auto populated as a uuid length 5
            color select button is the same
            icon select button is the same
            google drive button is the same
            local drive button is the same
            import file button is the same
            Subtree Node needs to alter the pane significantly to show various import options
                cherrytree, filesystem
        :param item:
        :return:
        """
        logma.info(f"Update Pane")
        self.file_path = None
        self.unshow_file_path()
        super().update_pane()
        self.update_file_buttons()
        self.unshow_unique_options()
        self.update_radio_buttons()
        self.unshow_muliple_options()
        self.multiple_options = None
        self.update_checkboxes()
        logma.info(f"Update Pane")
        return self

    def update_radio_buttons(self):
        """"""
        if self.active_item.has_unique_options:
            logma.info(f"Has Unique Options")
            self.show_radio_buttons()
        else:
            self.unshow_unique_options()
        return self


class NchantdOfficeNewSubtreePane(NchantdOfficeNewDocumentPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeNewSubtreePane").override(cfg))

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        # radio option group
        # have a research subtree that will allow for an input category/categories
        # then it will create a node with a tabset for each category and a highest level node combining all categories
        # the tabset will have a deep research ai prompt tab, a notes tab, a links tab, multiple pdf tabs as needed
        # create a node for any sub catgories and then a connected tabset

        # option - file system import
        # option - cherry tree import

        #

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
