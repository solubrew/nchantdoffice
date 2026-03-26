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
from condor import condor
from ogma.logma import Logma
from nchantrs.wizards.apps import NchantdApplicationStartupWizard

from nchantdoffice.updates.db import NchantdOfficeDBUpdate

from subtrix.utilities import uuid
from nchantrs.widgets.browsers.downloads import CodecDownloadThread
from nchantrs.widgets.browsers.codecs.h264 import OpenH264Downloader

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
# logma.off()
# ====================================================================================================================||
pxcfg = join(here, "_data_", "wizards.yaml")
pxcfg = {}


class NchantdOfficeApplicationStartupWizard(NchantdApplicationStartupWizard):
    """Startup Wizard for Nchantd Office Application"""

    def __init__(self, app=None, cfg=None):
        """ """
        super().__init__(app, cfg)
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeApplicationStartupWizard")).override(cfg)
        cfg = {}
        self.db_update = NchantdOfficeDBUpdate(self, cfg)
        self.download_codec = None
        self.h264_codec = None

    def initView(self, args=None):
        """"""
        super().initView(args)
        self.add_journal_document()
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

    def create_database_application(self):
        """"""
        super().create_database_application()
        return self

    def on_download_progress(self, event, *args, **kwargs):
        """"""

    def on_download_finished(self, event, *args, **kwargs):
        """"""
        self.downloaded = 1

    def run_application(self):
        """"""
        super().run_application()
        return self

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
        """"""
        Override to select Home node after install completes
        """
        super().run_install_complete()
        # Find and select the Home node after new installation
        self.select_home_node()
        return self

    def run_application(self):
        """"""
        Override to restore last selected node on regular (non-install) startup
        """
        super().run_application()
        # Restore last selected node or default to Home node
        self.restore_last_node()
        return self

    def restore_last_node(self):
        """"""
        Restore the last selected node on app startup, or default to Home node
        """
        try:
            # Get the tree view from the application
            if not hasattr(self.app, 'view') or not self.app.view:
                return self
            if not hasattr(self.app.view, 'panes') or 'left' not in self.app.view.panes:
                return self
            
            tree = self.app.view.panes['left']
            if not hasattr(tree, 'parent') or not hasattr(tree.parent, 'model'):
                return self
            
            # Get the instance metadata for last node
            instance = self.app.model.instance
            last_node_nid = None
            
            if hasattr(instance, 'meta_data') and instance.meta_data:
                last_node_nid = instance.meta_data.get('last_node_nid_txt')
            
            nodes = self.app.model.get_nodes()
            if nodes.empty:
                return self
            
            target_nid = None
            
            # First, try to restore the last selected node
            if last_node_nid:
                last_node_df = nodes[nodes['nid_txt'] == last_node_nid]
                if not last_node_df.empty:
                    target_nid = last_node_nid
                    logma.info(f"Restoring last node: {target_nid}")
            
            # If no last node, default to Home node
            if not target_nid:
                home_df = nodes[nodes['name_txt'] == 'Home']
                if not home_df.empty:
                    target_nid = home_df['nid_txt'].values[0]
                else:
                    # Get first root node as fallback
                    root_df = nodes[nodes['pid_txt'] == '0']
                    if not root_df.empty:
                        target_nid = root_df['nid_txt'].values[0]
            
            if not target_nid:
                return self
            
            # Find and select the node in the tree
            self._select_node_by_nid(tree, target_nid)
            logma.info(f"Selected node: {target_nid}")
            
        except Exception as e:
            logma.warning(f"Could not restore last node: {e}")
        return self

    def _select_node_by_nid(self, tree, target_nid):
        """"""
        Helper to find and select a node by its nid
        """
        try:
            # Try to find the node in the tree widget
            if hasattr(tree, 'findItem'):
                node_item = tree.findItem(target_nid, nid_column=0)
                if node_item:
                    tree.set_current_node(node_item)
                    return True
            
            # Try finding via the model
            if hasattr(tree, 'parent') and hasattr(tree.parent, 'model'):
                model = tree.parent.model
                if hasattr(model, 'getNodeData'):
                    # Walk through nodes to find the target
                    nodes = self.app.model.get_nodes()
                    node_df = nodes[nodes['nid_txt'] == target_nid]
                    if not node_df.empty:
                        node_data = node_df.to_dict('records')[0]
                        # Create a node item if needed
                        if hasattr(tree, 'node_widget'):
                            node_name = node_data.get('name_txt', 'Unknown')
                            node_item = tree.node_widget(tree.parent, node_name, target_nid, node_data)
                            if hasattr(node_item, 'initWidget'):
                                node_item.initWidget()
                            tree.set_current_node(node_item)
                            return True
                        elif hasattr(tree, 'set_current_node'):
                            # Try to set current node directly if it's already in the tree
                            for i in range(tree.parent.topLevelItemCount()):
                                item = tree.parent.topLevelItem(i)
                                if self._find_node_in_tree(item, target_nid):
                                    tree.set_current_node(item)
                                    return True
            
            logma.warning(f"Could not find node: {target_nid}")
        except Exception as e:
            logma.warning(f"Error selecting node {target_nid}: {e}")
        return False

    def _find_node_in_tree(self, item, target_nid):
        """"""
        Recursively find a node in the tree by nid
        """
        if hasattr(item, 'nid') and item.nid == target_nid:
            return True
        for i in range(item.childCount()):
            if self._find_node_in_tree(item.child(i), target_nid):
                return True
        return False

    def select_home_node(self):
        """"""
        Find and select the Home node in the tree (for new installs)
        """
        try:
            # Get the tree view from the application
            if hasattr(self.app, 'view') and self.app.view:
                if hasattr(self.app.view, 'panes') and 'left' in self.app.view.panes:
                    tree = self.app.view.panes['left']
                    if hasattr(tree, 'model'):
                        # Try to find Home node - typically named "Home" or at root level
                        nodes = self.app.model.get_nodes()
                        if not nodes.empty:
                            # Find Home node by name or get first root node
                            home_df = nodes[nodes['name_txt'] == 'Home']
                            if not home_df.empty:
                                home_nid = home_df['nid_txt'].values[0]
                            else:
                                # Get first root node (pid = '0')
                                root_df = nodes[nodes['pid_txt'] == '0']
                                if not root_df.empty:
                                    home_nid = root_df['nid_txt'].values[0]
                                else:
                                    return self
                            # Select the node using helper method
                            self._select_node_by_nid(tree, home_nid)
                            logma.info(f"Selected Home node: {home_nid}")
        except Exception as e:
            logma.warning(f"Could not select Home node: {e}")
        return self

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
