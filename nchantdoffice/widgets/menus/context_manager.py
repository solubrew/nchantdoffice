# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid:
	name: NchantdOffice Context Menus
	description: >
		Right-click context menus throughout the NchantdOffice application.
		Provides menus for tabs, tree nodes, canvas, and other widgets.
	version: 0.0.0.0.0.0
	authority: filesystem
	security: seclvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
from functools import partial

# ======================================3rd Party Library Modules======================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "menus.yaml")
pxcfg = {}


class ContextMenuManager:
    """Centralized context menu manager for NchantdOffice.
    
    Provides consistent right-click menus across all widgets:
    - Tree nodes
    - Tabs
    - Canvas/workspace
    - Toolbar items
    - Toolbox items
    """
    
    # Menu definitions - can be extended or overridden
    MENU_REGISTRY = {
        'tree_node': [
            ('Open', 'open_node'),
            ('Open in New Tab', 'open_new_tab'),
            ('---', None),
            ('Rename', 'rename_node'),
            ('Delete', 'delete_node'),
            ('---', None),
            ('Copy Path', 'copy_path'),
            ('Copy Name', 'copy_name'),
            ('---', None),
            ('Move To...', 'move_node'),
            ('New Sibling', 'new_sibling'),
            ('New Child', 'new_child'),
        ],
        'tab': [
            ('Close', 'close_tab'),
            ('Close Others', 'close_others'),
            ('Close All', 'close_all'),
            ('---', None),
            ('Duplicate', 'duplicate_tab'),
            ('Rename', 'rename_tab'),
            ('---', None),
            ('Move to Window', 'move_window'),
            ('Pop Out', 'pop_out'),
        ],
        'center_tab': [
            ('Close', 'close_tab'),
            ('Close Others', 'close_others'),
            ('Close All', 'close_all'),
            ('---', None),
            ('Duplicate', 'duplicate_tab'),
            ('Rename', 'rename_tab'),
            ('---', None),
            ('Move to Right Pane', 'move_to_right'),
            ('Pop Out', 'pop_out'),
        ],
        'right_tab': [
            ('Close', 'close_tab'),
            ('Pin Tab', 'pin_tab'),
            ('---', None),
            ('Move to Center', 'move_to_center'),
        ],
        'canvas': [
            ('Paste', 'paste'),
            ('Paste as Child', 'paste_child'),
            ('Select All', 'select_all'),
            ('---', None),
            ('Add Widget', 'add_widget'),
            ('Add Note', 'add_note'),
            ('---', None),
            ('Grid Settings', 'grid_settings'),
            ('Snap to Grid', 'toggle_snap'),
        ],
        'toolbox_item': [
            ('Use', 'use_tool'),
            ('Configure', 'configure_tool'),
            ('---', None),
            ('Remove', 'remove_tool'),
            ('Reset to Default', 'reset_tool'),
        ],
        'toolbar': [
            ('Customize...', 'customize_toolbar'),
            ('Lock Toolbars', 'lock_toolbars'),
            ('---', None),
            ('Reset to Default', 'reset_toolbar'),
        ],
        'workspace': [
            ('New Window', 'new_window'),
            ('Close Window', 'close_window'),
            ('---', None),
            ('Save Layout', 'save_layout'),
            ('Load Layout', 'load_layout'),
            ('---', None),
            ('Preferences', 'preferences'),
        ],
    }
    
    def __init__(self, parent=None, cfg=None):
        """Initialize the context menu manager."""
        self.parent = parent
        self.config = condor.Instruct(pxcfg).select("ContextMenuManager")
        self.config.override(cfg)
        self.app = pyqt.QApplication.instance()
        self.menu_cache = {}  # Cache created menus
        self.action_handlers = {}  # Map actions to handlers
    
    def get_menu(self, menu_type, context=None):
        """Get or create a menu of the specified type.
        
        Args:
            menu_type: Key from MENU_REGISTRY (e.g., 'tree_node', 'tab')
            context: Optional context data for dynamic menu building
            
        Returns:
            QMenu instance
        """
        cache_key = f"{menu_type}_{id(context)}" if context else menu_type
        
        if cache_key in self.menu_cache:
            return self.menu_cache[cache_key]
        
        menu_def = self.MENU_REGISTRY.get(menu_type, [])
        menu = self._build_menu(menu_def, context)
        self.menu_cache[cache_key] = menu
        
        return menu
    
    def _build_menu(self, menu_def, context=None):
        """Build a QMenu from menu definition.
        
        Args:
            menu_def: List of (label, action) tuples
            context: Optional context for dynamic actions
            
        Returns:
            QMenu instance
        """
        menu = pyqt.QMenu(self.parent)
        
        for label, action in menu_def:
            if label == '---':
                menu.addSeparator()
                continue
            
            if action is None:
                # Submenu
                submenu = menu.addMenu(label)
                # Could add submenu items here dynamically
                continue
            
            # Create action
            qaction = pyqt.QAction(label, menu)
            
            # Connect to handler if registered
            if action in self.action_handlers:
                qaction.triggered.connect(partial(self.action_handlers[action], context))
            else:
                # Default: emit signal with action name
                qaction.triggered.connect(partial(self._default_handler, action, context))
            
            menu.addAction(qaction)
        
        return menu
    
    def _default_handler(self, action, context, checked=False):
        """Default handler for menu actions.
        
        Can be overridden or connected to specific widgets.
        """
        logma.info(f"Context menu action: {action}")
        if context:
            logma.info(f"Context: {context}")
        # Emit signal or call connected widget method
        if hasattr(self.parent, f"on_context_{action}"):
            getattr(self.parent, f"on_context_{action}")(context)
    
    def register_handler(self, action, handler):
        """Register a custom handler for an action.
        
        Args:
            action: Action name from MENU_REGISTRY
            handler: Callable to handle the action
        """
        self.action_handlers[action] = handler
    
    def show_menu(self, menu_type, event, context=None):
        """Show a context menu at the given event position.
        
        Args:
            menu_type: Type of menu to show
            event: QMouseEvent or QPoint for menu position
            context: Optional context data
            
        Returns:
            The menu that was shown
        """
        menu = self.get_menu(menu_type, context)
        
        if hasattr(event, 'globalPos'):
            menu.exec(event.globalPos())
        else:
            menu.exec(event)
        
        return menu


