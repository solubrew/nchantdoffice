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
import sys

# ======================================3rd Party Library Modules=====================================================||
import pygame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.wizards.pages import NchantdWizardPage
from nchantrs.widgets.tables import NchantdTable
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdNewNchantdArenaApplicationPage(NchantdWizardPage):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdNewAccountNchantdActionPage")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdNewNchantdArenaApplicationPage, self).__init__(self.parent, self.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdMiniArena(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdMiniArena")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdMiniArena, self).__init__(self.parent, self.config)
        pygame.init()
        self.surface = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        self.set_surface_size()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def paintEvent(self, event):
        """"""
        painter = pyqt.QPainter()
        painter.begin(self)
        buffer = self.surface.get_buffer().raw
        width = self.surface.get_width()
        height = self.surface.get_height()
        image = pyqt.QImage(buffer, width, height, pyqt.QImage.Format_RGB32)
        painter.drawImage(0, 0, image)
        painter.end()

    def set_surface_size(self):
        """"""
        self.surface = pygame.Surface(self.size())
        return self

    def update_game(self):
        game(self.surface)
        self.update()


class NchantdLeaderBoard(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdLeaderBoard")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdLeaderBoard, self).__init__(self.parent, self.config)
        self.title = None
        self.table = None

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {"text": "Nchantd Leader Board"}
        self.title = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.title)

        cfg = {}
        self.table = NchantdTable(self, cfg).initWidget()
        labels = ["User", "Score", "Last Game Played"]
        self.table.setHorizontalHeaderLabels(labels)
        self.layout.addWidget(self.table)

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
