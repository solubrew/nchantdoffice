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
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from nchantrs.libraries import pyqt
from nchantrs.widgets.groups import NchantdGridScrollGroupBox, NchantdGroup
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument, NchantdOfficeDocumentManager
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.items.catalogs import NchantdCatalogItem
from ogma.logma import Logma
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.forms.forms import NchantdForm
from nchantdoffice.widgets.panes.forms import NchantdNewFormItemPane
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.widgets import NchantdWidget

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "forms.yaml")


class NchantdOfficeForm(NchantdForm):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdForm"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self):
        """"""
        super().initModel()
        self.document = self.app.model.codex.init_form()
        self.document.load_document()
        self.context_menu_name = "context.document.form"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
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
        # if self.toolbox_config is None:
        #     return None
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_selection_config()
        self.toolbox_config[300]["items"] = self.init_drawer_object_config()
        self.toolbox_config[500]["items"] = self.init_drawer_quickstart()


class NchantdOfficeContactForm(NchantdForm):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeContactForm")
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
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeFormManager(NchantdOfficeDocumentManager):
    """TODO: take an excel upload and convert it into and form and deploy it as a google form in a few clicks"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeFormManager"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.catalog = self
        self.form = None
        self.button_bar = None
        self.selected_form = None
        self.forms = []
        self.available_items = []
        self.select_form_compatibility = None
        self.form_catalog_group = None
        self.form_view_group = None
        self.new_item_pane = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.available_items = [
            {
                "text": "Blank",
                "action": "add_form_blank",
                "size_policy": "fixed",
                "width": 60,
                "height": 60,
                "widget": NchantdOfficeForm,
            },
            {
                "text": "Contact",
                "action": "add_form_contact",
                "size_policy": "fixed",
                "width": 60,
                "height": 60,
                "widget": NchantdOfficeContactForm,
            },
            {
                "text": "Issue",
                "action": "add_form_issue",
                "size_policy": "fixed",
                "width": 60,
                "height": 60,
                "widget": NchantdOfficeContactForm,
            },
            {
                "text": "New Feature",
                "action": "add_form_issue",
                "size_policy": "fixed",
                "width": 60,
                "height": 60,
                "widget": NchantdOfficeContactForm,
            },
        ]
        cfg = {}
        self.document = self.app.model.codex.init_forms_manager(cfg)
        self.document.load_document()
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        fcs_cfg = {
            "layout": "horizontal",
            "size": ["auto", 30],
            "label": "Select Form Compatibility:",
            "options": self.get_form_compatibility_options(),
        }
        self.form_compatibility_select = NchantdDropDown(self, fcs_cfg)
        cfg["buttons"] = {
            0: {"name": "select_form_compatibility", "widget": self.form_compatibility_select},
            1: {"action": "add_data_source_connection"},
            2: "_insert_stretch",
        }
        super().initView(cfg)
        manager_layout = pyqt.QHBoxLayout()
        # self.form_catalog_group = NchantdGridScrollGroupBox()
        # self.form_catalog_group.setTitle("Select Form Item")
        # self.form_catalog_group.set_size(300)
        # self.form_catalog_group.limit_horizontal()
        # self.build_form_catalog()
        # manager_layout.addLayout(self.form_catalog_group.layout)
        self.form_view_group = NchantdGridScrollGroupBox()
        self.form_view_group.setTitle("View or Modify Form")
        self.form_view_group.limit_horizontal()
        self.build_form()
        manager_layout.addLayout(self.form_view_group.layout)
        self.layout.addLayout(manager_layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_form(self, form):
        """"""
        self.selected_form = form
        self.forms.append(form)

    def add_form_item(self, item):
        """"""
        self.selected_form.add_item(item)

    def build_form(self):
        """"""

        row, col = 0, 0
        if self.selected_form is None:
            self.build_form_blank(row, col)
            row += 2
        else:
            for item in self.selected_form.items:
                self.form_view_group.addWidget(item, row, col)
                row += 1
        cfg = {}
        new_item_pane_group = NchantdGroup(self, cfg)
        new_item_pane_group.setTitle("Add New Form Item")
        new_item_pane_group_layout = pyqt.QVBoxLayout()
        new_item_pane_group.setLayout(new_item_pane_group_layout)
        cfg = {"size": ["auto", "auto"]}
        self.new_item_pane = NchantdNewFormItemPane(self, cfg).initWidget()
        new_item_pane_group_layout.addWidget(self.new_item_pane)
        self.form_view_group.addWidget(new_item_pane_group, row, col)
        return self

    def build_form_blank(self, row, col):
        """"""
        cfg = {
            "text": "This is a Blank Form that can be used to build a new form to be used in a survey or inside the Nchantd Office Application itself",
            "font": {"size": 30, "type": "Arial", "weight": "bold"},
            "wrap_limit": 1000,
            "size": ["auto", "auto"],
        }
        self.form_view_group.addWidget(NchantdLabel(self, cfg).initWidget(), row, col)
        form_details_group = pyqt.QGroupBox()
        form_details_group.setTitle("Form Details")
        form_details_group_layout = pyqt.QGridLayout()
        form_details_group.setLayout(form_details_group_layout)
        cfg = {
            "label": "Select Image to Use in Header",
            "size": [100, "auto"],
            "layout": "horizontal",
            "entrybox": {"size": ["auto", "auto"]},
        }
        self.form_header_image_entry = NchantdLabeledEntry(self, cfg).initWidget()
        form_details_group_layout.addWidget(self.form_header_image_entry, 0, 0)
        cfg = {
            "label": "Enter Form Title: ",
            "size": [100, "auto"],
            "layout": "horizontal",
            "entrybox": {"size": ["auto", "auto"]},
        }
        self.form_name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        form_details_group_layout.addWidget(self.form_name_entry, 1, 0)
        cfg = {
            "label": "Enter Form Description: ",
            "size": [100, "auto"],
            "layout": "horizontal",
            "entrybox": {"size": ["Auto", 90]},
        }
        self.form_description_entry = NchantdLabeledEntry(self, cfg).initWidget()
        form_details_group_layout.addWidget(self.form_description_entry, 0, 1, 2, 1)
        row += 1
        self.form_view_group.addWidget(form_details_group, row, col)

    def build_form_catalog(self):
        """"""
        row, col = 0, 0
        for item in self.available_items:
            if isinstance(item, dict):
                item = NchantdCatalogItem(self, item).initWidget()
            self.form_catalog_group.addWidget(item, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def cmd_select_form_compatibility(self):
        """"""

    def cmd_add_form_blank(self):
        """"""

    def cmd_image_file_select(self):
        """"""

    def cmd_on_change_form_title(self):
        """"""

    def create_data_table(self):
        """"""
        df = super().create_data_table()
        columns = []
        data = []
        df = DataFrame(data, columns=columns)
        return df

    def get_form_compatibility_options(self):
        """"""
        options = ["Google Forms", "Nchantd Office", ""]
        return options

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        options = ["Google Forms", "Nchantd Office"]
        cfg = {
            "label": "Form Compatibility: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.form_compatibility_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.form_compatibility_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Select Default Response Type",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.form_default_response_check = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.form_default_response_check
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Select Default Response Trigger",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.form_default_response_trigger_check = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.form_default_response_trigger_check
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "text": "Set Default Answer Required",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.form_default_answer_required_check = NchantdCheckbox(self, cfg)
        items[cnt]["widget"] = self.form_default_answer_required_check
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "text": "Set Default Always Asked",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.form_default_always_asked_check = NchantdCheckbox(self, cfg)
        items[cnt]["widget"] = self.form_default_always_asked_check
        cnt += 1
        return items

    def init_drawer_input_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action
        options = []
        cfg = {
            "label": "",
            "layout": "horizontal",
            "options": options,
        }
        self.validation_options_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.validation_options_select
        cnt += 1
        return items

    def init_drawer_connections(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        options = ["Google Forms", "YouForm", "Notion Forms", "Nchantd Office"]
        cfg = {
            "label": "Form Service: ",
            "layout": "horizontal",
            "options": options,
        }
        self.calendar_service_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.calendar_service_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Name: ",
            "layout": "horizontal",
        }
        self.calendar_account_name = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.calendar_account_name
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "text": "Connect to Service",
            "layout": "horizontal",
        }
        self.service_connect_button = NchantdButton(self, cfg)
        items[cnt]["widget"] = self.service_connect_button
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        # self.toolbox_config[200]["items"] = self.init_drawer_input_config()
        self.toolbox_config[300]["items"] = self.init_drawer_connections()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def select_form(self, form_name):
        """"""
        self.selected_form = self.forms[form_name]


class NchantdOfficeFeedback(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeFeedback"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
