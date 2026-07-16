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
from os.path import dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.groups import NchantdGridScrollGroupBox, NchantdGroup
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentManager
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.items.catalogs import NchantdCatalogItem
from kahndor.logma import Logma
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.forms.forms import NchantdForm
from nchantdoffice.widgets.panes.forms import NchantdNewFormItemPane
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.widgets import NchantdWidget

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "forms.yaml")


class NchantdOfficeForm(NchantdForm):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeForm").override(cfg))

    def initModel(self):
        """"""
        super().initModel()
        self.document = self.app.model.codex.init_form()
        self.document.load_document()
        self.context_menu_name = "context.document.form"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def init_drawer_document_config(self):
        """"""
        items = {}
        return items

    def init_drawer_selection_config(self):
        """"""
        items = {}
        return items

    def init_drawer_object_config(self):
        """"""
        items = {}
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        # if self.toolbox_config is None:
        #     return None
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_selection_config()
        self.toolbox_config[300]["items"] = self.init_drawer_object_config()
        self.toolbox_config[500]["items"] = self.init_drawer_quickstart()


class NchantdOfficeContactForm(NchantdForm):
    """Pre-configured contact information form"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeContactForm").override(cfg))

    def initModel(self):
        """"""
        super().initModel()
        return self

    def initView(self):
        """"""
        super().initView()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeFormManager(NchantdOfficeDocumentManager):
    """TODO: take an excel upload and convert it into and form and deploy it as a google form in a few clicks"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeFormManager").override(cfg))
        self.catalog = self
        self.form = None
        self.button_bar = None
        self.selected_form = None
        self.forms = []
        self.available_items = []
        self.select_form_compatibility = None
        self.form_catalog_group = None
        self.form_view_group = None
        self.new_item_pane = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.available_items = [
            {
                "text": "Blank",
                "action": "add_form_blank",
                "size_policy": "fixed",
                "width": 60,
                "height": 60,
                "widget": NchantdOfficeForm,
            },
            {
                "text": "Contact",
                "action": "add_form_contact",
                "size_policy": "fixed",
                "width": 60,
                "height": 60,
                "widget": NchantdOfficeContactForm,
            },
            {
                "text": "Issue",
                "action": "add_form_issue",
                "size_policy": "fixed",
                "width": 60,
                "height": 60,
                "widget": NchantdOfficeContactForm,
            },
            {
                "text": "New Feature",
                "action": "add_form_issue",
                "size_policy": "fixed",
                "width": 60,
                "height": 60,
                "widget": NchantdOfficeContactForm,
            },
        ]
        cfg = {}
        self.document = self.app.model.codex.init_forms_manager(cfg)
        self.document.load_document()
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        fcs_cfg = {
            "layout": "horizontal",
            "size": ["auto", 30],
            "label": "Select Form Compatibility:",
            "options": self.get_form_compatibility_options(),
        }
        self.form_compatibility_select = NchantdDropDown(self, fcs_cfg)
        cfg["buttons"] = {
            0: {"name": "select_form_compatibility", "widget": self.form_compatibility_select},
            1: {"action": "add_data_source_connection"},
            2: "_insert_stretch",
        }
        super().initView(cfg)
        manager_layout = pyqt.QHBoxLayout()
        self.form_catalog_group = NchantdGridScrollGroupBox()
        self.form_catalog_group.setTitle("Select Form Item")
        self.form_catalog_group.set_size(300)
        self.form_catalog_group.limit_horizontal()
        self.build_form_catalog()
        manager_layout.addLayout(self.form_catalog_group.layout)
        self.form_view_group = NchantdGridScrollGroupBox()
        self.form_view_group.setTitle("View or Modify Form")
        self.form_view_group.limit_horizontal()
        self.build_form()
        manager_layout.addLayout(self.form_view_group.layout)
        self.layout.addLayout(manager_layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def add_form(self, form):
        """"""
        self.selected_form = form
        self.forms.append(form)

    def add_form_field(self, field_type, label, required=False):
        """Add a new field to the current form

        Args:
            field_type: Type of field (text, number, email, dropdown, etc.)
            label: Field label
            required: Whether field is required
        """
        if not self.selected_form:
            logma.warning("No form selected")
            return self

        field_config = {
            "type": field_type,
            "label": label,
            "required": required,
            "id": f"field_{len(self.selected_form.items)}",
        }

        # Create field widget based on type
        field_widget = self.create_form_field_widget(field_config)
        self.add_form_item(field_widget)
        logma.info(f"Added {field_type} field: {label}")
        return self

    def add_form_item(self, item):
        """"""
        self.selected_form.add_item(item)

    def build_form(self):
        """"""

        row, col = 0, 0
        if self.selected_form is None:
            self.build_form_blank(row, col)
            row += 2
        else:
            for item in self.selected_form.items:
                self.form_view_group.addWidget(item, row, col)
                row += 1
        cfg = {}
        new_item_pane_group = NchantdGroup(self, cfg)
        new_item_pane_group.setTitle("Add New Form Item")
        new_item_pane_group_layout = pyqt.QVBoxLayout()
        new_item_pane_group.setLayout(new_item_pane_group_layout)
        cfg = {"size": ["auto", "auto"]}
        self.new_item_pane = NchantdNewFormItemPane(self, cfg).initWidget()
        new_item_pane_group_layout.addWidget(self.new_item_pane)
        self.form_view_group.addWidget(new_item_pane_group, row, col)
        return self

    def build_form_blank(self, row, col):
        """"""
        cfg = {
            "text": "This is a Blank Form that can be used to build a new form to be used in a survey or inside the Nchantd Office Application itself",
            "font": {"size": 30, "type": "Arial", "weight": "bold"},
            "wrap_limit": 1000,
            "size": ["auto", "auto"],
        }
        self.form_view_group.addWidget(NchantdLabel(self, cfg).initWidget(), row, col)
        form_details_group = pyqt.QGroupBox()
        form_details_group.setTitle("Form Details")
        form_details_group_layout = pyqt.QGridLayout()
        form_details_group.setLayout(form_details_group_layout)
        cfg = {
            "label": "Select Image to Use in Header",
            "size": [100, "auto"],
            "layout": "horizontal",
            "entrybox": {"size": ["auto", "auto"]},
        }
        self.form_header_image_entry = NchantdLabeledEntry(self, cfg).initWidget()
        form_details_group_layout.addWidget(self.form_header_image_entry, 0, 0)
        cfg = {
            "label": "Enter Form Title: ",
            "size": [100, "auto"],
            "layout": "horizontal",
            "entrybox": {"size": ["auto", "auto"]},
        }
        self.form_name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        form_details_group_layout.addWidget(self.form_name_entry, 0, 1)
        cfg = {
            "label": "Enter Form Description: ",
            "size": [100, "auto"],
            "layout": "horizontal",
            "entrybox": {"size": ["Auto", "auto"]},
        }
        self.form_description_entry = NchantdLabeledEntry(self, cfg).initWidget()
        form_details_group_layout.addWidget(self.form_description_entry, 0, 2)
        row += 1
        self.form_view_group.addWidget(form_details_group, row, col)

    def build_form_catalog(self):
        """"""
        row, col = 0, 0
        for item in self.available_items:
            if isinstance(item, dict):
                item = NchantdCatalogItem(self, item).initWidget()
            self.form_catalog_group.addWidget(item, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    # ========== Command Handlers ==========

    def cmd_select_form_compatibility(self, event=None):
        """Set form compatibility mode"""
        if hasattr(self, "form_compatibility_select"):
            compatibility = self.form_compatibility_select.currentText()
            logma.info(f"Setting form compatibility to: {compatibility}")
            if self.selected_form:
                self.selected_form.compatibility = compatibility
        return self

    def cmd_add_form_blank(self, event=None):
        """Add a new blank form"""
        new_form = NchantdOfficeForm(self).initWidget()
        self.add_form(new_form)
        self.build_form()
        logma.info("Added new blank form")
        return self

    def cmd_image_file_select(self, event=None):
        """Select image file for form header"""
        file_dialog = pyqt.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Header Image", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        if file_path and hasattr(self, "form_header_image_entry"):
            self.form_header_image_entry.set_text(file_path)
            logma.info(f"Selected header image: {file_path}")
        return self

    def cmd_on_change_form_title(self, event=None):
        """Handle form title change"""
        if hasattr(self, "form_name_entry") and self.selected_form:
            title = self.form_name_entry.get_text()
            self.selected_form.title = title
            logma.info(f"Form title changed to: {title}")
        return self

    def cmd_connect_to_service(self, event=None):
        """Connect to external form service"""
        if hasattr(self, "form_service_select") and hasattr(self, "form_account_name"):
            service = self.form_service_select.currentText()
            account = self.form_account_name.get_text()
            logma.info(f"Connecting to {service} with account: {account}")
            # NOTE: Implement service connection logic
        return self

    def cmd_validation_option_change(self, event=None, *args, **kwargs):
        """"""

    def collect_form_data(self):
        """Collect all form data into a dictionary

        Returns:
            dict of field_id -> value
        """
        form_data = {}

        if not self.selected_form:
            return form_data

        for item in self.selected_form.items:
            field_id = getattr(item, "id", None)
            if not field_id:
                continue

            # Get value based on widget type
            value = None
            if hasattr(item, "get_text"):
                value = item.get_text()
            elif hasattr(item, "value"):
                value = item.value()
            elif hasattr(item, "currentText"):
                value = item.currentText()
            elif hasattr(item, "isChecked"):
                value = item.isChecked()

            form_data[field_id] = value

        return form_data

    def create_data_table(self):
        """"""
        df = super().create_data_table()
        columns = []
        data = []
        df = DataFrame(data, columns=columns)
        return df

    def create_form_field_widget(self, field_config):
        """Create a form field widget from configuration"""
        field_type = field_config.get("type", "text")
        label = field_config.get("label", "")
        required = field_config.get("required", False)

        cfg = {
            "label": label + (" *" if required else ""),
            "layout": "horizontal",
        }

        if field_type in ["text", "email", "url", "phone"]:
            widget = NchantdLabeledEntry(self, cfg).initWidget()
        elif field_type == "number":
            from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox

            widget = NchantdLabeledSpinBox(self, cfg).initWidget()
        elif field_type == "dropdown":
            cfg["combobox"] = {"options": field_config.get("options", [])}
            widget = NchantdDropDown(self, cfg).initWidget()
        elif field_type == "checkbox":
            cfg["text"] = label
            widget = NchantdCheckbox(self, cfg).initWidget()
        else:
            widget = NchantdLabeledEntry(self, cfg).initWidget()

        return widget

    def get_form_compatibility_options(self):
        """"""
        options = ["Google Forms", "Nchantd Office", ""]
        return options

    def get_validation_options(self):
        """"""
        return ["None", "Email", "URL", "Number", "Phone", "Custom Regex"]

    def get_validation_option(self):
        """"""

    def init_drawer_document_config(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action.copy()
        options = ["Google Forms", "Nchantd Office"]
        cfg = {
            "label": "Form Compatibility: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
            "handler": self.cmd_select_form_compatibility,
        }
        self.form_compatibility_select = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.form_compatibility_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        response_types = ["Text", "Number", "Date", "Multiple Choice", "Checkboxes", "Dropdown"]
        cfg = {
            "label": "Default Response Type:",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": response_types},
            "handler": self.cmd_default_response_type_change,
            "value": self.get_default_response(),
        }
        self.form_default_response_check = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.form_default_response_check
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        triggers = ["On Submit", "On Change", "On Focus"]
        cfg = {
            "label": "Default Response Trigger:",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": triggers},
            "handler": self.cmd_default_response_trigger_type_change,
            "value": self.get_default_response_trigger(),
        }
        self.form_default_response_trigger_check = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.form_default_response_trigger_check
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "text": "Set Default Answer Required",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_default_answer_required,
            "value": self.get_default_answer_required(),
        }
        self.form_default_answer_required_check = NchantdCheckbox(self, cfg).initWidget()
        items[cnt]["widget"] = self.form_default_answer_required_check
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "text": "Set Default Always Asked",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_default_always_asked,
            "value": self.get_always_asked(),
        }
        self.form_default_always_asked_check = NchantdCheckbox(self, cfg).initWidget()
        items[cnt]["widget"] = self.form_default_always_asked_check
        cnt += 1
        return items

    def cmd_default_response_type_change(self):
        """"""
        # TODO implement method

    def cmd_default_answer_required(self):
        """"""
        # TODO implement method

    def cmd_default_response_trigger_type_change(self):
        """"""
        # TODO implement method

    def get_default_response(self):
        """"""
        # TODO implement method

    def get_default_response_trigger(self):
        """"""
        # TODO implement method

    def get_default_always_asked(self):
        """"""
        # TODO implement method

    def get_default_answer_required(self):
        """"""
        # TODO implement method

    def cmd_default_always_asked(self):
        """"""
        # TODO implement method

    def get_always_asked(self):
        """"""
        # TODO implement method

    def get_form_connection_options(self):
        """"""
        # TODO implement method

    def cmd_form_connection_change(self):
        """"""
        # TODO implement method

    def cmd_form_connection_option(self):
        """"""
        # TODO implement method

    def get_form_connection_option(self):
        """"""
        # TODO implement method

    def cmd_connection_account_name_change(self):
        """"""
        # TODO implement method

    def get_connection_form_account_name(self):
        """"""
        # TODO implement method

    def init_drawer_input_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action.copy()
        validation_options = self.get_validation_options()
        cfg = {
            "label": "Validation Type:",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": validation_options},
            "handler": self.cmd_validation_option_change,
            "value": self.get_validation_option(),
        }
        self.validation_options_select = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.validation_options_select
        cnt += 1
        return items

    def init_drawer_connections(self):
        """"""
        items = self.toolbox_config[300].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action.copy()
        options = ["Google Forms", "YouForm", "Notion Forms", "Nchantd Office"]
        cfg = {
            "label": "Form Service: ",
            "layout": "horizontal",
            "combobox": {
                "size": ["auto", "auto"],
                "options": self.get_form_connection_options(),
                "handler": self.cmd_form_connection_change,
                "value": self.get_form_connection_option(),
            },
        }
        self.form_service_select = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.form_service_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Account Name: ",
            "layout": "horizontal",
            "handler": self.cmd_connection_account_name_change,
            "value": self.get_connection_form_account_name(),
        }
        self.form_account_name = NchantdLabeledEntry(self, cfg).initWidget()
        items[cnt]["widget"] = self.form_account_name
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "text": "Connect to Service",
            "layout": "horizontal",
            "handler": self.cmd_connect_to_service,
        }
        self.service_connect_button = NchantdButton(self, cfg).initWidget()
        items[cnt]["widget"] = self.service_connect_button
        cnt += 1
        return items

    def init_drawer_quickstart(self):
        """"""
        items = {}
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        self.toolbox_config[200]["items"] = self.init_drawer_input_config()
        self.toolbox_config[300]["items"] = self.init_drawer_connections()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def remove_form_field(self, field_id):
        """Remove a field from the current form"""
        if not self.selected_form:
            return self

        # Find and remove field
        for item in self.selected_form.items:
            if hasattr(item, "id") and item.id == field_id:
                self.selected_form.items.remove(item)
                item.deleteLater()
                logma.info(f"Removed field: {field_id}")
                break

        return self

    def select_form(self, form_name):
        """"""
        self.selected_form = self.forms[form_name]

    def submit_form(self):
        """Submit form data"""
        # Validate first
        validation = self.validate_form()
        if not validation["valid"]:
            logma.error(f"Form validation failed: {validation['errors']}")
            # Show error dialog
            pyqt.QMessageBox.warning(self, "Validation Error", "\n".join(validation["errors"]))
            return False

        # Collect data
        form_data = self.collect_form_data()

        # Submit based on compatibility
        if hasattr(self, "form_compatibility_select"):
            compatibility = self.form_compatibility_select.currentText()
            if compatibility == "Google Forms":
                return self.submit_to_google_forms(form_data)
            elif compatibility == "Nchantd Office":
                return self.submit_to_local_storage(form_data)

        logma.info("Form submitted successfully")
        return True

    def submit_to_google_forms(self, form_data):
        """Submit form data to Google Forms"""
        logma.info("Submitting to Google Forms...")
        # NOTE: Implement Google Forms API integration
        return True

    def submit_to_local_storage(self, form_data):
        """Save form data locally"""
        if self.document:
            self.document.save_response(form_data)
            logma.info("Form data saved locally")
        return True

    def validate_form(self):
        """Validate all required fields in the form

        Returns:
            dict with 'valid' bool and 'errors' list
        """
        errors = []

        if not self.selected_form:
            return {"valid": False, "errors": ["No form selected"]}

        for item in self.selected_form.items:
            if hasattr(item, "required") and item.required:
                # Check if field has value
                value = None
                if hasattr(item, "get_text"):
                    value = item.get_text()
                elif hasattr(item, "value"):
                    value = item.value()
                elif hasattr(item, "isChecked"):
                    value = item.isChecked()

                if not value:
                    label = getattr(item, "label", "Unknown field")
                    errors.append(f"Required field '{label}' is empty")

        valid = len(errors) == 0
        logma.info(f"Form validation: {'passed' if valid else 'failed'}")

        return {"valid": valid, "errors": errors}


