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

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.config.storage import NchantdStorageSettings
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.button_groups import NchantdSaveButtons
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from nchantrs.widgets.groups import NchantdVScrollGroupBox, NchantdHGroupBox

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "storage.yaml")


class NchantdOfficeStorageSettings(NchantdStorageSettings):
    """"""

    def __init__(self, parent, cfg=None):
        """"""
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeStorageSettings").override(cfg))
        self.storage = self.config.dikt.get("default_storage", None)
        self.local_paths = []
        self.local_button_bar = None
        self.cloud_button_bar = None

    def initModel(self):
        """"""
        super().initModel()
        # self.local_paths = self.app.model.get_storage_paths()
        return self

    def initView(self):
        """
        implement storage retention policy for
                downloads
                imports

        :return:
        """
        super().initView()
        cfg = {
            "actions": {
                0: "new_local_storage",
                1: "move_files_at_path",
                2: "move_files_to_path",
                3: "remove_storage_path",
            }
        }
        # buttons = {
        # 			'New Local Path': {'icon': '', 'Tip': ''},
        # 			'Move Files at Path': {'icon': '', 'Tip': ''},
        # 			'Move Files to Path': {'icon': '', 'Tip': ''},
        # 			'Remove Path': {'icon': '', 'Tip': ''}
        #            }
        self.local_button_bar = NchantdButtonBar(self, cfg).initWidget()
        self.layout.addWidget(self.local_button_bar)
        local_group = NchantdVScrollGroupBox()
        local_group.setTitle("Local Storage")
        local_paths = self.config.dikt["default_storage"]["local"]["paths"]
        local_paths += self.local_paths
        for path in local_paths:

            local_group_path = NchantdHGroupBox(self, self.config).initWidget()
            local_group_path.setTitle(list(path.keys())[0])

            cfg = {"text": "size of store"}
            local_group_path.addWidget(NchantdLabel(self, cfg).initWidget())

            cfg = {"text": "List of Files"}
            local_group_path.addWidget(NchantdLabel(self, cfg).initWidget())

            cfg = {}
            local_group_path.addWidget(NchantdSaveButtons(self, cfg).initWidget(None))

            local_group.addWidget(local_group_path)
        self.layout.addLayout(local_group.layout)
        buttons = {
            "Add Service": {"icon": "", "Tip": ""},
            "Sync Service Locally": {"icon": "", "Tip": ""},
            "Backup Service Locally": {"icon": "", "Tip": ""},
            "Remove Service": {"icon": "", "Tip": ""},
        }
        cfg = {
            "actions": {
                0: "add_cloud_storage",
                1: "sync_service_locally",
                2: "backup_service_locally",
                3: "remove_service_connection",
            }
        }
        self.cloud_button_bar = NchantdButtonBar(self, cfg).initWidget(buttons)
        self.layout.addWidget(self.cloud_button_bar)
        cloud_group = NchantdVScrollGroupBox()
        cloud_group.setTitle("Cloud Storage")
        for service, details in self.config.dikt["default_storage"]["cloud"].items():
            cloud_group_path = NchantdHGroupBox(self, self.config).initWidget()
            cloud_group_path.setTitle(details["name"])
            cfg = {"name": service}
            cloud_group_path.addWidget(NchantdSaveButtons(self, cfg).initWidget(None))
            cloud_group.addWidget(cloud_group_path)
        self.layout.addLayout(cloud_group.layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
