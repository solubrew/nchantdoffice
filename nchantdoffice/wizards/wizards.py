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
from os import environ
from pathlib import Path
import datetime as dt
import time
import platform

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.wizards.apps import NchantdApplicationStartupWizard

from nchantdoffice.updates.db import NchantdOfficeDBUpdate

from subtrix.utilities import uuid
from nchantrs.widgets.browsers.downloads import CodecDownloadThread
from nchantrs.widgets.browsers.codecs.h264 import OpenH264Downloader

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
debug = True
if not log:
    logma.off()
# ====================================================================================================================||
pxcfg = join(here, "_data_", "wizards.yaml")


class NchantdOfficeApplicationStartupWizard(NchantdApplicationStartupWizard):
    """Startup Wizard for Nchantd Office Application"""

    def __init__(self, app=None, cfg=None):
        """ """
        super().__init__(app, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeApplicationStartupWizard")).override(cfg)
        cfg = {}
        self.db_update = NchantdOfficeDBUpdate(self, cfg)
        self.download_codec = None
        self.h264_codec = None

    def initView(self, args=None):
        """"""
        super().initView(args)
        # NOTE: add_journal_document() intentionally NOT called here. The journal
        # document is created on demand by the journal view, not eagerly at
        # startup. Eager creation caused a phantom Journal tab to appear in
        # every session and wrote a row to the DB before the user had logged in.
        # Keep this dormant; resurrect only with a clear UX reason.
        return self

    def add_journal_document(self):
        """"""
        did = uuid()
        widget = "journal"
        widgdata = {}
        doc_type = "journal"
        document = {
            "did": did,
            "name": "Journal",
            "compatibility": "pyffice",
            "type": "journal",
            "syntax": "plain-text",
            "description": "internal",
            "store_location": "",
            "encoding": "utf-8",
            "meta_data": {},
            "widget": widget,
            "pyffice_version_txt": self.app.model.instance.version,
        }
        logma.info(f"Journal Document Created: {document}")
        self.app.model.add_document_app(document, did, "0", 0, widget, widgdata, doc_type, "center", "db", False)
        return self

    def add_settings_document(self):
        """"""
        did = uuid()
        widget = "config"
        widgdata = {}
        doc_type = "config"
        document = {
            "did": did,
            "name": "Settings",
            "compatibility": "pyffice",
            "type": "config",
            "syntax": "plain-text",
            "description": "internal",
            "store_location": "",
            "encoding": "utf-8",
            "meta_data": {},
            "widget": widget,
        }
        logma.info(f"Settings Document Created: {document}")
        self.app.model.add_document_app(document, did, "0", 0, widget, widgdata, doc_type, "center", "db", False)

    def create_config_file(self):
        """"""
        super().create_config_file()

    def create_database_application(self):
        """"""
        super().create_database_application()
        return self

    def on_download_progress(self, event, *args, **kwargs):
        """"""

    def on_download_finished(self, event, *args, **kwargs):
        """"""
        self.downloaded = 1

    def run_application_install(self, paths):
        """"""
        super().run_application_install(paths)
        return self

    def run_application_update(self):
        """"""
        self.downloaded = 0
        # self.download_codec = CodecDownloadThread(OpenH264Downloader)
        # self.download_codec.progress.connect(self.on_download_progress)
        # self.download_codec.finished.connect(self.on_download_finished)
        # self.download_codec.start()
        downloader = OpenH264Downloader()
        downloader.download_and_extract()
        super().run_application_update()
        self.run_model_update()

        # while self.download_codec.isRunning():
        #     time.sleep(1)
        #     if self.downloaded == 1:
        #         break
        if not downloader.test():
            self.h264_codec = False
        else:
            self.h264_codec = True

        return self

    def run_model_update(self):
        """"""
        # Deactivate the Default Nchantrs Browser Type - this isn't really an update but a part of building on top of Nchantrs
        self.app.model.deactivate("app_document_type", uuid="066fae58-be2f-7095-8000-11dd4a720555")
        return self

    def run_install_complete(self):
        """Override to select Home node after install completes"""
        super().run_install_complete()
        # Find and select the Home node after new installation
        self.select_home_node()
        return self

    def run_application(self):
        """
        Override to restore last selected node on regular (non-install) startup
        """
        super().run_application()
        # Restore last selected node or default to Home node
        self.restore_last_node()
        return self

    def restore_last_node(self):
        """
        Restore the last selected node on app startup, or default to Home node
        """
        from nchantrs.libraries import pyqt

        pyqt.QTimer.singleShot(500, self._delayed_restore_last_node)
        return self

    def _delayed_restore_last_node(self):
        """
        Delayed version of restore_last_node to ensure tree is populated
        """
        try:
            # Get the tree view from the application
            if not hasattr(self.app, "view") or not self.app.view:
                return self
            if not hasattr(self.app.view, "panes") or "left" not in self.app.view.panes:
                return self

            tree_wrapper = self.app.view.panes["left"]
            if not hasattr(tree_wrapper, "tree") or tree_wrapper.tree is None:
                return self

            tree = tree_wrapper.tree

            # Get the instance metadata for last node
            instance = self.app.model.instance
            last_node_nid = None

            if hasattr(instance, "meta_data") and instance.meta_data:
                last_node_nid = instance.meta_data.get("last_node_nid_txt")

            nodes = self.app.model.get_nodes()
            if nodes.empty:
                return self

            target_nid = None

            # First, try to restore the last selected node
            if last_node_nid:
                last_node_df = nodes[nodes["nid_txt"] == last_node_nid]
                if not last_node_df.empty:
                    target_nid = last_node_nid
                    logma.info(f"Restoring last node: {target_nid}")

            # If no last node, default to Home node (using specified NID)
            if not target_nid:
                home_nid = "067ca837-17f6-74e7-8000-f7de9b7927f1"
                home_df = nodes[nodes["nid_txt"] == home_nid]
                if not home_df.empty:
                    target_nid = home_nid
                    logma.info(f"Defaulting to Home node by NID: {target_nid}")
                else:
                    # Fallback to name-based lookup
                    home_df = nodes[nodes["name_txt"] == "Home"]
                    if not home_df.empty:
                        target_nid = home_df["nid_txt"].values[0]
                        logma.info(f"Defaulting to Home node by name: {target_nid}")
                    else:
                        # Get first root node as fallback
                        root_df = nodes[nodes["pid_txt"] == "0"]
                        if not root_df.empty:
                            target_nid = root_df["nid_txt"].values[0]
                            logma.info(f"Defaulting to first root node: {target_nid}")

            if not target_nid:
                return self

            # Find and select the node in the tree
            found = self._select_node_by_nid(tree, target_nid)
            if found:
                logma.info(f"Selected node: {target_nid}")
            else:
                logma.warning(f"Could not find node in tree: {target_nid}. Forcing model-based update.")
                # Fallback: find node data and force a center pane build even if tree item not yet found
                try:
                    target_node_df = nodes[nodes["nid_txt"] == target_nid]
                    if not target_node_df.empty:
                        node_data = target_node_df.iloc[0].to_dict()
                        # Use updateTabs if we can get a reference to the view models
                        center_pane = self.app.view.panes["center"]
                        if hasattr(center_pane, "model") and center_pane.model:
                            # We need a node object to call buildTabSet.
                            # We can try using the tree's model to get or create a node object
                            if hasattr(tree, "model") and tree.model:
                                node_obj = tree.model.get_node(target_nid)
                                if node_obj:
                                    center_pane.model.buildTabSet(node_obj, "center")
                                    logma.info(f"Forced buildTabSet for node: {target_nid}")
                except Exception as inner_e:
                    logma.warning(f"Fallback update failed: {inner_e}")

        except Exception as e:
            logma.warning(f"Could not restore last node: {e}")
        return self

    def _select_node_by_nid(self, tree, target_nid):
        """
        Helper to find and select a node by its nid
        """
        try:
            logma.info(f"_select_node_by_nid: target_nid={target_nid}, topLevelItemCount={tree.topLevelItemCount()}")
            # Try finding by iterating through tree items
            for i in range(tree.topLevelItemCount()):
                item = tree.topLevelItem(i)
                found = self._find_node_in_tree(item, target_nid)
                if found:
                    logma.info(f"Found node in tree: {target_nid}")
                    tree.setCurrentItem(found)
                    tree.scrollToItem(found)

                    # Update model's current node to match selection
                    if hasattr(tree, "model"):
                        tree.model.current_node = found

                    # Explicitly update tabs for the selected node to ensure initial catalog renders
                    if hasattr(found, "updateTabs"):
                        found.updateTabs("center")

                    # Trigger the selection change if needed
                    if hasattr(tree, "itemSelectionChanged"):
                        tree.itemSelectionChanged.emit()
                    return True

            logma.warning(f"Could not find node: {target_nid} in tree with {tree.topLevelItemCount()} items")
        except Exception as e:
            if debug:
                raise e
            logma.warning(f"Error selecting node {target_nid}: {e}")
        return False

    def _find_node_in_tree(self, item, target_nid):
        """
        Recursively find a node in the tree by nid
        """
        nid = None
        if hasattr(item, "nid"):
            nid = item.nid
        elif hasattr(item, "nid_txt"):
            nid = item.nid_txt

        if nid == target_nid:
            return item

        # Also check data(0, Qt.UserRole) if nid is not an attribute
        try:
            from nchantrs.libraries import pyqt

            role_nid = item.data(0, pyqt.Qt.UserRole)
            if role_nid == target_nid:
                return item
        except:
            pass

        for i in range(item.childCount()):
            found = self._find_node_in_tree(item.child(i), target_nid)
            if found:
                return found
        return None

    def select_home_node(self):
        """
        Find and select the Home node in the tree (for new installs)
        """
        from nchantrs.libraries import pyqt

        pyqt.QTimer.singleShot(500, self._delayed_select_home_node)
        return self

    def _delayed_select_home_node(self):
        """
        Delayed version of select_home_node
        """
        try:
            # Get the tree view from the application
            if hasattr(self.app, "view") and self.app.view:
                if hasattr(self.app.view, "panes") and "left" in self.app.view.panes:
                    tree_wrapper = self.app.view.panes["left"]
                    if hasattr(tree_wrapper, "tree") and tree_wrapper.tree is not None:
                        tree = tree_wrapper.tree
                        logma.info("Attempting to select Home node (delayed)")
                        # Try to find Home node - typically named "Home" or at root level
                        nodes = self.app.model.get_nodes()
                        if not nodes.empty:
                            # Use specified NID for Home node
                            home_nid = "067ca837-17f6-74e7-8000-f7de9b7927f1"
                            home_df = nodes[nodes["nid_txt"] == home_nid]

                            if home_df.empty:
                                # Fallback to name-based lookup
                                home_df = nodes[nodes["name_txt"] == "Home"]
                                if not home_df.empty:
                                    home_nid = home_df["nid_txt"].values[0]
                                    logma.info(f"Setting Home node by name: {home_nid}")
                                else:
                                    # Get first root node (pid = '0')
                                    root_df = nodes[nodes["pid_txt"] == "0"]
                                    if not root_df.empty:
                                        home_nid = root_df["nid_txt"].values[0]
                                        logma.info(f"Setting first root node as Home: {home_nid}")
                                    else:
                                        return self
                            else:
                                logma.info(f"Setting Home node by NID: {home_nid}")

                            # Select the node using helper method
                            self._select_node_by_nid(tree, home_nid)
        except Exception as e:
            logma.warning(f"Could not select Home node: {e}")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
