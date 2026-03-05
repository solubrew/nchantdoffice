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
from functools import lru_cache

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantrs.widgets.tabsets import NchantdTabSet
from nchantdoffice.models import NchantdOfficeTabSetModel
from nchantdoffice.widgets.controls.toolboxes import NchantdOfficeApplicationToolBox

# Lazy imports for heavy widgets - loaded on demand
# Heavy widgets like charts, media, workbooks will be lazy loaded
_note_cache = None

def _get_note_widget():
    """Lazy load note widget to improve startup performance"""
    global _note_cache
    if _note_cache is None:
        from nchantdoffice.widgets.documents.media.notes import NchantdOfficeNote
        _note_cache = NchantdOfficeNote
    return _note_cache

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "widgets.yaml")
pxcfg = {}


class NchantdOfficeTabSet(NchantdTabSet):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("NchantdOfficeTabSet")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.model = NchantdOfficeTabSetModel(self, self.config)
        self.dragged_tab_index = -1
        self.cross_pane_drag_enabled = True

    def initModel(self, create_objects=True):
        """"""
        super().initModel(create_objects)
        return self

    def initView(self):
        """"""
        super().initView()
        # Enable cross-pane drag and drop
        self.setAcceptDrops(True)
        self.setMovable(True)
        self.setDragEnabled(True)
        return self

    def init_drag_drop(self):
        """Initialize drag and drop for this tabset"""
        self.setAcceptDrops(True)
        self.setMovable(True)
        self.setDragEnabled(True)
        return self
    
    def dragEnterEvent(self, event):
        """Handle drag enter events for cross-pane drops"""
        # Accept tab drags from other tabset widgets
        if event.mimeData().hasFormat("application/x-tab-index"):
            event.acceptProposedAction()
            return
        # Accept drags from other panes
        if event.mimeData().hasText():
            try:
                tab_data = eval(event.mimeData().text())
                if isinstance(tab_data, dict) and "source_widget" in tab_data:
                    event.acceptProposedAction()
                    return
            except:
                pass
        super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        """Handle drag move events for cross-pane drops"""
        if event.mimeData().hasFormat("application/x-tab-index"):
            event.acceptProposedAction()
            return
        if event.mimeData().hasText():
            event.acceptProposedAction()
            return
        super().dragMoveEvent(event)

    def dropEvent(self, event):
        """Handle drop events for cross-pane tab transfers"""
        self.drag_start_position = None
        
        # Handle cross-pane tab drops
        if event.mimeData().hasFormat("application/x-tab-index"):
            self._handle_cross_pane_drop(event)
            return
        
        # Handle text-based drops (from other widgets)
        if event.mimeData().hasText():
            self._handle_text_drop(event)
            return
            
        super().dropEvent(event)

    def _handle_cross_pane_drop(self, event):
        """Handle dropping a tab from another pane"""
        try:
            source_index = int(event.mimeData().data("application/x-tab-index").data().decode())
            source_widget_id = None
            
            # Try to find the source widget
            main_window = self.window()
            if hasattr(main_window, "tab_widgets"):
                for tab_widget in main_window.tab_widgets:
                    if id(tab_widget) != id(self):
                        # This is a cross-pane drop
                        source_widget = tab_widget
                        self._transfer_tab(source_widget, source_index, event.pos())
                        event.acceptProposedAction()
                        return
            
            # Fallback: try to handle internal drop
            super().dropEvent(event)
        except Exception as e:
            logma.info(f"Cross-pane drop error: {e}")
            event.ignore()

    def _handle_text_drop(self, event):
        """Handle dropping text/data from other widgets"""
        try:
            tab_data = eval(event.mimeData().text())
            if isinstance(tab_data, dict) and "source_widget" in tab_data:
                source_widget_id = tab_data["source_widget"]
                source_tab_index = tab_data["tab_index"]
                
                # Find source widget
                main_window = self.window()
                source_widget = None
                if hasattr(main_window, "tab_widgets"):
                    for tab_widget in main_window.tab_widgets:
                        if id(tab_widget) == source_widget_id:
                            source_widget = tab_widget
                            break
                
                if source_widget:
                    self._transfer_tab(source_widget, source_tab_index, event.pos())
                    event.acceptProposedAction()
        except Exception as e:
            logma.info(f"Text drop error: {e}")
            event.ignore()

    def _transfer_tab(self, source_widget, source_index, drop_pos):
        """Transfer a tab from another tabset to this one"""
        # Get tab data from source
        widget = source_widget.widget(source_index)
        tab_text = source_widget.tabText(source_index)
        tab_icon = source_widget.tabIcon(source_index)
        tab_tooltip = source_widget.tabToolTip(source_index)
        
        # Calculate drop position
        target_index = self.tabBar().tabAt(drop_pos)
        if target_index < 0:
            target_index = self.count()
        
        # Remove from source
        source_widget.removeTab(source_index)
        
        # Insert at target
        if target_index > source_index and source_widget == self:
            target_index -= 1
            
        new_index = self.insertTab(target_index, widget, tab_icon, tab_text)
        self.setTabToolTip(new_index, tab_tooltip)
        self.setCurrentIndex(new_index)
        
        logma.info(f"Transferred tab '{tab_text}' to position {new_index}")

    def launch_note(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        # Use lazy loaded note widget for faster startup
        NoteWidget = _get_note_widget()
        note = NoteWidget(self.app.main, cfg).initWidget()
        self.app.view.panes["center"].model.current_tab.append_note(note)
        return self

    @lru_cache(maxsize=16)
    def get_widget_config(self, widget_type):
        """Cache widget configuration lookups for performance"""
        return self.config.dikt.get(f"widgets.{widget_type}", {})

    def create_toolbox(self, parent=None, cfg=None):
        """"""
        toolbox = NchantdOfficeApplicationToolBox(parent, cfg)
        return toolbox

    def setTabText(self, position, text, store=True):
        """"""
        super().setTabText(position, text)
        if store:
            cfg = {"name_txt": text}
            self.app.model.update_tab(self.app.model.get_current_tab(), cfg)


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
