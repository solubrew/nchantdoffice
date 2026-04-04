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
from nchantrs.widgets.widgets import NchantdWidget
from pyffice.spreadsheet.finance.finance import ControlDataTable
from pyside6pandas.models.DataFrameModel import DataFrameModel

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "finance.yaml")


class NchantdSMAChart(baseCharts.NchantdTimeSeriesChart):
    """Simple Moving Average Chart"""

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdSMAChart")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """ """
        return self


class NchantdWMAChart(baseCharts.NchantdTimeSeriesChart):
    """Weighted Moving Average Chart"""

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdWMAChart")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """ """
        return self


class NchantdRSI(baseCharts.NchantdTimeSeriesChart):
    """Relative Strength Index Chart"""

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdRSIChart")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdRSI, self).__init__(parent)


class NchantdPriceHistoryChart(baseCharts.NchantdTimeSeriesChart):
    """Price History over Time Chart"""

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdPriceHistoryChart")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)
        super(NchantdPriceHistoryChart, self).__init__(parent)

    def bollinger_bands(self):
        pass


class NchantdVolumeChart(baseCharts.NchantdTimeSeriesChart):
    """Volume Bar Chart"""

    def __init__(self, parent=None, cfg={}):
        """ """
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdVolumeChart")
        self.config.override(cfg)
        if parent:
            self.config.override(parent.config)


class NchantdMACDChart(baseCharts.NchantdTimeSeriesChart):
    """ """

    def __init__(self):
        """ """


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
