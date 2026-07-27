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

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.managers import NchantdManager
from nchantrs.widgets.groups import NchantdHScrollGroupBox, NchantdVScrollGroupBox
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry, NchantdEntryBox
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.tables.lists import NchantdList
from pyffice.contacts.contacts import PyfficeContact, PyfficeRolodex
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "contacts.yaml")


class NchantdOfficeContact(NchantdWidget):
    """Represents a single contact with all their information"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeContact").override(cfg))
        self.document = PyfficeContact()
        self.contact_id = None
        self.first_name = ""
        self.last_name = ""
        self.company = ""
        self.title = ""
        self.email = ""
        self.phone = ""
        self.mobile = ""
        self.address = ""
        self.city = ""
        self.state = ""
        self.zip_code = ""
        self.country = ""
        self.website = ""
        self.notes = ""
        self.tags = []
        self.avatar_path = None
        self.created_date = dt.datetime.now()
        self.modified_date = dt.datetime.now()

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        # Load contact data from document if available
        if hasattr(self.document, "data") and self.document.data:
            self.load_from_dict(self.document.data)
        return self

    def initView(self, cfg=None):
        """"""
        super().initView(cfg)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def load_from_dict(self, data):
        """Load contact data from dictionary"""
        self.contact_id = data.get("id")
        self.first_name = data.get("first_name", "")
        self.last_name = data.get("last_name", "")
        self.company = data.get("company", "")
        self.title = data.get("title", "")
        self.email = data.get("email", "")
        self.phone = data.get("phone", "")
        self.mobile = data.get("mobile", "")
        self.address = data.get("address", "")
        self.city = data.get("city", "")
        self.state = data.get("state", "")
        self.zip_code = data.get("zip_code", "")
        self.country = data.get("country", "")
        self.website = data.get("website", "")
        self.notes = data.get("notes", "")
        self.tags = data.get("tags", [])
        self.avatar_path = data.get("avatar_path")
        return self

    def to_dict(self):
        """Convert contact to dictionary"""
        return {
            "id": self.contact_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "company": self.company,
            "title": self.title,
            "email": self.email,
            "phone": self.phone,
            "mobile": self.mobile,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "country": self.country,
            "website": self.website,
            "notes": self.notes,
            "tags": self.tags,
            "avatar_path": self.avatar_path,
            "created_date": self.created_date.isoformat() if self.created_date else None,
            "modified_date": self.modified_date.isoformat() if self.modified_date else None,
        }

    def get_full_name(self):
        """Get full name of contact"""
        return f"{self.first_name} {self.last_name}".strip()

    def get_display_name(self):
        """Get display name with company if available"""
        name = self.get_full_name()
        if self.company:
            return f"{name} ({self.company})"
        return name

    def update_modified_date(self):
        """Update the modified timestamp"""
        self.modified_date = dt.datetime.now()
        return self


class NchantdOfficeRolodex(NchantdOfficeDocument):
    """Manager for all contacts - provides CRUD, search, and import/export"""

    def __init__(self, parent=None, cfg=None):
        """ """
        icfg = {}
        super().__init__("Nchantd Rolodex", parent, icfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeRolodex").override(cfg))
        self.contacts = []  # List of NchantdOfficeContact objects
        self.contact_panes = {}  # Dict of contact_id -> ContactPane widget
        self.contacts_group = None
        self.contact_likely_group = None
        self.search_entry = None
        self.filter_dropdown = None
        self.add_button = None
        self.import_button = None
        self.export_button = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        document = {"document": self.config.dikt.get("document", {})}
        self.document = self.app.model.codex.init_contacts(document)
        self.document.load_document()
        self.context_menu_name = "context.document.files"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        if "buttons" not in cfg:
            cfg["buttons"] = {}
        search_cfg = {"label": "Search:", "layout": "horizontal", "text": "", "handler": self.cmd_search_contacts}
        self.search_entry = NchantdLabeledEntry(self, search_cfg)
        cfg["buttons"][10] = {"action": "search_contacts", "widget": self.search_entry}
        filter_cfg = {
            "label": "Filter:",
            "layout": "horizontal",
            "combobox": {"options": ["All", "Recent", "Favorites", "Company"]},
            "handler": self.cmd_filter_contacts,
            "value": self.get_filter_option(),
        }
        self.filter_dropdown = NchantdDropDown(self, filter_cfg)
        cfg["buttons"][11] = {"action": "filter_contacts", "widget": self.filter_dropdown}

        add_cfg = {"text": "Add Contact", "handler": self.cmd_add_contact}
        self.add_button = NchantdButton(self, add_cfg)
        cfg["buttons"][12] = {"action": "add_contact", "widget": self.add_button}

        import_cfg = {"text": "Import", "handler": self.cmd_import_contacts}
        self.import_button = NchantdButton(self, import_cfg)
        cfg["buttons"][13] = {"action": "import_contacts", "widget": self.import_button}
        export_cfg = {"text": "Export", "handler": self.cmd_export_contacts}
        self.export_button = NchantdButton(self, export_cfg)
        cfg["buttons"][14] = {"action": "export_contacts", "widget": self.export_button}
        cfg["buttons"][49] = "_insert_stretch"
        super().initView(cfg)
        # Most likely contacts section
        self.contact_likely_group = NchantdHScrollGroupBox()
        self.contact_likely_group.setTitle(f"Most Likely Contacts")
        self.layout.addLayout(self.contact_likely_group.layout)
        # All contacts section
        self.contacts_group = NchantdVScrollGroupBox(self)
        self.contacts_group.setTitle(f"All Contacts ({len(self.contacts)})")
        self.layout.addLayout(self.contacts_group.layout)
        # Populate contacts
        self.display_contacts(self.contacts)

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_filter_option(self):
        """Return the stored value of get_filter_option."""
        return self.config.dikt.get('filter_option', '') or ''

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}

    def init_drawer_contact_group_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}

    def init_drawer_contact_config(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}

    def init_drawer_quickstart(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        cnt = 0
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_contact_group_config()
        self.toolbox_config[300]["items"] = self.init_drawer_contact_config()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()
        return self

    def load_contacts(self):
        """Load contacts from document/database"""
        try:
            if self.document and hasattr(self.document, "contacts") and self.document.contacts:
                for contact_data in self.document.contacts:
                    contact = NchantdOfficeContact(self)
                    if isinstance(contact_data, dict):
                        contact.load_from_dict(contact_data)
                    else:
                        contact = contact_data
                    self.contacts.append(contact)
                logma.info(f"Loaded {len(self.contacts)} contacts")
        except Exception as e:
            logma.error(f"Error loading contacts: {e}")
        return self

    def add_contact_object(self, contact):
        """Add a contact object to the rolodex"""
        if contact not in self.contacts:
            self.contacts.append(contact)
            contact_pane = self.create_contact_pane(contact)
            self.contact_panes[id(contact)] = contact_pane
            self.contacts_group.addWidget(contact_pane)
            self.update_contact_count()
            logma.info(f"Added contact: {contact.get_full_name()}")
        return self

    def save_contact(self, contact):
        """Save/update a contact"""
        if contact not in self.contacts:
            self.add_contact_object(contact)

        # Save to document
        if self.document:
            self.document.save_contact(contact.to_dict())

        logma.info(f"Saved contact: {contact.get_full_name()}")
        return self

    def delete_contact(self, contact):
        """Delete a contact"""
        if contact in self.contacts:
            self.contacts.remove(contact)

            # Remove from UI
            contact_id = id(contact)
            if contact_id in self.contact_panes:
                pane = self.contact_panes[contact_id]
                self.contacts_group.layout.removeWidget(pane)
                pane.deleteLater()
                del self.contact_panes[contact_id]

            # Delete from document
            if self.document:
                self.document.delete_contact(contact.contact_id)

            self.update_contact_count()
            logma.info(f"Deleted contact: {contact.get_full_name()}")

        return self

    def create_contact_pane(self, contact):
        """Create a ContactPane widget for a contact"""
        cfg = {"contact": contact}
        contact_pane = NchantdOfficeContactPane(self, cfg).initWidget()
        return contact_pane

    def display_contacts(self, contacts):
        """Display a list of contacts in the UI"""
        # Clear existing
        self.clear_contact_display()

        # Add contacts
        for contact in contacts:
            contact_pane = self.create_contact_pane(contact)
            self.contact_panes[id(contact)] = contact_pane
            self.contacts_group.addWidget(contact_pane)

        return self

    def clear_contact_display(self):
        """Clear all displayed contacts"""
        for contact_id, pane in self.contact_panes.items():
            self.contacts_group.layout.removeWidget(pane)
            pane.deleteLater()
        self.contact_panes.clear()
        return self

    def update_contact_count(self):
        """Update the contact count in the title"""
        if self.contacts_group:
            self.contacts_group.setTitle(f"All Contacts ({len(self.contacts)})")
        return self

    # ========== Command Handlers ==========

    def cmd_add_contact(self, event=None):
        """Create a new contact"""
        new_contact = NchantdOfficeContact(self)
        new_contact.first_name = "New"
        new_contact.last_name = "Contact"
        self.add_contact_object(new_contact)
        return self

    def cmd_search_contacts(self, search_text=None):
        """Search/filter contacts by text"""
        if search_text is None and hasattr(self.search_entry, "get_text"):
            search_text = self.search_entry.get_text()

        if not search_text:
            # Show all contacts
            self.display_contacts(self.contacts)
            return self

        search_text = search_text.lower()
        filtered = []

        for contact in self.contacts:
            # Search in name, email, company, phone
            if (
                search_text in contact.get_full_name().lower()
                or search_text in contact.email.lower()
                or search_text in contact.company.lower()
                or search_text in contact.phone
                or search_text in contact.mobile
            ):
                filtered.append(contact)

        self.display_contacts(filtered)
        logma.info(f"Search '{search_text}' found {len(filtered)} contacts")
        return self

    def cmd_filter_contacts(self, event=None):
        """Filter contacts by category"""
        if not hasattr(self.filter_dropdown, "currentText"):
            return self

        filter_type = self.filter_dropdown.currentText()

        if filter_type == "All":
            self.display_contacts(self.contacts)
        elif filter_type == "Recent":
            # Sort by modified date, show most recent
            sorted_contacts = sorted(self.contacts, key=lambda c: c.modified_date, reverse=True)
            self.display_contacts(sorted_contacts[:10])
        elif filter_type == "Favorites":
            # Filter favorites (would need favorite flag)
            favorites = [c for c in self.contacts if hasattr(c, "is_favorite") and c.is_favorite]
            self.display_contacts(favorites)
        elif filter_type == "Company":
            # Group by company
            sorted_contacts = sorted(self.contacts, key=lambda c: c.company or "")
            self.display_contacts(sorted_contacts)

        return self

    def cmd_import_contacts(self, event=None):
        """Import contacts from file"""
        from os.path import exists

        file_dialog = pyqt.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Import Contacts", "", "CSV Files (*.csv);;JSON Files (*.json);;vCard Files (*.vcf);;All Files (*)"
        )

        if file_path and exists(file_path):
            self.import_from_file(file_path)

        return self

    def cmd_export_contacts(self, event=None):
        """Export contacts to file"""
        file_dialog = pyqt.QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(
            self, "Export Contacts", "contacts.csv", "CSV Files (*.csv);;JSON Files (*.json);;vCard Files (*.vcf)"
        )

        if file_path:
            self.export_to_file(file_path)

        return self

    # ========== Import/Export Methods ==========

    def import_from_file(self, file_path):
        """Import contacts from file based on extension"""
        ext = file_path.split(".")[-1].lower()

        try:
            if ext == "csv":
                self.import_from_csv(file_path)
            elif ext == "json":
                self.import_from_json(file_path)
            elif ext == "vcf":
                self.import_from_vcard(file_path)
            else:
                logma.warning(f"Unsupported import format: {ext}")

            logma.info(f"Imported contacts from {file_path}")
        except Exception as e:
            logma.error(f"Error importing contacts: {e}")

        return self

    def import_from_csv(self, file_path):
        """Import contacts from CSV file"""
        import csv

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                contact = NchantdOfficeContact(self)
                contact.load_from_dict(row)
                self.add_contact_object(contact)

        return self

    def import_from_json(self, file_path):
        """Import contacts from JSON file"""
        import json

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                for contact_data in data:
                    contact = NchantdOfficeContact(self)
                    contact.load_from_dict(contact_data)
                    self.add_contact_object(contact)

        return self

    def import_from_vcard(self, file_path):
        """Import contacts from vCard file"""
        # Basic vCard parsing - would need vobject library for full support
        logma.info("vCard import requires vobject library")
        return self

    def export_to_file(self, file_path):
        """Export contacts to file based on extension"""
        ext = file_path.split(".")[-1].lower()

        try:
            if ext == "csv":
                self.export_to_csv(file_path)
            elif ext == "json":
                self.export_to_json(file_path)
            elif ext == "vcf":
                self.export_to_vcard(file_path)
            else:
                logma.warning(f"Unsupported export format: {ext}")

            logma.info(f"Exported {len(self.contacts)} contacts to {file_path}")
        except Exception as e:
            logma.error(f"Error exporting contacts: {e}")

        return self

    def export_to_csv(self, file_path):
        """Export contacts to CSV file"""
        import csv

        if not self.contacts:
            return self

        fieldnames = list(self.contacts[0].to_dict().keys())

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for contact in self.contacts:
                writer.writerow(contact.to_dict())

        return self

    def export_to_json(self, file_path):
        """Export contacts to JSON file"""
        import json

        contacts_data = [contact.to_dict() for contact in self.contacts]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(contacts_data, f, indent=2, ensure_ascii=False)

        return self

def _format_contact_as_vcard(contact):
    """Return the vCard 3.0 textual representation of one contact.

    Extracted from ``NchantdOfficeRolodex.export_to_vcard`` so the
    contact-attribute-access logic lives next to the dataclass, not
    buried in a UI method. Reads ``get_full_name``, ``last_name``,
    ``first_name``, ``email``, ``phone``, ``mobile``, ``company``,
    and ``title`` from ``contact``.
    """
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"FN:{contact.get_full_name()}",
        f"N:{contact.last_name};{contact.first_name};;;",
    ]
    if contact.email:
        lines.append(f"EMAIL:{contact.email}")
    if contact.phone:
        lines.append(f"TEL;TYPE=WORK:{contact.phone}")
    if contact.mobile:
        lines.append(f"TEL;TYPE=CELL:{contact.mobile}")
    if contact.company:
        lines.append(f"ORG:{contact.company}")
    if contact.title:
        lines.append(f"TITLE:{contact.title}")
    lines.append("END:VCARD")
    return "\n".join(lines) + "\n"


def _write_vcard_file(file_path, contacts):
    """Write a vCard 3.0 file containing one record per contact."""
    with open(file_path, "w", encoding="utf-8") as f:
        for contact in contacts:
            f.write(_format_contact_as_vcard(contact))


    def export_to_vcard(self, file_path):
        """Export contacts to vCard file"""
        _write_vcard_file(file_path, self.contacts)
        return self


class NchantdOfficeContactPane(NchantdWidget):
    """UI widget for displaying and editing a single contact"""

    def __init__(self, parent=None, cfg=None):
        """ """
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("NchantdOfficeContactPane")
        if self.parent:
            self.config.override(parent.config)
        super().__init__(self.parent)
        self.config.override(cfg)

        self.contact = None
        self.is_editing = False

        # UI Elements
        self.name_label = None
        self.first_name_entry = None
        self.last_name_entry = None
        self.company_entry = None
        self.title_entry = None
        self.email_entry = None
        self.phone_entry = None
        self.mobile_entry = None
        self.address_entry = None
        self.city_entry = None
        self.state_entry = None
        self.zip_entry = None
        self.country_entry = None
        self.website_entry = None
        self.notes_entry = None
        self.edit_button = None
        self.save_button = None
        self.delete_button = None
        self.avatar_label = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        # Create or load contact
        if cfg and "contact" in cfg:
            self.contact = cfg["contact"]
        elif cfg and "contact_data" in cfg:
            self.contact = NchantdOfficeContact(self)
            self.contact.load_from_dict(cfg["contact_data"])
        else:
            self.contact = NchantdOfficeContact(self)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "grid"
        super().initView(cfg)

        row = 0

        # Avatar section
        avatar_cfg = {"text": "👤", "size": [80, 80]}
        self.avatar_label = NchantdLabel(self, avatar_cfg).initWidget()
        self.layout.addWidget(self.avatar_label, row, 0, 3, 1)

        # Name section
        cfg = {"label": "First Name:", "layout": "horizontal", "text": self.contact.first_name}
        self.first_name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.first_name_entry, row, 1, 1, 2)
        row += 1

        cfg = {"label": "Last Name:", "layout": "horizontal", "text": self.contact.last_name}
        self.last_name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.last_name_entry, row, 1, 1, 2)
        row += 1

        # Company and Title
        cfg = {"label": "Company:", "layout": "horizontal", "text": self.contact.company}
        self.company_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.company_entry, row, 1, 1, 2)
        row += 1

        cfg = {"label": "Title:", "layout": "horizontal", "text": self.contact.title}
        self.title_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.title_entry, row, 0, 1, 3)
        row += 1

        # Contact Information
        cfg = {"label": "Email:", "layout": "horizontal", "text": self.contact.email}
        self.email_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.email_entry, row, 0, 1, 3)
        row += 1

        cfg = {"label": "Phone:", "layout": "horizontal", "text": self.contact.phone}
        self.phone_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.phone_entry, row, 0, 1, 3)
        row += 1

        cfg = {"label": "Mobile:", "layout": "horizontal", "text": self.contact.mobile}
        self.mobile_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.mobile_entry, row, 0, 1, 3)
        row += 1

        # Address
        cfg = {"label": "Address:", "layout": "horizontal", "text": self.contact.address}
        self.address_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.address_entry, row, 0, 1, 3)
        row += 1

        cfg = {"label": "City:", "layout": "horizontal", "text": self.contact.city}
        self.city_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.city_entry, row, 0, 1, 1)

        cfg = {"label": "State:", "layout": "horizontal", "text": self.contact.state}
        self.state_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.state_entry, row, 1, 1, 1)

        cfg = {"label": "Zip:", "layout": "horizontal", "text": self.contact.zip_code}
        self.zip_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.zip_entry, row, 2, 1, 1)
        row += 1

        cfg = {"label": "Country:", "layout": "horizontal", "text": self.contact.country}
        self.country_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.country_entry, row, 0, 1, 3)
        row += 1

        cfg = {"label": "Website:", "layout": "horizontal", "text": self.contact.website}
        self.website_entry = NchantdLabeledEntry(self, cfg).initWidget()
        self.layout.addWidget(self.website_entry, row, 0, 1, 3)
        row += 1

        # Notes
        cfg = {"label": "Notes:", "layout": "horizontal", "text": self.contact.notes}
        self.notes_entry = NchantdEntryBox(self, cfg).initWidget()
        self.layout.addWidget(self.notes_entry, row, 0, 2, 3)
        row += 2

        # Buttons
        button_layout = pyqt.QHBoxLayout()

        cfg = {"text": "Edit", "handler": self.cmd_edit_contact}
        self.edit_button = NchantdButton(self, cfg).initWidget()
        button_layout.addWidget(self.edit_button)

        cfg = {"text": "Save", "handler": self.cmd_save_contact}
        self.save_button = NchantdButton(self, cfg).initWidget()
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)

        cfg = {"text": "Delete", "handler": self.cmd_delete_contact}
        self.delete_button = NchantdButton(self, cfg).initWidget()
        button_layout.addWidget(self.delete_button)

        self.layout.addLayout(button_layout, row, 0, 1, 3)

        # Set all fields to read-only initially
        self.set_fields_editable(False)

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def set_fields_editable(self, editable):
        """Enable or disable editing of contact fields"""
        self.is_editing = editable

        if hasattr(self.first_name_entry, "entry"):
            self.first_name_entry.entry.setReadOnly(not editable)
        if hasattr(self.last_name_entry, "entry"):
            self.last_name_entry.entry.setReadOnly(not editable)
        if hasattr(self.company_entry, "entry"):
            self.company_entry.entry.setReadOnly(not editable)
        if hasattr(self.title_entry, "entry"):
            self.title_entry.entry.setReadOnly(not editable)
        if hasattr(self.email_entry, "entry"):
            self.email_entry.entry.setReadOnly(not editable)
        if hasattr(self.phone_entry, "entry"):
            self.phone_entry.entry.setReadOnly(not editable)
        if hasattr(self.mobile_entry, "entry"):
            self.mobile_entry.entry.setReadOnly(not editable)
        if hasattr(self.address_entry, "entry"):
            self.address_entry.entry.setReadOnly(not editable)
        if hasattr(self.city_entry, "entry"):
            self.city_entry.entry.setReadOnly(not editable)
        if hasattr(self.state_entry, "entry"):
            self.state_entry.entry.setReadOnly(not editable)
        if hasattr(self.zip_entry, "entry"):
            self.zip_entry.entry.setReadOnly(not editable)
        if hasattr(self.country_entry, "entry"):
            self.country_entry.entry.setReadOnly(not editable)
        if hasattr(self.website_entry, "entry"):
            self.website_entry.entry.setReadOnly(not editable)
        if hasattr(self.notes_entry, "entry"):
            self.notes_entry.setReadOnly(not editable)

        self.edit_button.setEnabled(not editable)
        self.save_button.setEnabled(editable)

        return self

    def cmd_edit_contact(self, event=None):
        """Enable editing mode"""
        self.set_fields_editable(True)
        return self

    def cmd_save_contact(self, event=None):
        """Save contact changes"""
        # Update contact object from UI fields
        if hasattr(self.first_name_entry, "get_text"):
            self.contact.first_name = self.first_name_entry.get_text()
        if hasattr(self.last_name_entry, "get_text"):
            self.contact.last_name = self.last_name_entry.get_text()
        if hasattr(self.company_entry, "get_text"):
            self.contact.company = self.company_entry.get_text()
        if hasattr(self.title_entry, "get_text"):
            self.contact.title = self.title_entry.get_text()
        if hasattr(self.email_entry, "get_text"):
            self.contact.email = self.email_entry.get_text()
        if hasattr(self.phone_entry, "get_text"):
            self.contact.phone = self.phone_entry.get_text()
        if hasattr(self.mobile_entry, "get_text"):
            self.contact.mobile = self.mobile_entry.get_text()
        if hasattr(self.address_entry, "get_text"):
            self.contact.address = self.address_entry.get_text()
        if hasattr(self.city_entry, "get_text"):
            self.contact.city = self.city_entry.get_text()
        if hasattr(self.state_entry, "get_text"):
            self.contact.state = self.state_entry.get_text()
        if hasattr(self.zip_entry, "get_text"):
            self.contact.zip_code = self.zip_entry.get_text()
        if hasattr(self.country_entry, "get_text"):
            self.contact.country = self.country_entry.get_text()
        if hasattr(self.website_entry, "get_text"):
            self.contact.website = self.website_entry.get_text()
        if hasattr(self.notes_entry, "toPlainText"):
            self.contact.notes = self.notes_entry.toPlainText()

        self.contact.update_modified_date()

        # Notify parent rolodex
        if self.parent and hasattr(self.parent, "save_contact"):
            self.parent.save_contact(self.contact)

        self.set_fields_editable(False)
        logma.info(f"Saved contact: {self.contact.get_full_name()}")
        return self

    def cmd_delete_contact(self, event=None):
        """Delete contact"""
        # Confirm deletion
        reply = pyqt.QMessageBox.question(
            self,
            "Delete Contact",
            f"Are you sure you want to delete {self.contact.get_full_name()}?",
            pyqt.QMessageBox.StandardButton.Yes | pyqt.QMessageBox.StandardButton.No,
        )

        if reply == pyqt.QMessageBox.StandardButton.Yes:
            # Notify parent rolodex
            if self.parent and hasattr(self.parent, "delete_contact"):
                self.parent.delete_contact(self.contact)
            logma.info(f"Deleted contact: {self.contact.get_full_name()}")

        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
