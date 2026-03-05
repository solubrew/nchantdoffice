"""
Lazy loading utilities for NchantdOffice performance optimization.

Provides:
- Lazy imports for heavy modules
- LazyWidget class for deferred widget loading
- Import optimization for pyffice, pandas, matplotlib
"""

import importlib
import sys
from typing import Any, Callable, Optional, Dict, Type, Union
from functools import wraps


# Module registry for lazy loading
_LAZY_MODULES: Dict[str, str] = {
    'pandas': 'pandas',
    'numpy': 'numpy',
    'matplotlib': 'matplotlib',
    'matplotlib.pyplot': 'matplotlib.pyplot',
    'seaborn': 'seaborn',
    'openpyxl': 'openpyxl',
    'xlrd': 'xlrd',
    'xlwt': 'xlwt',
    'pdfminer': 'pdfminer.six',
    'pyyaml': 'yaml',
    'jinja2': 'jinja2',
    'beautifulsoup4': 'bs4',
    'selenium': 'selenium',
    'requests': 'requests',
    'evernote': 'evernote',
    'notion': 'notion',
}

# Track which modules are actually loaded
_LOADED_MODULES: Dict[str, bool] = {}


def lazy_import(module_name: str, fromlist: tuple = ()):
    """
    Lazily import a module.
    
    Module is only imported when first accessed.
    
    Usage:
        pd = lazy_import('pandas')
        plt = lazy_import('matplotlib.pyplot')
    """
    if module_name in sys.modules:
        return sys.modules[module_name]
    
    def _load():
        if module_name in _LAZY_MODULES:
            actual_name = _LAZY_MODULES[module_name]
        else:
            actual_name = module_name
        
        if fromlist:
            mod = importlib.import_module(actual_name)
            return getattr(mod, fromlist[0]) if fromlist else mod
        else:
            return importlib.import_module(actual_name)
    
    # Create a lazy loader proxy
    return _LazyModuleProxy(module_name, _load)


class _LazyModuleProxy:
    """Proxy object for lazy module loading."""
    
    def __init__(self, name: str, loader: Callable):
        self._name = name
        self._loader = loader
        self._module = None
    
    def _ensure_loaded(self):
        if self._module is None:
            self._module = self._loader()
            _LOADED_MODULES[self._name] = True
        return self._module
    
    def __getattr__(self, name: str) -> Any:
        return getattr(self._ensure_loaded(), name)
    
    def __call__(self, *args, **kwargs):
        return self._ensure_loaded()(*args, **kwargs)
    
    def __repr__(self):
        return f"<LazyModule: {self._name}>"


class LazyImport:
    """
    Context manager for lazy imports with optional availability check.
    
    Usage:
        with LazyImport('pandas') as pd:
            df = pd.DataFrame(...)
        
        # Or with optional - won't fail if not available
        with LazyImport('optional_module', optional=True) as mod:
            if mod:
                mod.do_something()
    """
    
    def __init__(self, module_name: str, optional: bool = False):
        self.module_name = module_name
        self.optional = optional
        self.module = None
    
    def __enter__(self):
        try:
            self.module = lazy_import(self.module_name)
        except ImportError:
            if not self.optional:
                raise
            self.module = None
        return self.module
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def is_module_available(module_name: str) -> bool:
    """Check if a module is available without importing it."""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


def get_loaded_modules() -> Dict[str, bool]:
    """Get list of all lazily loaded modules."""
    return _LOADED_MODULES.copy()


# Pre-configured lazy imports for common heavy modules
# Usage: from nchantdoffice.utilities.lazy import pd, plt, sns
pd = lambda: lazy_import('pandas')
plt = lambda: lazy_import('matplotlib.pyplot')
sns = lambda: lazy_import('seaborn')
np = lambda: lazy_import('numpy')
openpyxl = lambda: lazy_import('openpyxl')


