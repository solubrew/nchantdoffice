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
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.groups import NchantdVScrollGroupBox, NchantdHGroupBox
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry, NchantdDropDown
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "tasks.yaml")
pxcfg = {}


class NchantdOfficeTaskEntryPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeTaskEntry")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self)
        self.config.override(cfg)
        self.primary_settings_group = None

    def initModel(self):
        """"""
        super().initModel()

        return self

    def initView(self):
        """"""
        super().initView()
        cfg = {
            "label": "Task Action: ",
            "layout": "horizontal",
            "size": [75, 20],
            "entrybox": {
                "size": [200, 20],
            },
        }
        self.tab_name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.left_side_layout.addWidget(self.tab_name_entry)
        cfg = {
            "label": "Description: ",
            "layout": "horizontal",
            "size": [75, 20],
            "entrybox": {
                "size": [200, 20],
            },
        }
        self.description = NchantdLabeledEntry(self, cfg).initWidget()
        self.left_side_layout.addWidget(self.description)
        cfg = {
            "label": "Due Date: ",
            "layout": "horizontal",
            "size": [75, 20],
            "entrybox": {
                "size": [200, 20],
            },
        }
        self.due_dttm = NchantdLabeledEntry(self, cfg).initWidget()
        self.left_side_layout.addWidget(self.due_dttm)
        cfg = {
            "label": "Intended Start Date: ",
            "layout": "horizontal",
            "size": [75, 20],
            "entrybox": {
                "size": [200, 20],
            },
        }
        self.start_dttm = NchantdLabeledEntry(self, cfg).initWidget()
        self.left_side_layout.addWidget(self.start_dttm)
        cfg = {"action": "open_recurrence_config", "handler": self.open_recurrence_config}
        self.recurrence_button = NchantdButton(self, cfg).initWidget()
        self.center_layout.addWidget(self.recurrence_button)
        # have a group with check boxes for each focus the user has access to
        # this will control startup, quick launch options
        # a focus will reprsent a package like Action, Fund, etc
        cfg = {"action": None, "handler": self.accept}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        self.left_side_layout.addWidget(self.accept_buttons)
        self.left_side_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignBottom | pyqt.Qt.AlignmentFlag.AlignRight)
        # self.setSizePolicy(pyqt.QSizePolicy.Expanding, pyqt.QSizePolicy.Expanding)
        # self.left_side_layout.addLayout(self.accept_buttons_layout)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def accept(self):
        """"""

    def open_recurrence_config(self):
        """"""


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
