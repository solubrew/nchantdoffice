"""PyfficeTable document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficeTable as BasePyfficeTable
from ogma.logma import Logma
logma = Logma(__name__)
logma.off()
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficeTable(NchantdOfficeDocument, BasePyfficeTable):
    """Table document - implements PyfficeTable.
    
    Provides data table functionality with filtering, sorting,
    and export capabilities.
    """
    
    PYTYPE = 'table'
    DEFAULT_TOOLS = [
        {'id': 'add_row', 'icon': 'plus', 'label': 'Add Row', 'method': 'add_row'},
        {'id': 'add_col', 'icon': 'plus', 'label': 'Add Column', 'method': 'add_column'},
        {'id': 'delete_row', 'icon': 'minus', 'label': 'Delete Row', 'method': 'delete_row'},
        {'id': 'delete_col', 'icon': 'minus', 'label': 'Delete Column', 'method': 'delete_column'},
        {'id': 'filter', 'icon': 'filter', 'label': 'Filter', 'method': 'filter_data'},
        {'id': 'sort_asc', 'icon': 'sort-up', 'label': 'Sort Ascending', 'method': 'sort_ascending'},
        {'id': 'sort_desc', 'icon': 'sort-down', 'label': 'Sort Descending', 'method': 'sort_descending'},
        {'id': 'search', 'icon': 'search', 'label': 'Search', 'method': 'search_table'},
        {'id': 'export_csv', 'icon': 'file-csv', 'label': 'Export CSV', 'method': 'export_csv'},
        {'id': 'export_json', 'icon': 'file-json', 'label': 'Export JSON', 'method': 'export_json'},
    ]
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for table document."""
        return cls.DEFAULT_TOOLS
    
    def add_row(self, position: Optional[int] = None) -> bool:
        """Add a new row to the table."""
        try:
            if position is None:
                position = self.rowCount()
            self.insertRow(position)
            return True
        except Exception as e:
            logma.error(f"Failed to add row: {e}")
            return False
    
    def add_column(self, position: Optional[int] = None, header: str = None) -> bool:
        """Add a new column to the table."""
        try:
            if position is None:
                position = self.columnCount()
            self.insertColumn(position)
            if header:
                self.setHorizontalHeaderItem(position, header)
            return True
        except Exception as e:
            logma.error(f"Failed to add column: {e}")
            return False
    
    def delete_row(self, position: int) -> bool:
        """Delete a row from the table."""
        try:
            self.removeRow(position)
            return True
        except Exception as e:
            logma.error(f"Failed to delete row: {e}")
            return False
    
    def delete_column(self, position: int) -> bool:
        """Delete a column from the table."""
        try:
            self.removeColumn(position)
            return True
        except Exception as e:
            logma.error(f"Failed to delete column: {e}")
            return False
    
    def filter_data(self, column: int, value: Any) -> bool:
        """Filter table data by column value."""
        # Implementation would filter the model
        logma.info(f"Filtering column {column} for value: {value}")
        return True
    
    def sort_ascending(self, column: int) -> bool:
        """Sort table by column ascending."""
        self.sortByColumn(column, 1)  # Qt.AscendingOrder
        return True
    
    def sort_descending(self, column: int) -> bool:
        """Sort table by column descending."""
        self.sortByColumn(column, 0)  # Qt.DescendingOrder
        return True
    
    def search_table(self, query: str) -> List[int]:
        """Search table for matching rows."""
        results = []
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item and query.lower() in item.text().lower():
                    results.append(row)
                    break
        return results
    
    def export_csv(self, filepath: str) -> bool:
        """Export table data to CSV."""
        try:
            import csv
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write headers
                headers = [self.horizontalHeaderItem(i).text() 
                          for i in range(self.columnCount())]
                writer.writerow(headers)
                # Write data
                for row in range(self.rowCount()):
                    row_data = [self.item(row, col).text() 
                               for col in range(self.columnCount())]
                    writer.writerow(row_data)
            return True
        except Exception as e:
            logma.error(f"Failed to export CSV: {e}")
            return False
    
    def export_json(self, filepath: str) -> bool:
        """Export table data to JSON."""
        try:
            import json
            data = []
            for row in range(self.rowCount()):
                row_data = {}
                for col in range(self.columnCount()):
                    header = self.horizontalHeaderItem(col).text()
                    item = self.item(row, col)
                    row_data[header] = item.text() if item else ""
                data.append(row_data)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logma.error(f"Failed to export JSON: {e}")
            return False
