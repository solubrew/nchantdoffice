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
from pyffice.document import PyfficeChart

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "charts.yaml")


class NchantdOfficeChart(NchantdOfficeDocument, PyfficeChart):
    """Chart document - implements PyfficeChart"""
    
    PYTYPE = 'chart'
    
    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for chart documents"""
        return [
            {'id': 'data_source', 'icon': 'database', 'label': 'Data Source', 'method': 'set_data_source'},
            {'id': 'chart_type', 'icon': 'chart-bar', 'label': 'Chart Type', 'method': 'set_chart_type'},
            {'id': 'style', 'icon': 'palette', 'label': 'Style', 'method': 'set_style'},
            {'id': 'legend', 'icon': 'info-circle', 'label': 'Legend', 'method': 'toggle_legend'},
            {'id': 'axes', 'icon': 'axis', 'label': 'Axes', 'method': 'configure_axes'},
            {'id': 'export', 'icon': 'download', 'label': 'Export', 'method': 'export_chart'},
        ]
    
    def __init__(self, name="Nchantd Chart", parent=None, cfg=None):
        """ """
        super().__init__(name, parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeChart"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.chart_type = 'bar'
        self.data_source = None

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
    
    def set_data_source(self):
        """Set data source for chart"""
        logma.info("Setting chart data source...")
        return self
    
    def set_chart_type(self):
        """Set chart type"""
        logma.info("Setting chart type...")
        return self
    
    def set_style(self):
        """Set chart style"""
        logma.info("Setting chart style...")
        return self
    
    def toggle_legend(self):
        """Toggle legend visibility"""
        logma.info("Toggling legend...")
        return self
    
    def configure_axes(self):
        """Configure chart axes"""
        logma.info("Configuring axes...")
        return self
    
    def export_chart(self):
        """Export chart"""
        logma.info("Exporting chart...")
        return self


# ====================================================================================================================||
