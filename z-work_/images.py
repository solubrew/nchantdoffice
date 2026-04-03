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
from pyffice.document import PyfficeImage

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "../_data_", "images.yaml")


class NchantdOfficeImage(NchantdOfficeDocument, PyfficeImage):
    """Image document - implements PyfficeImage"""

    PYTYPE = "image"

    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for image documents"""
        return [
            {"id": "crop", "icon": "crop", "label": "Crop", "method": "crop_image"},
            {"id": "rotate", "icon": "rotate", "label": "Rotate", "method": "rotate_image"},
            {"id": "filters", "icon": "filter", "label": "Filters", "method": "apply_filters"},
            {"id": "resize", "icon": "resize", "label": "Resize", "method": "resize_image"},
            {"id": "enhance", "icon": "wand", "label": "Enhance", "method": "auto_enhance"},
        ]

    def __init__(self, name="Nchantd Image", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeImage"))
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

    def crop_image(self):
        """Crop image"""
        logma.info("Cropping image...")
        return self

    def rotate_image(self):
        """Rotate image"""
        logma.info("Rotating image...")
        return self

    def apply_filters(self):
        """Apply filters"""
        logma.info("Applying filters...")
        return self

    def resize_image(self):
        """Resize image"""
        logma.info("Resizing image...")
        return self

    def auto_enhance(self):
        """Auto enhance"""
        logma.info("Auto enhancing...")
        return self


# ====================================================================================================================||
