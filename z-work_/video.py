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
from nchantrs.libraries import pyqt

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from pyffice.document import PyfficeVideo

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "../_data_", "video.yaml")


class NchantdOfficeVideo(NchantdOfficeDocument, PyfficeVideo):
    """Video document - implements PyfficeVideo"""

    PYTYPE = "video"

    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for video documents"""
        return [
            {"id": "play", "icon": "play", "label": "Play/Pause", "method": "toggle_play"},
            {"id": "trim", "icon": "cut", "label": "Trim", "method": "trim_video"},
            {"id": "effects", "icon": "magic", "label": "Effects", "method": "add_effects"},
            {"id": "export", "icon": "download", "label": "Export", "method": "export_video"},
        ]

    def __init__(self, name="Nchantd Video", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeVideo"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self, cfg=None):
        """"""
        self.initModel(cfg)
        self.initView(cfg)
        return self

    def toggle_play(self):
        """Toggle play/pause"""
        logma.info("Toggling play/pause...")
        return self

    def trim_video(self):
        """Trim video"""
        logma.info("Trimming video...")
        return self

    def add_effects(self):
        """Add effects"""
        logma.info("Adding effects...")
        return self

    def export_video(self):
        """Export video"""
        logma.info("Exporting video...")
        return self


# ====================================================================================================================||
