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
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.widgets.applications.applications import NchantdCloak, NchantdMainWindow
from nchantdoffice.models import NchantdOfficeCloakModel
from nchantdoffice.views import NchantdOfficeCloakView
from nchantdoffice.updates.db import NchantdOfficeDBUpdate
from kahndor.logma import Logma
from nchantrs.libraries import pyqt

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
logma.info(f"here: {here}")
pxcfg = join(here, "_data_", "nchantdoffice.yaml")


class NchantdOfficeCloak(NchantdCloak):
    """"""

    def __init__(self, name, instance=None, parent=None, cfg=None, args=None):
        """ """
        super().__init__(name, instance, parent, None, args)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCloak").override(cfg))
        self.config.override({"app": "nchantdoffice"})
        self.parent = parent
        logma.info(f"NchantdOfficeCloak: {self.config.dikt.get("config", None)}")
        if self.parent is None:
            self.parent = self
        self.main = NchantdOfficeMainWindow(self)
        self.model = NchantdOfficeCloakModel(name, self.instance, self)
        self.view = NchantdOfficeCloakView(self)
        self.dbupdate = NchantdOfficeDBUpdate(self)
        self.application_NCD = "40c94efb-d374-437f-a48b-3c6b843fd110"
        self.install = True
        self.primary_focus = "office_platform"
        self.is_installable = True
        self.is_install_optional = False
        self.has_comms = True
        self.has_library = True
        self.library_optional = True
        self.toolbox = None

    def run_on_launch(self):
        """Called on every application startup."""
        super().run_on_launch()
        self.model.set_today()
        # Restore last selected node or default to Home
        self.select_initial_node()
        return self

    def select_initial_node(self):
        """Restore last selected node on successive runs, fallback to Home."""
        # Get last selected node from preferences
        last_selected_id = self.config.dikt.get("preferences", {}).get("last_selected_node")

        # Find the tree widget
        tree = None
        if hasattr(self.main, "application_tree"):
            tree = self.main.application_tree.tree if hasattr(self.main.application_tree, "tree") else None

        if tree and hasattr(tree, "findItems"):
            # Try to restore last selected node
            if last_selected_id:
                items = tree.findItems(last_selected_id, pyqt.Qt.MatchExactly | pyqt.Qt.MatchRecursive, 0)
                if items:
                    tree.setCurrentItem(items[0])
                    return

            # Fallback to Home node
            home_items = tree.findItems("Home", pyqt.Qt.MatchExactly, 0)
            if home_items:
                tree.setCurrentItem(home_items[0])

    def save_selected_node(self, node_id):
        """Save selected node to preferences."""
        if "preferences" not in self.config.dikt:
            self.config.dikt["preferences"] = {}
        self.config.dikt["preferences"]["last_selected_node"] = node_id
        # Persist to storage (config system handles this automatically)
        if hasattr(self.config, "save"):
            self.config.save()

    def _on_tree_selection_changed(self, selected, deselected):
        """Handle tree selection change - save to preferences."""
        # Get selected node ID from selection model
        indexes = selected.indexes() if selected else []
        if indexes:
            # Get the node ID from the model
            node_id = indexes[0].data(pyqt.Qt.UserRole)
            if node_id:
                self.save_selected_node(node_id)


class NchantdOfficeMainWindow(NchantdMainWindow):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        logma.info(f"NchantdOfficeMainWindow init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeMainWindow").override(cfg))

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

    def hideEvent(self, event):
        """"""
        super().hideEvent(event)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
