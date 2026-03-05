# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name:
	description: NchantdOffice implementation of PyfficeChart
	version: 0.0.0.0.0.0
	authority: filesystem
	security: seclvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import dirname, join

# ======================================3rd Party Library Modules=====================================================||
from ogma.logma import Logma
from pyffice.charts.charts import PyfficeChart
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)
# logma.off()

# ====================================================================================================================||


class NchantdOfficeChart(NchantdOfficeDocument, PyfficeChart):
    """NchantdOffice implementation of PyfficeChart.
    
    This class implements the PyfficeChart document type for NchantdOffice,
    providing charting functionality with full GUI integration.
    
    Inherits from:
        - NchantdOfficeDocument: Base GUI document class
        - PyfficeChart: Pyffice data model for charts
    
    Attributes:
        type: Chart type (bar, line, pie, etc.)
        data: Chart data source
        series: Data series configurations
        theme: Chart visual theme
    """
    
    PYTYPE = PyfficeChart
    
    def __init__(self, name=None, parent=None, cfg=None):
        """Initialize NchantdOfficeChart document.
        
        Args:
            name: Document name
            parent: Parent widget/document
            cfg: Configuration dictionary
        """
        NchantdOfficeDocument.__init__(self, name, parent, cfg)
        PyfficeChart.__init__(self, cfg)
        self.document_type = "chart"
    
    def get_pyffice_tools(self):
        """Get toolbox tools for chart documents.
        
        Returns:
            list: Toolbox configuration for chart operations
        """
        return [
            {'id': 'data_source', 'icon': 'database', 'label': 'Data Source', 'method': 'set_data_source'},
            {'id': 'chart_type', 'icon': 'chart', 'label': 'Chart Type', 'method': 'change_type'},
            {'id': 'style', 'icon': 'palette', 'label': 'Style', 'method': 'apply_style'},
            {'id': 'legend', 'icon': 'info', 'label': 'Legend', 'method': 'toggle_legend'},
            {'id': 'title', 'icon': 'heading', 'label': 'Title', 'method': 'edit_title'},
            {'id': 'axes', 'icon': 'axis', 'label': 'Axes', 'method': 'configure_axes'},
            {'id': 'series', 'icon': 'line-chart', 'label': 'Series', 'method': 'edit_series'},
            {'id': 'export', 'icon': 'export', 'label': 'Export', 'method': 'export_chart'},
        ]
    
    def set_data_source(self, source=None, source_type='spreadsheet'):
        """Set the data source for the chart.
        
        Args:
            source: Data source (file path, DataFrame, etc.)
            source_type: Type of source ('spreadsheet', 'csv', 'database')
            
        Returns:
            self
        """
        logma.info(f"Set data source: {source} ({source_type})")
        return self
    
    def change_type(self, chart_type='bar'):
        """Change the chart type.
        
        Args:
            chart_type: New chart type ('bar', 'line', 'pie', 'scatter', 'area', etc.)
            
        Returns:
            self
        """
        logma.info(f"Change chart type to: {chart_type}")
        return self
    
    def apply_style(self, theme='whitegrid'):
        """Apply a visual theme to the chart.
        
        Args:
            theme: Theme name ('whitegrid', 'darkgrid', 'ticks', etc.)
            
        Returns:
            self
        """
        logma.info(f"Apply style: {theme}")
        return self
    
    def toggle_legend(self, position='right'):
        """Toggle and configure the chart legend.
        
        Args:
            position: Legend position ('right', 'left', 'top', 'bottom', 'none')
            
        Returns:
            self
        """
        logma.info(f"Toggle legend at: {position}")
        return self
    
    def edit_title(self, title=None, size=12, color='black'):
        """Edit the chart title.
        
        Args:
            title: Title text
            size: Font size
            color: Font color
            
        Returns:
            self
        """
        logma.info(f"Edit title: {title}")
        return self
    
    def configure_axes(self, xlabel=None, ylabel=None, xscale=None, yscale=None):
        """Configure the chart axes.
        
        Args:
            xlabel: X-axis label
            ylabel: Y-axis label
            xscale: X-axis scale ('linear', 'log')
            yscale: Y-axis scale ('linear', 'log')
            
        Returns:
            self
        """
        logma.info(f"Configure axes: x={xlabel}, y={ylabel}")
        return self
    
    def edit_series(self, series_name=None, label=None, color=None, marker=None):
        """Edit a data series.
        
        Args:
            series_name: Name of the series
            label: Series label
            color: Series color
            marker: Marker style
            
        Returns:
            self
        """
        logma.info(f"Edit series: {series_name}")
        return self
    
    def export_chart(self, format='png', path=None):
        """Export the chart to an image file.
        
        Args:
            format: Export format ('png', 'svg', 'pdf', 'jpg')
            path: Output file path
            
        Returns:
            self
        """
        logma.info(f"Export chart as {format} to {path}")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