class TreeContextMenuMixin:
    """Mixin to add context menu functionality to tree widgets."""
    
    def __init__(self):
        self.context_menu_manager = ContextMenuManager(self)
        self.setContextMenuPolicy(pyqt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_tree_context_menu)
    
    def _show_tree_context_menu(self, position):
        """Show context menu for tree node."""
        index = self.indexAt(position)
        if not index.isValid():
            return
        
        # Get the node data
        node = self.model().itemFromIndex(index)
        context = {'node': node, 'index': index, 'tree': self}
        
        menu = self.context_menu_manager.get_menu('tree_node', context)
        menu.exec(self.mapToGlobal(position))


class TabContextMenuMixin:
    """Mixin to add context menu functionality to tab widgets."""
    
    def __init__(self):
        self.context_menu_manager = ContextMenuManager(self)
        self.setContextMenuPolicy(pyqt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_tab_context_menu)
    
    def _show_tab_context_menu(self, position):
        """Show context menu for tab."""
        # Get tab at position
        tab_index = self.tabBar().tabAt(position)
        if tab_index < 0:
            return
        
        context = {
            'tab_index': tab_index,
            'tab_widget': self.widget(tab_index),
            'tab_text': self.tabText(tab_index),
            'tabset': self,
        }
        
        # Different menu for center vs right pane
        pane_position = getattr(self, 'pane_position', 'center')
        menu_type = f'{pane_position}_tab' if pane_position in ['center', 'right'] else 'tab'
        
        menu = self.context_menu_manager.get_menu(menu_type, context)
        menu.exec(self.mapToGlobal(position))


class CanvasContextMenuMixin:
    """Mixin to add context menu functionality to canvas/workspace widgets."""
    
    def __init__(self):
        self.context_menu_manager = ContextMenuManager(self)
        self.setContextMenuPolicy(pyqt.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_canvas_context_menu)
    
    def _show_canvas_context_menu(self, position):
        """Show context menu for canvas."""
        context = {
            'position': position,
            'canvas': self,
            'selection': self.get_selected_items() if hasattr(self, 'get_selected_items') else [],
        }
        
        menu = self.context_menu_manager.get_menu('canvas', context)
        menu.exec(self.mapToGlobal(position))


# Convenience function to create context menus
def create_context_menu(parent, menu_type, context=None, handlers=None):
    """Create a context menu with custom handlers.
    
    Args:
        parent: Parent widget
        menu_type: Type of menu ('tree_node', 'tab', 'canvas', etc.)
        context: Context data for the menu
        handlers: Dict of {action_name: handler_function}
        
    Returns:
        QMenu instance
    """
    manager = ContextMenuManager(parent)
    
    if handlers:
        for action, handler in handlers.items():
            manager.register_handler(action, handler)
    
    return manager.get_menu(menu_type, context)


# ====================================================================================================================||
# Example usage in a widget:
"""
from nchantdoffice.widgets.menus import TreeContextMenuMixin, TabContextMenuMixin

class MyTree(NchantdApplicationTree, TreeContextMenuMixin):
    def __init__(self, parent=None, cfg=None):
        super().__init__(parent, cfg)
        TreeContextMenuMixin.__init__(self)
        
        # Register custom handlers
        self.context_menu_manager.register_handler('open_node', self.handle_open)
        self.context_menu_manager.register_handler('delete_node', self.handle_delete)
    
    def handle_open(self, context):
        node = context['node']
        # Open the node...
        
    def handle_delete(self, context):
        node = context['node']
        # Delete the node...
"""

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