class LazyWidget:
    """
    Base class for lazily loading widgets.
    
    Widget content is only loaded when first displayed.
    """
    
    def __init__(self, widget_loader: Callable, *args, **kwargs):
        """
        Args:
            widget_loader: Callable that returns the actual widget
            *args, **kwargs: Arguments to pass to widget_loader
        """
        self._widget_loader = widget_loader
        self._args = args
        self._kwargs = kwargs
        self._widget = None
        self._loaded = False
    
    def _ensure_loaded(self):
        """Ensure widget is loaded."""
        if not self._loaded:
            self._widget = self._widget_loader(*self._args, **self._kwargs)
            self._loaded = True
        return self._widget
    
    @property
    def widget(self):
        """Get the actual widget."""
        return self._ensure_loaded()
    
    @property
    def is_loaded(self) -> bool:
        """Check if widget has been loaded."""
        return self._loaded
    
    def reload(self):
        """Force reload of the widget."""
        self._widget = None
        self._loaded = False
        return self._ensure_loaded()


def lazy_widget(widget_type: str, *args, **kwargs):
    """
    Factory function for creating lazy widgets.
    
    Usage:
        chart = lazy_widget('chart', data=data, chart_type='bar')
        table = lazy_widget('table', data=data, columns=cols)
    """
    widget_loaders = {
        'chart': lambda: _load_chart_widget(*args, **kwargs),
        'table': lambda: _load_table_widget(*args, **kwargs),
        'matrix': lambda: _load_matrix_widget(*args, **kwargs),
        'pdf': lambda: _load_pdf_widget(*args, **kwargs),
        'notebook': lambda: _load_notebook_widget(*args, **kwargs),
    }
    
    if widget_type not in widget_loaders:
        raise ValueError(f"Unknown widget type: {widget_type}")
    
    return LazyWidget(widget_loaders[widget_type])


# Widget loader stubs - replace with actual implementations
def _load_chart_widget(*args, **kwargs):
    """Lazily load chart widget."""
    from nchantdoffice.widgets.documents.analytics import charts
    return charts.NchantdChartWidget(*args, **kwargs)


def _load_table_widget(*args, **kwargs):
    """Lazily load table widget."""
    from nchantdoffice.widgets import table as table_module
    return table_module.NchantdTableWidget(*args, **kwargs)


def _load_matrix_widget(*args, **kwargs):
    """Lazily load matrix widget."""
    from nchantdoffice.widgets.documents.workbooks import matricies
    return matricies.NchantdMatrixWidget(*args, **kwargs)


def _load_pdf_widget(*args, **kwargs):
    """Lazily load PDF widget."""
    from nchantdoffice.widgets.documents.media import pdfs
    return pdfs.NchantdPDFWidget(*args, **kwargs)


def _load_notebook_widget(*args, **kwargs):
    """Lazily load notebook widget."""
    from nchantdoffice.widgets.documents.workbooks import notebooks
    return notebooks.NchantdNotebookWidget(*args, **kwargs)


class LazyLoader:
    """
    Generic lazy loader for any object.
    
    Usage:
        loader = LazyLoader(HeavyClass, arg1, arg2)
        obj = loader.get()  # Only creates object when needed
    """
    
    def __init__(self, factory: Callable, *args, **kwargs):
        self._factory = factory
        self._args = args
        self._kwargs = kwargs
        self._instance = None
        self._loaded = False
    
    def get(self):
        """Get or create the instance."""
        if not self._loaded:
            self._instance = self._factory(*self._args, **self._kwargs)
            self._loaded = True
        return self._instance
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    def reset(self):
        """Reset the loader to create a new instance."""
        self._instance = None
        self._loaded = False


def preload_modules(*module_names: str):
    """
    Preload specified modules eagerly.
    
    Use this for modules that will definitely be needed.
    
    Usage:
        preload_modules('pandas', 'matplotlib.pyplot')
    """
    for name in module_names:
        lazy_import(name)


def get_import_stats() -> Dict[str, Any]:
    """Get lazy import statistics."""
    return {
        "lazy_modules": list(_LAZY_MODULES.keys()),
        "loaded_modules": list(_LOADED_MODULES.keys()),
        "loaded_count": len(_LOADED_MODULES),
    }
