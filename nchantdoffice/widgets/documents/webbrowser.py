"""PyfficeWebBrowser document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficeWebBrowser as BasePyfficeWebBrowser
from nchantrs.logging import logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficeWebBrowser(NchantdOfficeDocument, BasePyfficeWebBrowser):
    """WebBrowser document - implements PyfficeWebBrowser.
    
    Provides web browser functionality with tabs, history,
    bookmarks, and download management.
    """
    
    PYTYPE = 'webbrowser'
    DEFAULT_TOOLS = [
        {'id': 'back', 'icon': 'arrow-left', 'label': 'Back', 'method': 'go_back'},
        {'id': 'forward', 'icon': 'arrow-right', 'label': 'Forward', 'method': 'go_forward'},
        {'id': 'refresh', 'icon': 'refresh', 'label': 'Refresh', 'method': 'refresh_page'},
        {'id': 'home', 'icon': 'home', 'label': 'Home', 'method': 'go_home'},
        {'id': 'new_tab', 'icon': 'plus', 'label': 'New Tab', 'method': 'new_tab'},
        {'id': 'close_tab', 'icon': 'x', 'label': 'Close Tab', 'method': 'close_tab'},
        {'id': 'bookmark', 'icon': 'bookmark', 'label': 'Bookmark', 'method': 'add_bookmark'},
        {'id': 'history', 'icon': 'clock', 'label': 'History', 'method': 'show_history'},
        {'id': 'downloads', 'icon': 'download', 'label': 'Downloads', 'method': 'show_downloads'},
        {'id': 'devtools', 'icon': 'code', 'label': 'DevTools', 'method': 'toggle_devtools'},
        {'id': 'zoom_in', 'icon': 'zoom-in', 'label': 'Zoom In', 'method': 'zoom_in'},
        {'id': 'zoom_out', 'icon': 'zoom-out', 'label': 'Zoom Out', 'method': 'zoom_out'},
    ]
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for web browser document."""
        return cls.DEFAULT_TOOLS
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._history = []
        self._bookmarks = {}
        self._downloads = []
        self._tabs = []
        self._current_tab = 0
    
    def go_back(self) -> bool:
        """Navigate back in history."""
        try:
            if hasattr(self, '_web_view') and self._web_view.history().canGoBack():
                self._web_view.back()
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to go back: {e}")
            return False
    
    def go_forward(self) -> bool:
        """Navigate forward in history."""
        try:
            if hasattr(self, '_web_view') and self._web_view.history().canGoForward():
                self._web_view.forward()
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to go forward: {e}")
            return False
    
    def refresh_page(self) -> bool:
        """Refresh current page."""
        try:
            if hasattr(self, '_web_view'):
                self._web_view.reload()
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to refresh: {e}")
            return False
    
    def go_home(self) -> bool:
        """Navigate to home page."""
        try:
            home_url = self._config.get('home_url', 'about:blank')
            self.load_url(home_url)
            return True
        except Exception as e:
            logma.error(f"Failed to go home: {e}")
            return False
    
    def load_url(self, url: str) -> bool:
        """Load a URL in the browser."""
        try:
            if hasattr(self, '_web_view'):
                self._web_view.setUrl(url)
                self._add_to_history(url)
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to load URL: {e}")
            return False
    
    def new_tab(self, url: str = 'about:blank') -> Optional[int]:
        """Create a new browser tab."""
        try:
            tab_index = len(self._tabs)
            self._tabs.append({'url': url, 'title': 'New Tab'})
            return tab_index
        except Exception as e:
            logma.error(f"Failed to create new tab: {e}")
            return None
    
    def close_tab(self, tab_index: int = None) -> bool:
        """Close a browser tab."""
        try:
            if tab_index is None:
                tab_index = self._current_tab
            if 0 <= tab_index < len(self._tabs):
                self._tabs.pop(tab_index)
                if self._current_tab >= len(self._tabs):
                    self._current_tab = max(0, len(self._tabs) - 1)
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to close tab: {e}")
            return False
    
    def add_bookmark(self, url: str, title: str = None) -> bool:
        """Add current page to bookmarks."""
        try:
            self._bookmarks[url] = title or url
            return True
        except Exception as e:
            logma.error(f"Failed to add bookmark: {e}")
            return False
    
    def remove_bookmark(self, url: str) -> bool:
        """Remove bookmark."""
        try:
            if url in self._bookmarks:
                del self._bookmarks[url]
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to remove bookmark: {e}")
            return False
    
    def get_bookmarks(self) -> Dict[str, str]:
        """Get all bookmarks."""
        return self._bookmarks.copy()
    
    def show_history(self) -> List[Dict[str, str]]:
        """Get browsing history."""
        return self._history.copy()
    
    def _add_to_history(self, url: str) -> None:
        """Add URL to history."""
        from datetime import datetime
        self._history.append({
            'url': url,
            'timestamp': datetime.now().isoformat(),
        })
        # Limit history size
        if len(self._history) > 1000:
            self._history = self._history[-1000:]
    
    def show_downloads(self) -> List[Dict[str, Any]]:
        """Get download list."""
        return self._downloads.copy()
    
    def add_download(self, url: str, filepath: str) -> bool:
        """Add a download task."""
        try:
            self._downloads.append({
                'url': url,
                'filepath': filepath,
                'status': 'pending',
                'progress': 0,
            })
            return True
        except Exception as e:
            logma.error(f"Failed to add download: {e}")
            return False
    
    def toggle_devtools(self) -> bool:
        """Toggle developer tools."""
        try:
            if hasattr(self, '_web_view'):
                # Toggle inspector
                inspector = getattr(self, '_inspector', None)
                if inspector:
                    inspector.toggle()
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to toggle devtools: {e}")
            return False
    
    def zoom_in(self) -> bool:
        """Zoom in page."""
        try:
            if hasattr(self, '_web_view'):
                self._web_view.setZoomFactor(self._web_view.zoomFactor() + 0.1)
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to zoom in: {e}")
            return False
    
    def zoom_out(self) -> bool:
        """Zoom out page."""
        try:
            if hasattr(self, '_web_view'):
                self._web_view.setZoomFactor(self._web_view.zoomFactor() - 0.1)
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to zoom out: {e}")
            return False
