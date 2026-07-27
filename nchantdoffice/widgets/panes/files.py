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
from os.path import abspath, dirname, exists, join, getsize, getmtime, getatime, getctime
import datetime as dt

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
        logma.info(f"[files] NchantdFileDetailsPane.__init__ parent={type(parent).__name__ if parent else None}")
        try:
            super().__init__(parent, cfg)
            self.config.override(kahndor.Instruct(pxcfg).select("NchantdFileDetailsPane").override(cfg))
        except Exception as e:
            logma.error(f"[files] NchantdFileDetailsPane.__init__ failed: {e}", exc_info=True)
            raise

    def initModel(self, cfg=None):
        """"""
        logma.info(f"[files] initModel cfg_provided={cfg is not None}")
        try:
            super().initModel(cfg)
        except Exception as e:
            logma.error(f"[files] initModel failed: {e}", exc_info=True)
            raise
        return self

    def initView(self, cfg=None):
        """"""
        logma.info("[files] initView: building File Details pane with 7 labelled entries")
        try:
            if cfg is None:
                cfg = {}
            cfg["label"] = "File Details"
            cfg["layout"] = "vertical"
            super().initView(cfg)
            for entry_name, label in [
                ("file_name_entry", "File Name: "),
                ("file_path_entry", "File Path: "),
                ("file_size_entry", "File Size: "),
                ("creon_entry", "Date Created: "),
                ("accon_entry", "Date Accessed: "),
                ("modon_entry", "Date Modified: "),
                ("hash_entry", "File Hash: "),
            ]:
                cfg = {"label": label, "layout": "horizontal", "read_only": True}
                widget = NchantdLabeledEntry(self, cfg).initWidget()
                setattr(self, entry_name, widget)
                self.layout.addWidget(widget)
            logma.debug("[files] initView: 7 entries built")
        except Exception as e:
            logma.error(f"[files] initView failed: {e}", exc_info=True)
            raise
        return self

    def initWidget(self):
        """"""
        logma.info("[files] initWidget")
        try:
            self.initModel()
            self.initView()
        except Exception as e:
            logma.error(f"[files] initWidget failed: {e}", exc_info=True)
            raise
        return self

    def get_access_date(self, path):
        """"""
        logma.debug(f"[files] get_access_date: path={path!r}")
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
        self.accon_entry.setText(str(date))
        return self

    def get_created_date(self, path):
        """"""
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
        self.creon_entry.setText(str(date))
        return self

    def get_file_size(self, path):
        """"""
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
        self.file_size_entry.setText(str(size))
        return self

    def get_hash(self, path):
        """"""
        logma.debug(f"[files] get_hash: path={path!r}")
        try:
            hash_ = get_file_hash(path)
            logma.debug(f"[files] get_hash: hash_len={len(hash_) if hash_ else 0}")
            self.hash_entry.setText(hash_)
        except Exception as e:
            logma.error(f"[files] get_hash failed: {path!r} err={e}", exc_info=True)
            self.hash_entry.setText("")
        return self

    def get_modified_date(self, path):
        """"""
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
        self.modon_entry.setText(str(date))
        return self

    def set_file_name(self, name):
        """"""
        logma.debug(f"[files] set_file_name: name={name!r}")
        self.file_name_entry.setText(name)
        return self

    def set_file_path(self, path):
        """"""
        logma.debug(f"[files] set_file_path: path={path!r}")
        self.file_path_entry.setText(path)
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
