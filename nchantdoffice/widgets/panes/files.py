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

# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, exists, join, getsize, getmtime, getatime, getctime, isfile
import datetime as dt
from pathlib import Path

# ======================================3rd Party Library Modules======================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from pycurity.pyhash import get_file_hash

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
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdFileDetailsPane").override(cfg))
        self.file_path = None
        self.file_name_entry = None
        self.file_path_entry = None
        self.file_size_entry = None
        self.creon_entry = None
        self.accon_entry = None
        self.modon_entry = None
        self.hash_entry = None

    def initModel(self, cfg=None):
        """"""
        logma.info(f"[files] initModel cfg_provided={cfg is not None}")
        super().initModel(cfg)
        self.set_file_path(self.config.get("file_path"))
        return self

    def initView(self, cfg=None):
        """"""
        logma.info("[files] initView: building File Details pane with 7 labelled entries")
        cfg = cfg or {}
        cfg["label"] = "File Details"
        cfg["layout"] = "vertical"
        super().initView(cfg)
        for entry_name, label, value in [
            ("file_name_entry", "File Name: ", self.get_name()),
            ("file_path_entry", "File Path: ", self.get_file_path()),
            ("file_size_entry", "File Size: ", self.get_file_size()),
            ("creon_entry", "Date Created: ", self.get_created_date()),
            ("accon_entry", "Date Accessed: ", self.get_access_date()),
            ("modon_entry", "Date Modified: ", self.get_modified_date()),
            ("hash_entry", "File Hash: ", self.get_hash(self.file_path)),
        ]:
            cfg = {"label": label, "layout": "horizontal", "read_only": True}
            widget = NchantdLabeledEntry(self, cfg).initWidget()
            setattr(self, entry_name, widget)
            self.layout.addWidget(widget)
        logma.debug("[files] initView: 7 entries built")

        return self

    def initWidget(self):
        """"""
        logma.info("[files] initWidget")
        self.initModel()
        self.initView()
        return self

    def get_access_date(self, path=None):
        """"""
        logma.debug(f"[files] get_access_date: path={path!r}")
        path = path or self.file_path or Path("")
        if not exists(path):
            logma.warning(f"[files] get_access_date: path missing, using '0': {path!r}")
            date = "0"
        else:
            try:
                ts = getatime(path)
                date = dt.datetime.fromtimestamp(ts).isoformat()
            except Exception as e:
                logma.error(f"[files] get_access_date failed: {path!r} err={e}", exc_info=True)
                date = "0"
        if self.accon_entry is None:
            return self
        self.accon_entry.setText(str(date))
        return self

    def get_created_date(self, path=None):
        """"""
        path = path or self.file_path or Path("")

        logma.debug(f"[files] get_created_date: path={path!r}")
        if not exists(path):
            logma.warning(f"[files] get_created_date: path missing, using '0': {path!r}")
            date = "0"
        else:
            try:
                ts = getctime(path)
                date = dt.datetime.fromtimestamp(ts).isoformat()
            except Exception as e:
                logma.error(f"[files] get_created_date failed: {path!r} err={e}", exc_info=True)
                date = "0"
        if self.creon_entry is None:
            return self
        self.creon_entry.setText(str(date))
        return self

    def get_file_path(self):
        """"""
        return self.file_path

    def get_file_size(self, path=None):
        """"""
        path = path or self.file_path or Path("")
        logma.debug(f"[files] get_file_size: path={path!r}")
        if not exists(path):
            logma.warning(f"[files] get_file_size: path missing, using '0': {path!r}")
            size = "0"
        else:
            try:
                size = getsize(path)
            except Exception as e:
                logma.error(f"[files] get_file_size failed: {path!r} err={e}", exc_info=True)
                size = "0"
        if self.file_size_entry is None:
            return self
        self.file_size_entry.setText(str(size))
        return self

    def get_hash(self, path=None):
        """"""
        path = path or self.file_path
        logma.debug(f"[files] get_hash: path={path!r}")
        if path is None:
            return self
        if not isfile(path):
            return self
        try:
            hash_ = get_file_hash(path)
            logma.debug(f"[files] get_hash: hash_len={len(hash_) if hash_ else 0}")
            if self.hash_entry is None:
                return self
            self.hash_entry.setText(hash_)
        except Exception as e:
            logma.error(f"[files] get_hash failed: {path!r} err={e}", exc_info=True)
            if self.hash_entry is None:
                return self
            self.hash_entry.setText("")
        return self

    def get_modified_date(self, path=None):
        """"""
        path = path or self.file_path or Path("")
        logma.debug(f"[files] get_modified_date: path={path!r}")
        if not exists(path):
            logma.warning(f"[files] get_modified_date: path missing, using '0': {path!r}")
            date = "0"
        else:
            try:
                ts = getmtime(path)
                date = dt.datetime.fromtimestamp(ts).isoformat()
            except Exception as e:
                logma.error(f"[files] get_modified_date failed: {path!r} err={e}", exc_info=True)
                date = "0"
        if self.modon_entry is None:
            return self
        self.modon_entry.setText(str(date))
        return self

    def get_name(self, path=None):
        """"""
        path = path or self.file_path or Path("")
        return path.name

    def set_file_name(self, name):
        """"""
        logma.debug(f"[files] set_file_name: name={name!r}")
        if self.file_name_entry is None:
            return self
        self.file_name_entry.setText(name)
        return self

    def set_file_path(self, path):
        """"""
        logma.debug(f"[files] set_file_path: path={path!r}")
        path = path or ""
        self.file_path = Path(path)
        if self.file_path_entry is None:
            return self
        self.file_path_entry.setText(path)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
