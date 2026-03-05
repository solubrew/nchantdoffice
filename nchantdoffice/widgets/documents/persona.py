"""PyfficePersona document implementation for NchantdOffice."""

from typing import Dict, List, Any, Optional
from pyffice.documents import PyfficePersona as BasePyfficePersona
from nchantrs.logging import logma
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

logma.off(__name__)


class NchantdOfficePersona(NchantdOfficeDocument, BasePyfficePersona):
    """Persona document - implements PyfficePersona.
    
    Provides persona profile management with avatar,
    contact info, social links, and attributes.
    """
    
    PYTYPE = 'persona'
    DEFAULT_TOOLS = [
        {'id': 'edit_profile', 'icon': 'user', 'label': 'Edit Profile', 'method': 'edit_profile'},
        {'id': 'set_avatar', 'icon': 'image', 'label': 'Set Avatar', 'method': 'set_avatar'},
        {'id': 'add_contact', 'icon': 'plus', 'label': 'Add Contact', 'method': 'add_contact'},
        {'id': 'add_social', 'icon': 'share', 'label': 'Add Social', 'method': 'add_social'},
        {'id': 'add_attribute', 'icon': 'tag', 'label': 'Add Attribute', 'method': 'add_attribute'},
        {'id': 'export_vcard', 'icon': 'file', 'label': 'Export vCard', 'method': 'export_vcard'},
        {'id': 'import_vcard', 'icon': 'download', 'label': 'Import vCard', 'method': 'import_vcard'},
        {'id': 'duplicate', 'icon': 'copy', 'label': 'Duplicate', 'method': 'duplicate'},
    ]
    
    @classmethod
    def get_pyffice_tools(cls) -> List[Dict[str, Any]]:
        """Return toolbox tools for persona document."""
        return cls.DEFAULT_TOOLS
    
    def edit_profile(self, **kwargs) -> bool:
        """Edit persona profile fields."""
        try:
            self._profile.update(kwargs)
            return True
        except Exception as e:
            logma.error(f"Failed to edit profile: {e}")
            return False
    
    def set_avatar(self, filepath: str) -> bool:
        """Set persona avatar image."""
        try:
            self._avatar = filepath
            return True
        except Exception as e:
            logma.error(f"Failed to set avatar: {e}")
            return False
    
    def add_contact(self, contact_type: str, value: str) -> bool:
        """Add contact information."""
        try:
            if 'contacts' not in self._profile:
                self._profile['contacts'] = {}
            self._profile['contacts'][contact_type] = value
            return True
        except Exception as e:
            logma.error(f"Failed to add contact: {e}")
            return False
    
    def add_social(self, platform: str, url: str) -> bool:
        """Add social media link."""
        try:
            if 'social' not in self._profile:
                self._profile['social'] = {}
            self._profile['social'][platform] = url
            return True
        except Exception as e:
            logma.error(f"Failed to add social: {e}")
            return False
    
    def add_attribute(self, key: str, value: str) -> bool:
        """Add custom persona attribute."""
        try:
            if 'attributes' not in self._profile:
                self._profile['attributes'] = {}
            self._profile['attributes'][key] = value
            return True
        except Exception as e:
            logma.error(f"Failed to add attribute: {e}")
            return False
    
    def export_vcard(self, filepath: str) -> bool:
        """Export persona as vCard."""
        try:
            lines = [
                "BEGIN:VCARD",
                "VERSION:3.0",
                f"FN:{self._profile.get('name', '')}",
                f"N:{self._profile.get('lastname', '')};{self._profile.get('firstname', '')}",
            ]
            if 'contacts' in self._profile:
                for ctype, value in self._profile['contacts'].items():
                    if ctype == 'email':
                        lines.append(f"EMAIL:{value}")
                    elif ctype == 'phone':
                        lines.append(f"TEL:{value}")
            lines.append("END:VCARD")
            with open(filepath, 'w') as f:
                f.write('\n'.join(lines))
            return True
        except Exception as e:
            logma.error(f"Failed to export vCard: {e}")
            return False
    
    def import_vcard(self, filepath: str) -> bool:
        """Import persona from vCard."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            # Parse vCard content
            for line in content.split('\n'):
                if line.startswith('FN:'):
                    self._profile['name'] = line[3:]
                elif line.startswith('EMAIL:'):
                    self.add_contact('email', line[6:])
                elif line.startswith('TEL:'):
                    self.add_contact('phone', line[4:])
            return True
        except Exception as e:
            logma.error(f"Failed to import vCard: {e}")
            return False
    
    def duplicate(self) -> 'NchantdOfficePersona':
        """Create a copy of this persona."""
        try:
            new_persona = self.__class__()
            new_persona._profile = self._profile.copy()
            new_persona._avatar = self._avatar
            return new_persona
        except Exception as e:
            logma.error(f"Failed to duplicate: {e}")
            return None
