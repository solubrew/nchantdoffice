"""PyfficeConfig document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficeConfig as BasePyfficeConfig
from nchantrs.logging import logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficeConfig(NchantdOfficeDocument, BasePyfficeConfig):
    """Config document - implements PyfficeConfig.
    
    Provides configuration management with key-value pairs,
    sections, validation, and import/export features.
    """
    
    PYTYPE = 'config'
    DEFAULT_TOOLS = [
        {'id': 'add_key', 'icon': 'plus', 'label': 'Add Key', 'method': 'add_key'},
        {'id': 'remove_key', 'icon': 'minus', 'label': 'Remove Key', 'method': 'remove_key'},
        {'id': 'edit_key', 'icon': 'edit', 'label': 'Edit Key', 'method': 'edit_key'},
        {'id': 'add_section', 'icon': 'folder', 'label': 'Add Section', 'method': 'add_section'},
        {'id': 'validate', 'icon': 'check', 'label': 'Validate', 'method': 'validate_config'},
        {'id': 'import_json', 'icon': 'file-json', 'label': 'Import JSON', 'method': 'import_json'},
        {'id': 'export_json', 'icon': 'save', 'label': 'Export JSON', 'method': 'export_json'},
        {'id': 'import_yaml', 'icon': 'file-code', 'label': 'Import YAML', 'method': 'import_yaml'},
        {'id': 'export_yaml', 'icon': 'download', 'label': 'Export YAML', 'method': 'export_yaml'},
        {'id': 'reset', 'icon': 'refresh', 'label': 'Reset', 'method': 'reset_config'},
    ]
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for config document."""
        return cls.DEFAULT_TOOLS
    
    def add_key(self, key: str, value: Any, section: str = None) -> bool:
        """Add a configuration key."""
        try:
            if section:
                if section not in self._config:
                    self._config[section] = {}
                self._config[section][key] = value
            else:
                self._config[key] = value
            return True
        except Exception as e:
            logma.error(f"Failed to add key: {e}")
            return False
    
    def remove_key(self, key: str, section: str = None) -> bool:
        """Remove a configuration key."""
        try:
            if section and section in self._config:
                if key in self._config[section]:
                    del self._config[section][key]
                    return True
            elif key in self._config:
                del self._config[key]
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to remove key: {e}")
            return False
    
    def edit_key(self, key: str, value: Any, section: str = None) -> bool:
        """Edit a configuration key value."""
        return self.add_key(key, value, section)
    
    def add_section(self, section: str) -> bool:
        """Add a configuration section."""
        try:
            if section not in self._config:
                self._config[section] = {}
                return True
            return False
        except Exception as e:
            logma.error(f"Failed to add section: {e}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration structure."""
        results = {'valid': True, 'errors': [], 'warnings': []}
        
        # Check for empty sections
        for section, values in self._config.items():
            if isinstance(values, dict) and not values:
                results['warnings'].append(f"Empty section: {section}")
        
        # Check for required keys (if schema defined)
        if hasattr(self, '_required_keys'):
            for key in self._required_keys:
                if key not in self._config:
                    results['errors'].append(f"Missing required key: {key}")
                    results['valid'] = False
        
        return results
    
    def import_json(self, filepath: str) -> bool:
        """Import configuration from JSON file."""
        try:
            import json
            with open(filepath, 'r') as f:
                self._config = json.load(f)
            return True
        except Exception as e:
            logma.error(f"Failed to import JSON: {e}")
            return False
    
    def export_json(self, filepath: str, indent: int = 2) -> bool:
        """Export configuration to JSON file."""
        try:
            import json
            with open(filepath, 'w') as f:
                json.dump(self._config, f, indent=indent)
            return True
        except Exception as e:
            logma.error(f"Failed to export JSON: {e}")
            return False
    
    def import_yaml(self, filepath: str) -> bool:
        """Import configuration from YAML file."""
        try:
            import yaml
            with open(filepath, 'r') as f:
                self._config = yaml.safe_load(f)
            return True
        except Exception as e:
            logma.error(f"Failed to import YAML: {e}")
            return False
    
    def export_yaml(self, filepath: str) -> bool:
        """Export configuration to YAML file."""
        try:
            import yaml
            with open(filepath, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
            return True
        except Exception as e:
            logma.error(f"Failed to export YAML: {e}")
            return False
    
    def reset_config(self) -> bool:
        """Reset configuration to default."""
        try:
            self._config = {}
            return True
        except Exception as e:
            logma.error(f"Failed to reset config: {e}")
            return False
    
    def get_value(self, key: str, default: Any = None, section: str = None) -> Any:
        """Get configuration value with optional default."""
        try:
            if section and section in self._config:
                return self._config[section].get(key, default)
            return self._config.get(key, default)
        except Exception as e:
            logma.error(f"Failed to get value: {e}")
            return default
