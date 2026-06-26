"""Contact document types for nchantdoffice."""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Contact:
    """Represents a contact."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    title: Optional[str] = None
    address: Optional[str] = None
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert contact to dictionary."""
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "organization": self.organization,
            "title": self.title,
            "address": self.address,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat()
        }


class ContactDocument:
    """Represents a contact document."""
    
    def __init__(self, name: str = "Contacts"):
        self.name = name
        self.contacts: List[Contact] = []
    
    def add_contact(self, contact: Contact) -> None:
        """Add a contact."""
        self.contacts.append(contact)
    
    def remove_contact(self, name: str) -> bool:
        """Remove a contact by name."""
        for i, contact in enumerate(self.contacts):
            if contact.name == name:
                self.contacts.pop(i)
                return True
        return False
    
    def search(self, query: str) -> List[Contact]:
        """Search contacts by query."""
        results = []
        query_lower = query.lower()
        for contact in self.contacts:
            if (query_lower in contact.name.lower() or
                (contact.email and query_lower in contact.email.lower()) or
                (contact.organization and query_lower in contact.organization.lower())):
                results.append(contact)
        return results
    
    def get_by_tag(self, tag: str) -> List[Contact]:
        """Get contacts by tag."""
        return [c for c in self.contacts if tag in c.tags]
    
    def export_vcard(self, contact: Contact) -> str:
        """Export contact as vCard format."""
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{contact.name}",
        ]
        if contact.email:
            lines.append(f"EMAIL:{contact.email}")
        if contact.phone:
            lines.append(f"TEL:{contact.phone}")
        if contact.organization:
            lines.append(f"ORG:{contact.organization}")
        if contact.address:
            lines.append(f"ADR:{contact.address}")
        lines.append("END:VCARD")
        return "\n".join(lines)
