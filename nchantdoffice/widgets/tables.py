#!/usr/bin/env python3
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


# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.widgets.tables.tables import NchantdTable
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.media.editors.selectors import NchantdComboBox
from nchantrs.widgets.controls.toolbars import NchantdButtonBar
from pycurity.pytime import PyTime
from nchantrs.libraries import pyqt

# ====================================================================================================================||
HERE = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)
if not log:
    logma.off()
# ====================================================================================================================||
PXCFG = join(HERE, "_data_", ".yaml")


class NchantdOfficeTable(NchantdTable):
    """"""

    def __init__(self, parent=None, cfg=None):
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(PXCFG).select("Nchantd").override(cfg))

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

    def set_data(self, data):
        """"""
        super().set_data(data)

    def assign_widget(self, column_name, x, y, d):
        """"""
        if self.config.dikt["column_widgets"][column_name] == "label":
            self.setCellWidget(y, x, NchantdLabel(self, d))
        elif self.config.dikt["column_widgets"][column_name] == "datetime":
            # logma.info(f"Date Time {d}")
            date_time_widget = pyqt.QDateTimeEdit()
            date_time_widget.setCalendarPopup(True)  # Enable calendar popup for easy selection
            date_time_widget.setDateTime(PyTime({"datetime": d}).get_datetime())  # Set current date and time
            self.setCellWidget(x, y, date_time_widget)
        elif self.config.dikt["column_widgets"][column_name] == "date":
            date_widget = pyqt.QDateEdit()
            date_widget.setCalendarPopup(True)
            date_widget.setDateTime(d)
            self.setCellWidget(x, y, date_widget)
        elif self.config.dikt["column_widgets"][column_name] == "time":
            time_widget = pyqt.QTimeEdit()
            time_widget.setCalendarPopup(True)
            time_widget.setDateTime(d)
            self.setCellWidget(x, y, time_widget)
        elif self.config.dikt["column_widgets"][column_name] == "combobox":
            cfg = {"text": d}
            combobox = NchantdComboBox(self, cfg).initWidget()
            self.setCellWidget(x, y, combobox)
        elif self.config.dikt["column_widgets"][column_name] == "checkbox":
            cfg = {}
            checkbox = pyqt.QCheckBox(d)
            checkbox.setChecked(True)
            self.setCellWidget(x, y, checkbox)
        elif self.config.dikt["column_widgets"][column_name] == "spinbox":
            cfg = {}
            spinbox = pyqt.QSpinBox()
            spinbox.setRange(0, 100)
            spinbox.setValue(0)
            self.setCellWidget(x, y, spinbox)
        elif self.config.dikt["column_widgets"][column_name] == "buttonbar":
            cfg = {}
            buttonbar = NchantdButtonBar(self, cfg).initWidget()
            self.setCellWidget(x, y, buttonbar)
        else:
            logma.warning(
                f"[tables] unknown column_widgets type {self.config.dikt['column_widgets'][column_name]!r} for column {column_name!r}"
            )
            raise Exception(f"Unknown Widget {self.config.dikt['column_widgets'][column_name]!r}")


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
