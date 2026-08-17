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
from __future__ import annotations
from os.path import abspath, dirname, exists, join, getsize, getmtime, getatime, getctime, isfile
import datetime as dt
from pathlib import Path
from typing import Any, Self

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
    """T-NEW-144a: shows internal-document data when the bound tab
    has no on-disk file_path. Mirrors the T-NEW-038 refresh
    pattern: every getter re-runs against the bound tab +
    file_path, so a tab switch updates the pane."""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdFileDetailsPane").override(cfg))
        self.file_path = None
        # T-NEW-144a: bound-tab reference for internal-doc
        # fallback. ``set_tab`` / ``bind_to_tab`` populates this;
        # the getters consult it when ``file_path`` is empty.
        self.tab = None
        self.file_name_entry = None
        self.file_path_entry = None
        self.file_size_entry = None
        self.creon_entry = None
        self.accon_entry = None
        self.modon_entry = None
        self.hash_entry = None

    def bind_to_tab(self, tab) -> Self:
        """T-NEW-144a: bind the pane to the active tab so internal-
document metadata (no file_path) renders correctly.

        Stores ``tab`` on ``self.tab`` and refreshes the detail
widgets. The bound tab dict (or SimpleNamespace) must
expose ``name``, ``location``, optional ``file_path``,
optional ``content`` (bytes / str), optional ``creon`` /
``accon`` / ``modon`` ISO timestamps. Missing attributes
fall back to defaults rather than raising.

        If the tab carries a non-empty ``file_path``, the pane
adopts it so the on-disk getters continue to work for
external docs (backward compat with T-NEW-038).
        """
        self.tab = tab
        tab_file_path = getattr(tab, "file_path", None)
        if tab_file_path:
            self.file_path = Path(tab_file_path)
        self.refresh()
        return self

    def initModel(self, cfg=None) -> Self:
        """"""
        logma.info(f"[files] initModel cfg_provided={cfg is not None}")
        super().initModel(cfg)
        self.set_file_path(self.config.get("file_path"))
        return self

    def initView(self, cfg=None) -> Self:
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
            cfg = {"label": label, "layout": "vertical", "read_only": True, "value": value, "wrap": True}
            widget = NchantdLabeledEntry(self, cfg).initWidget()
            setattr(self, entry_name, widget)
            self.layout.addWidget(widget)
        logma.debug("[files] initView: 7 entries built")

        return self

    def initWidget(self) -> Self:
        """"""
        logma.info("[files] initWidget")
        self.initModel()
        self.initView()
        return self

    def refresh(self) -> Self:
        """Re-read file details from disk and update the widget fields.

        T-NEW-038: ``FileDetailsPane is not updated on initial file
        open need to implement a refresh`` -- the file details
        widgets are populated once during initView with the initial
        values, but the getters (``get_file_size``, ``get_hash``,
        etc.) only update the widget when the file path is set
        AFTER the widgets are built. ``refresh()`` re-runs all
        getters so the pane reflects the current file path at any
        time without needing a rebuild.
        """
        try:
            self.get_name()
            self.get_file_path()
            self.get_file_size()
            self.get_created_date()
            self.get_access_date()
            self.get_modified_date()
            self.get_hash()
        except Exception as e:
            logma.warning(f"[files] refresh failed: {e}")
        return self

    def get_access_date(self, path=None) -> str:
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
            return date
        self.accon_entry.setText(str(date))
        return date

    def get_created_date(self, path=None) -> str:
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
            return date
        self.creon_entry.setText(str(date))
        return date

    def get_file_path(self) -> Path:
        """T-NEW-144a: show '(internal storage)' when no
        file_path is set (internal docs). The widget text is
        updated via the file_path_entry attribute. For external
        docs we leave the widget alone -- set_file_path already
        populates it with the full path, and overwriting with
        the parent dir would regress T-NEW-038.
        """
        if self.file_path is None or not str(self.file_path):
            placeholder = "(internal storage)"
            if getattr(self, "file_path_entry", None) is not None:
                self.file_path_entry.setText(placeholder)
            return Path(placeholder)
        # External doc: preserve the pre-T-NEW-144a behaviour
        # (return parent dir, leave widget text alone so the
        # value set by set_file_path / refresh wins).
        return self.file_path.parent

    def get_file_size(self, path=None) -> str | int:
        """T-NEW-144a: fall back to self.tab.content length
        when no file_path is set. Internal docs are stored in
        the doc_media / app_media_content table as bytes (or
        str); we report the byte length so the user can see
        the actual stored size."""
        path = path or self.file_path or Path("")
        logma.debug(f"[files] get_file_size: path={path!r}")
        if not path or not path.name or not exists(path):
            tab_content = (
                getattr(self.tab, "content", None) if self.tab is not None else None
            )
            if tab_content is None:
                size = "0"
            elif isinstance(tab_content, (bytes, bytearray)):
                size = len(tab_content)
            elif isinstance(tab_content, str):
                size = len(tab_content.encode("utf-8"))
            else:
                size = len(str(tab_content))
        else:
            try:
                size = getsize(path)
            except Exception as e:
                logma.error(f"[files] get_file_size failed: {path!r} err={e}", exc_info=True)
                size = "0"
        if self.file_size_entry is None:
            return size
        self.file_size_entry.setText(str(size))
        return size

    def get_hash(self, path=None) -> str:
        """"""
        hash_ = ""
        path = path or self.file_path
        logma.debug(f"[files] get_hash: path={path!r}")
        if path is None:
            return hash_
        if not isfile(path):
            return hash_
        try:
            hash_ = get_file_hash(path)
            logma.debug(f"[files] get_hash: hash_len={len(hash_) if hash_ else 0}")
            if self.hash_entry is None:
                return hash_
            self.hash_entry.setText(hash_)
        except Exception as e:
            logma.error(f"[files] get_hash failed: {path!r} err={e}", exc_info=True)
            if self.hash_entry is None:
                return hash_
            self.hash_entry.setText(hash_)
        return hash_

    def get_modified_date(self, path=None) -> str:
        """T-NEW-144a: fall back to self.tab.modon (ISO string)
        when no file_path is set. Internal tabs store the
        modification timestamp in the doc_media row."""
        path = path or self.file_path or Path("")
        logma.debug(f"[files] get_modified_date: path={path!r}")
        if not path or not path.name or not exists(path):
            tab_modon = (
                getattr(self.tab, "modon", None) if self.tab is not None else None
            )
            date = str(tab_modon) if tab_modon else "0"
        else:
            try:
                ts = getmtime(path)
                date = dt.datetime.fromtimestamp(ts).isoformat()
            except Exception as e:
                logma.error(f"[files] get_modified_date failed: {path!r} err={e}", exc_info=True)
                date = "0"
        if self.modon_entry is None:
            return date
        self.modon_entry.setText(str(date))
        return date

    def get_name(self, path=None) -> str:
        """Read the file name (basename) and update the file-name widget.

        T-NEW-038: prior to this, ``get_name`` only returned the
        basename without updating ``self.file_name_entry``. Now it
        mirrors the pattern used by the other getters (``get_file_size``
        etc.) and writes the name into the widget so a ``refresh()``
        after ``initView`` actually refreshes every field.

        T-NEW-144a: when ``self.file_path`` is empty (internal doc),
        fall back to ``self.tab.name`` (or "(unnamed)" when missing)
        so internal tabs render a meaningful file_name field.
        """
        path = path or self.file_path or Path("")
        name = path.name if path.name else (
            getattr(self.tab, "name", None) if self.tab is not None else None
        ) or "(unnamed)"
        if self.file_name_entry is not None:
            self.file_name_entry.setText(str(name))
        return name

    def set_file_name(self, name) -> Self:
        """"""
        logma.debug(f"[files] set_file_name: name={name!r}")
        if self.file_name_entry is None:
            return self
        self.file_name_entry.setText(name)
        return self

    def set_file_path(self, path) -> Self:
        """Set the file path and refresh all detail fields.

        T-NEW-038: ``FileDetailsPane is not updated on initial file
        open`` -- calling ``set_file_path`` previously only updated
        the path-entry widget. The size / hash / date widgets
        stayed at their initView-time values. Now ``set_file_path``
        also calls ``refresh()`` so every getter re-runs against
        the new path. Defensive: when the widgets haven't been
        built yet (``initView`` not called), ``refresh()`` is a
        no-op because the getters bail out on missing widgets.
        """
        logma.debug(f"[files] set_file_path: path={path!r}")
        path = path or ""
        self.file_path = Path(path)
        if self.file_path_entry is None:
            return self
        self.file_path_entry.setText(self.file_path)
        self.refresh()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
