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
from os.path import abspath, dirname, join, exists
from os import listdir
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.groups import NchantdVScrollGroupBox, NchantdHScrollGroupBox
from nchantrs.widgets.media.images import NchantdImage
from numpy import PyUFunc_f_f
from kahndor.logma import Logma

from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from pyffice.presentation.presentation import NchantdPresentation

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "shows.yaml")


class NchantdOfficeFilmStrip(NchantdOfficeDocument):
    """
            An Nchantd Film Strip widget will provide a scrollable line of images in either a
            horizontal or vertical layout.

    :param parent: The parent widget.
    :param cfg: The configuration for the film strip.
    """

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("NchantdFilmStrip")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super().__init__(self.parent, self.config)
        self.images = {}

    def load_folder(self, path):
        """"""
        images = [x for x in listdir(path) if self.is_image(x)]
        self.images = {i: x for i, x in enumerate(images)}

    def load_list(self, list_of_paths):
        """"""
        images = [x for x in list_of_paths if self.is_image(x)]
        self.images = {i: x for i, x in enumerate(images)}

    def is_image(self, path):
        """"""
        if exists(path):
            if path.endswith([".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]):
                return True
        return False

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        if self.config.dikt["layout"] == "vertical":
            self.film_strip_group = NchantdVScrollGroupBox(self, self.config)
        else:
            self.film_strip_group = NchantdHScrollGroupBox(self, self.config)
        self.film_strip_group.setTitle("Film Strip")
        for seq, image in self.images.items():
            cfg = {"path": image["path"]}
            image_widget = NchantdImage(self, cfg).initWidget()
            self.film_strip_group.addWidget(image_widget)
        self.layout.addLayout(self.film_strip_group.layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficePresentation(NchantdOfficeDocument):
    """
    A Slide show will provide a scrollable line of interactive Widgets that can be used to tell a story

    Args:
        parent (QWidget): The parent widget. Defaults to None.
        cfg (dict): Configuration options for the slideshow widget. Defaults to None.

    Attributes:
        parent (QWidget): The parent widget of the slideshow widget.
        config (dict): Configuration options for the slideshow widget.
        slideShowView (QGraphicsView): The QGraphicsView used to display the slideshow.
        slideShowScene (QGraphicsScene): The QGraphicsScene used for the slideshow.

    """

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("NchantdSlideShow")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self.parent, self.config)
        self.config.override(cfg)
        self.document = PyfficePresentation()
        self.timer = None
        self.interval_ms = self.config.dikt["interval_ms"]
        self.current_slide = 0
        self.slides = []

    def initModel(self):
        """"""
        return self

    def initView(self):
        """"""
        self.slideShowView = pyqt.QGraphicsView(self)
        self.slideShowScene = pyqt.QGraphicsScene(self)
        self.slideShowView.setScene(self.slideShowScene)

        layout = pyqt.QVBoxLayout()
        self.label = pyqt.QLabel()
        self.timer = pyqt.QTimer()
        self.timer.timeout(self.next_slide)
        self.timer.start(self.interval_ms)
        self.label.setPixmap(self.image)
        layout.addWidget(self.label)
        self.setLayout(layout)

        return self

    def initWidget(self, path):
        """"""
        self.initModel()
        self.initView()
        return self

    def next_slide(self):
        """"""
        self.current_slide += 1
        if self.current_slide >= len(self.slides):
            self.current_slide = 0
        self.label.setPixmap(self.slides[self.current_slide])

    def previous_slide(self):
        """"""
        self.current_slide -= 1
        if self.current_slide <= 0:
            self.current_slide = len(self.slides) - 1
        self.label.setPixmap(self.slides[self.current_slide])

    def set_wait_time(self, wait_ms):
        """"""
        self.interval_ms = wait_ms
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
