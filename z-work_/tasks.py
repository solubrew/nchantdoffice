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
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument, NchantdOfficeDocumentManager
from nchantrs.widgets.calendars.days import NchantdDayCalendar
from nchantrs.widgets.groups import NchantdVScrollGroupBox
from nchantrs.widgets.tables.tables import NchantdTable
from nchantdoffice.widgets.panes.tasks import NchantdOfficeTaskEntryPane
from pyffice.items.tasks import PyfficeTasksManager, PyfficeProjectsManager

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "tasks.yaml")


# TODO: leverage NchantdAXN  and AXN tasks to replace the below
class NchantdOfficeTasksManager(NchantdOfficeDocumentManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeTasksManager")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)

    def initModel(self):
        """"""
        super().initModel()
        # load all tasks
        # use a default filter to get the display tasks...likely active
        # self.display_tasks = df
        return self

    def initView(self):
        """"""
        super().initView()
        # populate table of tasks
        cfg = {}
        self.projects_table = NchantdTable(self, cfg).initWidget()
        self.layout.addWidget(self.projects_table)
        cfg = {"size": ["auto", 400]}
        self.add_task = NchantdOfficeTaskEntryPane(self, cfg).initWidget()
        self.layout.addWidget(self.add_task)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeProjectsManager(NchantdOfficeDocumentManager):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("Nchantd")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)
        self.document = PyfficeProjectsManager(self.config)

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

    def create_daily_tasks(self):
        """"""


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