class NchantdOfficeFeedback(NchantdWidget):
    """Feedback form widget for collecting user feedback"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeFeedback"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

        # Feedback data
        self.feedback_type = "Bug Report"
        self.feedback_priority = "Medium"
        self.feedback_data = {}

        # UI elements
        self.type_select = None
        self.priority_select = None
        self.title_entry = None
        self.description_entry = None
        self.email_entry = None
        self.screenshot_button = None
        self.submit_button = None
        self.cancel_button = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        cfg["layout"] = "grid"
        super().initView(cfg)

        row = 0

        # Title
        title_cfg = {
            "text": "Send Feedback",
            "font": {"size": 16, "weight": "bold"},
        }
        title_label = NchantdLabel(self, title_cfg).initWidget()
        self.layout.addWidget(title_label, row, 0, 1, 2)
        row += 1

        # Feedback type
        type_cfg = {
            "label": "Feedback Type:",
            "layout": "horizontal",
            "combobox": {"options": ["Bug Report", "Feature Request", "Question", "General Feedback"]},
        }
        self.type_select = NchantdDropDown(self, type_cfg).initWidget()
        self.layout.addWidget(self.type_select, row, 0, 1, 2)
        row += 1

        # Priority
        priority_cfg = {
            "label": "Priority:",
            "layout": "horizontal",
            "combobox": {"options": ["Low", "Medium", "High", "Critical"]},
        }
        self.priority_select = NchantdDropDown(self, priority_cfg).initWidget()
        self.layout.addWidget(self.priority_select, row, 0, 1, 2)
        row += 1

        # Title/Summary
        title_cfg = {
            "label": "Title:",
            "layout": "horizontal",
            "text": "",
        }
        self.title_entry = NchantdLabeledEntry(self, title_cfg).initWidget()
        self.layout.addWidget(self.title_entry, row, 0, 1, 2)
        row += 1

        # Description
        desc_label = NchantdLabel(self, {"text": "Description:"}).initWidget()
        self.layout.addWidget(desc_label, row, 0, 1, 2)
        row += 1

        from nchantrs.widgets.media.editors.editors import NchantdEntryBox

        desc_cfg = {"size": ["auto", 150]}
        self.description_entry = NchantdEntryBox(self, desc_cfg).initWidget()
        self.layout.addWidget(self.description_entry, row, 0, 1, 2)
        row += 1

        # Email (optional)
        email_cfg = {
            "label": "Email (optional):",
            "layout": "horizontal",
            "text": "",
        }
        self.email_entry = NchantdLabeledEntry(self, email_cfg).initWidget()
        self.layout.addWidget(self.email_entry, row, 0, 1, 2)
        row += 1

        # Buttons
        button_layout = pyqt.QHBoxLayout()

        screenshot_cfg = {
            "text": "Attach Screenshot",
            "handler": self.cmd_attach_screenshot,
        }
        self.screenshot_button = NchantdButton(self, screenshot_cfg).initWidget()
        button_layout.addWidget(self.screenshot_button)

        button_layout.addStretch()

        cancel_cfg = {
            "text": "Cancel",
            "handler": self.cmd_cancel,
        }
        self.cancel_button = NchantdButton(self, cancel_cfg).initWidget()
        button_layout.addWidget(self.cancel_button)

        submit_cfg = {
            "text": "Submit Feedback",
            "handler": self.cmd_submit_feedback,
        }
        self.submit_button = NchantdButton(self, submit_cfg).initWidget()
        button_layout.addWidget(self.submit_button)

        self.layout.addLayout(button_layout, row, 0, 1, 2)

        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_attach_screenshot(self, event=None):
        """Attach a screenshot to the feedback"""
        file_dialog = pyqt.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Screenshot", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        if file_path:
            self.feedback_data["screenshot"] = file_path
            logma.info(f"Screenshot attached: {file_path}")
        return self

    def cmd_submit_feedback(self, event=None):
        """Submit the feedback"""
        # Collect feedback data
        if hasattr(self, "type_select"):
            self.feedback_data["type"] = self.type_select.currentText()
        if hasattr(self, "priority_select"):
            self.feedback_data["priority"] = self.priority_select.currentText()
        if hasattr(self, "title_entry"):
            self.feedback_data["title"] = self.title_entry.get_text()
        if hasattr(self, "description_entry"):
            self.feedback_data["description"] = self.description_entry.toPlainText()
        if hasattr(self, "email_entry"):
            self.feedback_data["email"] = self.email_entry.get_text()

        # Validate
        if not self.feedback_data.get("title"):
            pyqt.QMessageBox.warning(self, "Validation Error", "Please enter a title")
            return self

        if not self.feedback_data.get("description"):
            pyqt.QMessageBox.warning(self, "Validation Error", "Please enter a description")
            return self

        # Submit
        success = self.send_feedback(self.feedback_data)

        if success:
            pyqt.QMessageBox.information(self, "Feedback Sent", "Thank you for your feedback!")
            self.close()
        else:
            pyqt.QMessageBox.critical(self, "Error", "Failed to send feedback. Please try again later.")

        return self

    def cmd_cancel(self, event=None):
        """Cancel and close the feedback form"""
        self.close()
        return self

    def send_feedback(self, feedback_data):
        """Send feedback to server or save locally

        Args:
            feedback_data: Dictionary containing feedback information

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Add timestamp
            feedback_data["timestamp"] = dt.datetime.now().isoformat()

            # Save locally
            self.save_feedback_locally(feedback_data)

            # NOTE: Send to remote server/issue tracker
            # self.send_to_server(feedback_data)

            logma.info(f"Feedback submitted: {feedback_data['type']} - {feedback_data['title']}")
            return True

        except Exception as e:
            logma.error(f"Error sending feedback: {e}")
            return False

    def save_feedback_locally(self, feedback_data):
        """Save feedback to local file"""
        import json
        from os.path import exists, join

        feedback_file = join(here, "feedback_log.json")

        # Load existing feedback
        all_feedback = []
        if exists(feedback_file):
            try:
                with open(feedback_file, "r") as f:
                    all_feedback = json.load(f)
            except:
                pass

        # Append new feedback
        all_feedback.append(feedback_data)

        # Save
        with open(feedback_file, "w") as f:
            json.dump(all_feedback, f, indent=2)

        logma.info(f"Feedback saved to {feedback_file}")
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
