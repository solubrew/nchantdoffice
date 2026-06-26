"""Chart document types for nchantdoffice."""

from typing import Dict, Any, Optional
from pathlib import Path


class ChartDocument:
    """Represents a chart document."""
    
    def __init__(self, chart_type: str = "line", data: Optional[Dict[str, Any]] = None):
        self.chart_type = chart_type
        self.data = data or {}
        self.title = ""
        self.x_label = ""
        self.y_label = ""
    
    def set_data(self, data: Dict[str, Any]) -> None:
        """Set chart data."""
        self.data = data
    
    def set_labels(self, title: str, x_label: str = "", y_label: str = "") -> None:
        """Set chart labels."""
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
    
    def render(self) -> Dict[str, Any]:
        """Render the chart."""
        return {
            "type": self.chart_type,
            "title": self.title,
            "x_label": self.x_label,
            "y_label": self.y_label,
            "data": self.data
        }


class LineChart(ChartDocument):
    """Line chart document."""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        super().__init__(chart_type="line", data=data)


class BarChart(ChartDocument):
    """Bar chart document."""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        super().__init__(chart_type="bar", data=data)


class PieChart(ChartDocument):
    """Pie chart document."""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        super().__init__(chart_type="pie", data=data)


class ScatterChart(ChartDocument):
    """Scatter plot chart document."""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        super().__init__(chart_type="scatter", data=data)


class HistogramChart(ChartDocument):
    """Histogram chart document."""
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        super().__init__(chart_type="histogram", data=data)
