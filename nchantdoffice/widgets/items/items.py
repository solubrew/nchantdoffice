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
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.items.catalogs import NchantdCatalogItem
from nchantrs.utilities.utils import lookup
from nchantrs.widgets.widgets import NchantdAction
from nchantrs.widgets.items.nodes import NchantdTreeNode
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
logma.off()
debug = True

# ====================================================================================================================||
pxcfg = join(here, "_data_", "items.yaml")


class NchantdOfficeDocumentCatalogItem(NchantdCatalogItem):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent_widget = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeDocumentCatalogItem"))
        if self.parent_widget:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.action = None
        self.action_params = None
        self.document = None
        self.did = None
        self.document_nm = None
        self.file_type = None
        self.has_local_options = False
        self.has_google_options = False
        self.has_unique_options = False
        self.selected_unique_option = None
        self.has_multiple_options = False
        self.selected_multiple_options = []
        self.params = None
        self.file_path = None
        self.widget = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.file_type = self.config.dikt.get("file_type", None)
        action = self.config.dikt.get("action", None)
        self.action = NchantdAction(action, "base", self)
        action_slug = action[action.rfind("_") + 1 :]
        self.catalog.all_items["slug"] = self.catalog.all_items["name_txt"].apply(lambda x: x.lower().replace(" ", ""))
        self.document = self.catalog.all_items[self.catalog.all_items["slug"] == action_slug].to_dict("records")[0]
        self.document_nm = self.document.get("name_txt", None)
        self.document_txt = self.document.get("document_txt", None)
        self.widget = self.document.get("widget_txt", None)
        if self.document.get("parameters_dict", "") == "":
            self.document["parameters_dict"] = "{}"
        try:
            self.params = j.loads(self.document.get("parameters_dict", "{}").replace("'", '"').strip())
        except Exception as e:
            logma.info(self.document.get("parameters_dict", "{}").replace("'", '"').strip())
            logma.info(e)
            if debug:
                raise e
        # logma.info(f"Parameters: {self.params}")
        params = self.action.get_parameters()
        if int(params.get("google_drive_bit", 0)) == 1:
            self.has_google_options = True
        if int(params.get("local_drive_bit", 0)) == 1:
            self.has_local_options = True
        if self.params.get("unique_options", None):
            self.has_unique_options = True
            self.unique_options = self.params.get("unique_options", [])
        if self.params.get("multiple_options", None):
            self.has_multiple_options = True
            self.multiple_options = self.params.get("multiple_options", [])

        return self

    def initView(self, cfg=None):
        """"""
        cfg = {"size": [128, 128]}
        super().initView(cfg)
        self.setStyleSheet("QWidget {background-color: #4F5665}")
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeSourceCatalogItem(NchantdCatalogItem):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent_widget = parent
        self.config.override(
            kahndor.Instruct(pxcfg).select("NchantdOfficeSourceCatalogItem").override(parent.config).override(cfg)
        )
        self.requires_api_key = None
        self.is_data_source_available = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.requires_api_key = self.config.dikt.get("requires_api_key", True)
        self.is_data_source_available = self.config.dikt.get("is_data_source_available", False)
        action = self.config.dikt.get("action", None)
        # NOTE: instantiate a base NchantdAction from the config-supplied action string;
        # mirrors the pattern used in NchantdOfficeDocumentCatalogItem.initModel above.
        self.action = NchantdAction(action, "base", self)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        # add a checkbox to make the datasource available
        cfg = {"text": "Activate Data Source"}
        self.activation_checkbox = NchantdCheckbox(self, cfg).initWidget()
        cfg = {
            "options": [{"text": "API Key Required"}, {"text": "API Key Optional"}, {"text": "No API Key"}],
            "handler": self.cmd_update_api_key_requirements,
        }
        self.apikey_radio_buttons = NchantdRadioButtonGroup(self, cfg).initWidget()
        cfg = {"text": "API Key:", "handler": self.cmd_update_api_key_entry, "value": self.get_api_key}
        self.apikey = NchantdLabeledEntry(self, cfg).initWidget()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_update_api_key_requirements(self, event, *args, **kwargs):
        """Handle radio-button selection to update API key requirement mode.

        Maps radio-button index to requires_api_key values:
            0 = API Key Required  (True,  required=True)
            1 = API Key Optional (True,  required=False)
            2 = No API Key        (False, required=False)
        Persists the new mode to the app model data-source config table.
        """
        selected_index = self.apikey_radio_buttons.get_selected_index()
        if selected_index == 0:
            required = True
            required_flag = True
        elif selected_index == 1:
            required = True
            required_flag = False
        else:
            required = False
            required_flag = False
        self.requires_api_key = required
        # Persist to data-source config
        if hasattr(self, "app") and self.app and hasattr(self.app, "model"):
            self.app.model.update_data_source(self.nid, {"requires_api_key": required, "api_key_required": required_flag})
        return

    def cmd_update_api_key_entry(self, event, *args, **kwargs):
        """Handle API key entry widget edits.

        Reads the current value from the NchantdLabeledEntry widget and
        persists it to the app model data-source config table.
        Called on every textChanged signal from the entry field.
        """
        raw = self.apikey.get_value()
        api_key = raw if raw else ""
        # Persist to data-source config
        if hasattr(self, "app") and self.app and hasattr(self.app, "model"):
            self.app.model.update_data_source(self.nid, {"api_key_txt": api_key})
        return

    def get_api_key(self):
        """Return the stored API key for this data source.

        Pulls the api_key_txt value from the app model data-source config
        table for this node (self.nid).  Returns empty string if not set.
        """
        if hasattr(self, "app") and self.app and hasattr(self.app, "model"):
            row = self.app.model.get_data_source(self.nid)
            if row is not None:
                return row.get("api_key_txt", "")
        return ""


class NchantdOfficeTreeNode(NchantdTreeNode):
    """"""

    def __init__(self, parent, name, nid, node, children=DataFrame(), cfg=None):
        """ """
        super().__init__(parent, name, nid, node, children)
        self.parent_widget = parent
        self.config.override(
            kahndor.Instruct(pxcfg).select("NchantdOfficeTreeNode").override(parent.config).override(cfg)
        )

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
        self.set_as_current()

        return self

    def set_as_current(self):
        """Set this node as the current/focused node in the tree"""
        if hasattr(self, "app") and hasattr(self.app, "view") and hasattr(self.app.view.panes["left"], "tree"):
            tree = self.app.view.panes["left"].tree
            if tree is None:
                return self
            tree.setCurrentItem(self)
            tree.scrollToItem(self)
        return self

    def setText(self, column, text, store=True):
        """"""
        # logma.inspect_caller()
        super().setText(column, text)
        logma.info(f"Set Text: {text}")
        if store:
            if self.app.view.panes["left"].tree is not None:
                cfg = {"name_txt": text}
                self.app.model.update_node(self.app.model.get_current_node(), cfg)
            else:
                logma.info(f"Tree is None")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||