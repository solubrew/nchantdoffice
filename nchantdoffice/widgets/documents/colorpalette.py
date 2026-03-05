"""PyfficeColorPalette document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficeColorPalette as BasePyfficeColorPalette
from ogma.logma import Logma
logma = Logma(__name__)
logma.off()
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficeColorPalette(NchantdOfficeDocument, BasePyfficeColorPalette):
    """ColorPalette document - implements PyfficeColorPalette.
    
    Provides color palette management with color picker,
    palette creation, and export capabilities.
    """
    
    PYTYPE = 'colorpalette'
    DEFAULT_TOOLS = [
        {'id': 'add_color', 'icon': 'plus', 'label': 'Add Color', 'method': 'add_color'},
        {'id': 'remove_color', 'icon': 'minus', 'label': 'Remove Color', 'method': 'remove_color'},
        {'id': 'edit_color', 'icon': 'edit', 'label': 'Edit Color', 'method': 'edit_color'},
        {'id': 'picker', 'icon': 'eyedropper', 'label': 'Color Picker', 'method': 'open_picker'},
        {'id': 'import_palette', 'icon': 'import', 'label': 'Import Palette', 'method': 'import_palette'},
        {'id': 'export_palette', 'icon': 'export', 'label': 'Export Palette', 'method': 'export_palette'},
        {'id': 'copy_hex', 'icon': 'copy', 'label': 'Copy HEX', 'method': 'copy_hex'},
        {'id': 'copy_rgb', 'icon': 'copy', 'label': 'Copy RGB', 'method': 'copy_rgb'},
    ]
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for color palette document."""
        return cls.DEFAULT_TOOLS
    
    def add_color(self, color: str) -> bool:
        """Add a color to the palette."""
        try:
            self._colors.append(color)
            return True
        except Exception as e:
            logma.error(f"Failed to add color: {e}")
            return False
    
    def remove_color(self, index: int) -> bool:
        """Remove a color from the palette."""
        try:
            if 0 <= index < len(self._colors):
                self._colors.pop(index)
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to remove color: {e}")
            return False
    
    def edit_color(self, index: int, color: str) -> bool:
        """Edit a color in the palette."""
        try:
            if 0 <= index < len(self._colors):
                self._colors[index] = color
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to edit color: {e}")
            return False
    
    def open_picker(self) -> Optional[str]:
        """Open color picker dialog."""
        # Implementation would show QColorDialog
        return None
    
    def import_palette(self, filepath: str) -> bool:
        """Import palette from file."""
        try:
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
                self._colors = data.get('colors', [])
            return True
        except Exception as e:
            logma.error(f"Failed to import palette: {e}")
            return False
    
    def export_palette(self, filepath: str) -> bool:
        """Export palette to file."""
        try:
            import json
            with open(filepath, 'w') as f:
                json.dump({'colors': self._colors}, f, indent=2)
            return True
        except Exception as e:
            logma.error(f"Failed to export palette: {e}")
            return False
    
    def copy_hex(self, index: int) -> bool:
        """Copy color as HEX to clipboard."""
        try:
            from PyQt6.QtWidgets import QApplication
            if 0 <= index < len(self._colors):
                QApplication.clipboard().setText(self._colors[index])
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to copy HEX: {e}")
            return False
    
    def copy_rgb(self, index: int) -> bool:
        """Convert and copy color as RGB."""
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtGui import QColor
            if 0 <= index < len(self._colors):
                color = QColor(self._colors[index])
                rgb = f"rgb({color.red()}, {color.green()}, {color.blue()})"
                QApplication.clipboard().setText(rgb)
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to copy RGB: {e}")
            return False
