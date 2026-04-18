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
try:
    import FreeCAD, FreeCADGui

    freecad = True
except:
    freecad = False

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdOfficeFreeCAD(NchantdOfficeDocument):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        # Embed FreeCAD GUI Viewer
        self.init_freecad_viewer()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def init_freecad_viewer(self):
        """Initialize FreeCAD's embedded 3D viewer."""
        try:
            FreeCADGui.showMainWindow()  # Make sure FreeCAD GUI is initialized
            FreeCADGui.setupWithoutGUI()  # Setup FreeCAD without its standalone interface
        except RuntimeError:
            pass  # GUI has already been initialized

        # Embed FreeCAD viewer into our PySide6 app
        self.freecad_view = FreeCADGui.Control.getMainWindow()
        self.freecad_view.setParent(self.viewer)
        self.freecad_view.setGeometry(self.viewer.geometry())
        self.freecad_view.setWindowFlags(pyqt.Qt.Widget)
        self.freecad_view.show()

    def load_file(self):
        """Open a file dialog to load a 3D file into FreeCAD."""
        file_path = join(here, "_data_", "cube.FCStd")
        if file_path:
            # Load the file in FreeCAD's active document
            doc = FreeCAD.newDocument("ImportedModel")
            FreeCADGui.activeDocument().activeView().viewAxometric()  # Set axometric view
            doc.addObject("Part::Feature", "ImportedFile")
            doc.Import(file_path)
            FreeCADGui.ActiveDocument.ActiveView.fitAll()  # Fit the view to loaded geometry


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
