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

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.documents.shows import NchantdFilmStrip
from nchantrs.widgets.trees import NchantdTimeTree
from nchantrs.widgets.tables import NchantdBulletedList
from nchantrs.widgets.tabsets import NchantdTabSet
from nchantrs.widgets.widgets import NchantdWidget

# from nchantrs.nchantdvision.app.models import NVSTreeModel, NVSTabSetModel
from nchantrs.widgets.business.atnr.content.news import NchantdCommunitiesSummary
from nchantrs.widgets.business.tags import NchantdQuickTagsWidget
from nchantrs.widgets.business.services import NchantdRecentServices
from nchantrs.widgets.groups import NchantdHScrollGroupBox
from nchantrs.wizards.pages import NchantdWizardPage
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "nchantdvision.yaml")


class NchantdNewNchantdVisionApplicationPage(NchantdWizardPage):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdNewAccountNchantdVisionPage")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdNewNchantdVisionApplicationPage, self).__init__(self.parent, self.config)

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


class NchantdVisionToolsPackage(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdVisionToolsPackage")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdVisionToolsPackage, self).__init__(self.parent, self.config)

    def add_ai_generator(self, pid):
        """"""
        pid = self.add_node(pid)
        services = self.app.model.get_tab_set("vision_ai_generators_service")
        self.add_tabs(services)
        return self

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


class NchantdImageGeneratorTool(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NchantdImageGeneratorTool")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NchantdImageGeneratorTool, self).__init__(self.parent, self.config)

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


class NVSTree(NchantdTimeTree):
    """"""

    def __init__(self, parent=None, cfg=None, root=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NVSTree")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NVSTree, self).__init__(self.parent, self.config)
        self.model = NVSTreeModel(self, root, self.config)
        self.app = pyqt.QApplication.instance()

    def add_data_storage_site_node(self, pid, url, name):
        """"""
        cfg = "{'url': '" + url + "'}"
        tabs = [[name, "nchantrs.widgets.browsers.browsers.NchantdWebBrowser", cfg, pid, 4]]
        self.add_tabset(tabs)
        return self

    def add_ai_image_generation_site_node(self, pid, url):
        """"""
        pid = self.add_node(pid)
        overview_cfg = "{}"
        prompt_cfg = "{'url': " + url + "}"
        communities_cfg = "{}"
        tips_cfg = "{}"
        get_apikey_cfg = "{}"
        tabs = [
            ["Overview", "nchantrs.widgets.documents.managers.NchantdPromptManager", overview_cfg, pid, 0],
            ["Prompt", "nchantrs.widgets.browsers.prompts.NchantdPromptBrowser", prompt_cfg, pid, 0],
            [
                "Communities",
                "nchantrs.widgets.business.atnr.socials.socials.NchantdCommunityOverview",
                communities_cfg,
                pid,
                1,
            ],
            ["Tips", "nchantrs.widgets.tables.NchantdBulletedList", tips_cfg, pid, 2],
            ["Get API Key", "nchantrs.widgets.browsers.browsers.NchantdWebBrowser", get_apikey_cfg, pid, 3],
        ]
        self.add_tabset(tabs)
        return self

    def initModel(self):
        super().initModel()

        table = "app_option"
        params = {"table": [table]}
        cfg = {"WHERE": {"IN": {"tag_txt": ["data_storage_site", "ai_image_generation_site"]}}}
        rdr = self.app.model.store.docs["db"].read(params, cfg)
        data = next(rdr).dikt[table]["df"]

        data_storage_sites = data[data["tag_txt"] == "data_storage_site"]
        if not data_storage_sites.empty:
            data_storage_sites.apply(self.add_data_storage_site_node, axis=1)

        data_ai_image_generation_sites = data[data["tag_txt"] == "ai_image_generation_site"]
        if not data_ai_image_generation_sites.empty:
            data_ai_image_generation_sites.apply(self.add_ai_image_generation_site_node, axis=1)

        return self


class NVSTabSet(NchantdTabSet):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NVSTabSet")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NVSTabSet, self).__init__(self.parent, self.config)
        self.model = NVSTabSetModel(self, self.config)

    def add_image_library_site_tab(self):
        """"""

        return self

    def initModel(self, pos, pid, newInstance):
        super().initModel(pos, pid, newInstance)

        table = "app_option"
        params = {"table": [table]}
        cfg = {
            "WHERE": {
                "IN": {
                    "tag_txt": [
                        "image_library_site",
                    ]
                }
            }
        }
        rdr = self.app.model.store.docs["db"].read(params, cfg)
        data = next(rdr).dikt[table]["df"]

        image_library_sites = data[data["tag_txt"] == "image_library_site"]
        if not image_library_sites.empty:
            image_library_sites.apply(self.add_data_storage_site_node, axis=1)

        if self.config.dikt.get("image_selection_sites", None):
            for site in self.config.dikt["image_selection_sites"]:
                self.add_(site["pid"], site["name"])

        return self


class NVSOverview(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NVSOverview")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NVSOverview, self).__init__(self.parent, self.config)

    def initModel(self):
        """"""
        return self

    def initView(self):
        """"""
        super().initView()

        scroll = NchantdHScrollGroupBox()
        scroll.setTitle("Recent Images")
        cfg = {"text": "Images"}
        scroll.addWidget(NchantdLabel(self, cfg).initWidget())  # turn this into a slideshowish thing
        self.layout.addLayout(scroll.layout)

        layout = pyqt.QHBoxLayout()
        cfg = {}
        layout.addWidget(NchantdRecentServices(self, cfg).initWidget())

        cfg = {}
        layout.addWidget(NchantdCommunitiesSummary(self, cfg).initWidget())

        self.layout.addLayout(layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NVSLocalLibraryOverview(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NVSLocalLibraryOverview, self).__init__(self.parent, self.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()

        layout = pyqt.QHBoxLayout()
        cfg = {"text": "Local Image Library"}
        label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(label, alignment=pyqt.Qt.AlignLeft)
        cfg = {"text": "Add Images"}
        self.button = NchantdButton(self, cfg).initWidget()
        layout.addWidget(self.button, alignment=pyqt.Qt.AlignLeft)
        self.tags = NchantdQuickTagsWidget().initWidget()
        layout.addWidget(self.tags, alignment=pyqt.Qt.AlignRight)
        self.layout.addLayout(layout)

        left_layout = pyqt.QHBoxLayout()
        bullet_list = NchantdBulletedList(self, self.config).initWidget()
        left_layout.addWidget(bullet_list)
        recent_list = NchantdFilmStrip(self, self.config).initWidget()
        left_layout.addWidget(recent_list)
        self.layout.addLayout(left_layout)

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NVSCloudLibraryOverview(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NVSCloudLibraryOverview, self).__init__(self.parent, self.config)

    def initModel(self):
        """"""
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


class NVSServiceLibraryOverview(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.instruct(pxcfg).select("NVSServiceLibraryOverview")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        super(NVSServiceLibraryOverview, self).__init__(self.parent, self.config)

    def initModel(self):
        """"""
        return self

    def initView(self):
        """"""
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
