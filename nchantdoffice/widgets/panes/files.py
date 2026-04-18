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
from os.path import abspath, dirname, exists, join, getsize, getmtime, getatime, getctime
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "files.yaml")


class NchantdFileDetailsPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("Nchantd"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["label"] = "File Details"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        cfg = {"label": "File Name: ", "layout": "horizontal", "read_only": True}
        self.file_name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.file_name_entry)
        cfg = {"label": "File Path: ", "layout": "horizontal", "read_only": True}
        self.file_path_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.file_path_entry)
        cfg = {"label": "File Size: ", "layout": "horizontal", "read_only": True}
        self.file_size_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.file_size_entry)
        cfg = {"label": "Date Created: ", "layout": "horizontal", "read_only": True}
        self.creon_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.creon_entry)
        cfg = {"label": "Date Accessed: ", "layout": "horizontal", "read_only": True}
        self.accon_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.accon_entry)
        cfg = {"label": "Date Modified: ", "layout": "horizontal", "read_only": True}
        self.modon_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.modon_entry)
        cfg = {"label": "File Hash: ", "layout": "horizontal", "read_only": True}
        self.hash_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.hash_entry)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_access_date(self, path):
        """"""
        if not exists(path):
            date = "0"
        else:
            date = getatime(path)
        self.accon_entry.setText(date)
        return self

    def get_created_date(self, path):
        """"""
        if not exists(path):
            date = "0"
        else:
            date = getctime(path)
        self.creon_entry.setText(date)
        return self

    def get_file_size(self, path):
        """"""
        if not exists(path):
            size = "0"
        else:
            size = getsize(path)
        self.file_size_entry.setText(size)
        return self

    def get_hash(self, path):
        """"""
        hash_ = get_file_hash(path)
        self.hash_entry.setText(hash_)
        return self

    def get_modified_date(self, path):
        """"""
        if not exists(path):
            date = "0"
        else:
            date = getmtime(path)
        self.modon_entry.setText(date)
        return self

    def set_file_name(self, name):
        """"""
        self.file_name_entry.setText(name)
        return self

    def set_file_path(self, path):
        """"""
        self.file_path_entry.setText(path)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
