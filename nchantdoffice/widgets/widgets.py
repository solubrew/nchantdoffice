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
from functools import lru_cache

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantrs.widgets.tabsets import NchantdTabSet
from nchantdoffice.models import NchantdOfficeTabSetModel
from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox

# Lazy imports for heavy widgets - loaded on demand
# Heavy widgets like charts, media, workbooks will be lazy loaded
_note_cache = None

def _get_note_widget():
    """Lazy load note widget to improve startup performance"""
    global _note_cache
    if _note_cache is None:
        from nchantdoffice.widgets.documents.media.notes import NchantdOfficeNote
        _note_cache = NchantdOfficeNote
    return _note_cache

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "widgets.yaml")
pxcfg = {}


class NchantdOfficeTabSet(NchantdTabSet):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeTabSet")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.model = NchantdOfficeTabSetModel(self, self.config)

    def initModel(self, create_objects=True):
        """"""
        super().initModel(create_objects)
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        self.initModel(cfg.get("create_objects", True))
        self.initView()
        return self

    def launch_note(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        # Use lazy loaded note widget for faster startup
        NoteWidget = _get_note_widget()
        note = NoteWidget(self.app.main, cfg).initWidget()
        self.app.view.panes["center"].model.current_tab.append_note(note)
        return self

    @lru_cache(maxsize=16)
    def get_widget_config(self, widget_type):
        """Cache widget configuration lookups for performance"""
        return self.config.dikt.get(f"widgets.{widget_type}", {})

    def create_toolbox(self, parent=None, cfg=None):
        """"""
        toolbox = NchantdOfficeApplicationToolBox(parent, cfg)
        return toolbox

    def setTabText(self, position, text, store=True):
        """"""
        super().setTabText(position, text)
        if store:
            cfg = {"name_txt": text}
            self.app.model.update_tab(self.app.model.get_current_tab(), cfg)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
