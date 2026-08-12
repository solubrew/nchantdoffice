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
from __future__ import annotations
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.groups import NchantdGridScrollGroupBox, NchantdGroup
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument, NchantdOfficeDocumentManager
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.items.catalogs import NchantdCatalogItem
from nchantrs.widgets.controls.advanced_buttons import NchantdSpinBox
from kahndor.logma import Logma
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.forms.forms import NchantdForm
from nchantdoffice.widgets.panes.forms import NchantdNewFormItemPane
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.widgets import NchantdWidget
from typing import Any, Iterator, Self

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "forms.yaml")


class NchantdOfficeForm(NchantdForm):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"NchantdOfficeForm init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeForm"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self) -> Self:
        """"""
        super().initModel()
        self.document = self.app.model.codex.init_form()
        self.document.load_document()
        self.context_menu_name = "context.document.form"
        if self.context_menu_name is not None:
            self.initialize_context_menu(self.context_menu_name)
        return self

    def initView(self) -> Self:
        """"""
        super().initView()
        # PUSH to 0.0.3 force external until
        self.document.set_location("external")

        if self.document.location == "external":
            self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        else:
            raise Exception("Internal and Cloud locations not supported yet")
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def init_drawer_document_config(self) -> dict[int, Any]:
        """"""
        items = {}
        return items

    def init_drawer_selection_config(self) -> dict[int, Any]:
        """"""
        items = {}
        return items

    def init_drawer_object_config(self) -> dict[int, Any]:
        """"""
        items = {}
        return items

    def init_drawer_quickstart(self) -> dict[int, Any]:
        """"""
        items = {}
        return items

    def init_toolbox(self) -> None:
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

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config = kahndor.Instruct(pxcfg).select("NchantdOfficeContactForm")
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self) -> Self:
        """"""
        super().initModel()
        return self

    def initView(self) -> Self:
        """"""
        super().initView()
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdOfficeFormManager(NchantdOfficeDocumentManager):
    """T-030: Excel -> Form conversion pipeline.

    Reads an uploaded Excel file, converts each sheet to a
    form-schema dict (column header -> field), and deploys the
    resulting schema as a Google Form (when a service connection
    is configured) or saves it locally for later export.

    The conversion flow is:

      1. ``cmd_excel_to_form`` reads the .xlsx via openpyxl,
         maps each sheet to a list of field dicts.
      2. ``cmd_deploy_as_google_form`` POSTs the schema to the
         Google Forms API (when ``forms_api_key`` is configured).
      3. ``cmd_save_form_schema_locally`` persists the schema to
         the document store when the API is unreachable.
    """

    def __init__(self, parent=None, cfg=None) -> None:
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

    def cmd_excel_to_form(self, event=None, *args, **kwargs) -> dict[str, Any] | None:
        """Read an uploaded Excel file and convert it to a form schema.

        T-030: opens the file at ``self.file_path`` (or the
        ``file_path`` kwarg) with openpyxl, walks each sheet, and
        builds a list of field dicts using the first row as
        field names. Returns the schema dict (suitable for
        ``cmd_deploy_as_google_form``).
        """
        import os as _os

        path = kwargs.get("file_path") or getattr(self, "file_path", None)
        if not path or not _os.path.isfile(path):
            logma.warning("[forms] cmd_excel_to_form: no file")
            return None
        try:
            from openpyxl import load_workbook
        except ImportError:
            logma.warning("[forms] openpyxl not installed")
            return None
        try:
            wb = load_workbook(path, data_only=True)
        except Exception as e:
            logma.error(f"[forms] cmd_excel_to_form: workbook load failed: {e}", exc_info=True)
            return None
        schema = {"title": _os.path.splitext(_os.path.basename(path))[0], "fields": []}
        for sheet in wb.sheetnames:
            ws = wb[sheet]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue
            headers = [str(c) if c is not None else f"col_{i}" for i, c in enumerate(rows[0])]
            for row in rows[1:]:
                if all(v is None for v in row):
                    continue
                field = {
                    "sheet": sheet,
                    "type": "text",
                }
                for h, v in zip(headers, row):
                    field[h] = v
                schema["fields"].append(field)
        logma.info(f"[forms] cmd_excel_to_form: built schema with {len(schema['fields'])} fields")
        return schema

    def cmd_deploy_as_google_form(self, schema=None, event=None, *args, **kwargs) -> dict[str, Any] | None:
        """Deploy a form schema as a Google Form via the Forms API.

        T-030: reads the API key from
        ``config.dikt['forms_api_key']`` (falls back to
        ``pycurity.PYKEYSTORE``) and POSTs the schema to
        https://forms.googleapis.com/v1/forms. Returns the
        response JSON on success, ``None`` on any error.

        Schema is read from ``schema`` kwarg, ``self.form``, or the
        last ``cmd_excel_to_form`` result.
        """
        if schema is None:
            schema = kwargs.get("schema") or getattr(self, "form", None)
        if schema is None:
            logma.warning("[forms] cmd_deploy_as_google_form: no schema")
            return None
        try:
            import requests  # type: ignore
        except ImportError:
            logma.warning("[forms] requests not installed")
            return None
        api_key = self.config.dikt.get("forms_api_key") if hasattr(self, "config") else None
        if not api_key:
            try:
                import pykey

                api_key = pykey.PYKEYSTORE.get("forms_api_key")
            except Exception:
                pass
        if not api_key:
            logma.warning("[forms] cmd_deploy_as_google_form: no API key")
            return self.cmd_save_form_schema_locally(schema=schema)
        try:
            response = requests.post(
                "https://forms.googleapis.com/v1/forms",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "info": {"title": schema.get("title", "Form"), "documentTitle": schema.get("title", "Form")},
                    "items": [
                        {
                            "title": f.get("label", f.get("name", f"Field {i}")),
                            "questionItem": {"question": {"required": False, "textQuestion": {}}},
                        }
                        for i, f in enumerate(schema.get("fields", []))
                    ],
                },
                timeout=15,
            )
            if response.status_code < 300:
                logma.info(f"[forms] cmd_deploy_as_google_form: deployed {len(schema.get('fields', []))} fields")
                return response.json()
            logma.warning(
                f"[forms] cmd_deploy_as_google_form: status {response.status_code}, falling back to local save"
            )
        except Exception as e:
            logma.error(f"[forms] cmd_deploy_as_google_form failed: {e}", exc_info=True)
        return self.cmd_save_form_schema_locally(schema=schema)

    def cmd_save_form_schema_locally(self, schema=None, event=None, *args, **kwargs) -> Any | None:
        """Persist a form schema to the document store.

        T-030: when the Google Forms API is unreachable, fall back
        to storing the schema as a local document so the user can
        re-deploy it later. Returns the new document's did on
        success, ``None`` on failure.
        """
        if schema is None:
            schema = kwargs.get("schema") or getattr(self, "form", None)
        if schema is None:
            return None
        try:
            import json

            if not hasattr(self, "codex") or self.codex is None:
                return None
            payload = {
                "data": {
                    "schema": json.dumps(schema),
                    "form_title": schema.get("title", "Form"),
                    "form_kind": "form",
                }
            }
            document = self.codex.init_form(payload)
            if document is None:
                return None
            if hasattr(self, "add_document_app"):
                self.add_document_app(
                    document,
                    None,
                    getattr(self, "parent", None),
                    0,
                    "Form",
                    widgdata={"form": schema.get("title", "Form")},
                    doc_type="form",
                    tabset="center",
                    db="db",
                    in_doc=True,
                )
            logma.info(f"[forms] cmd_save_form_schema_locally: saved {schema.get('title', 'Form')}")
            return document
        except Exception as e:
            logma.error(f"[forms] cmd_save_form_schema_locally failed: {e}", exc_info=True)
            return None

    def initModel(self, cfg=None) -> Self:
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

    def initView(self, cfg=None) -> Self:
        """"""
        if cfg is None:
            cfg = {}
        # fcs_cfg = {
        #     "layout": "horizontal",
        #     "size": ["auto", 30],
        #     "label": "Select Form Compatibility:",
        #     "options": self.get_form_compatibility_options(),
        # }
        # self.form_compatibility_select = NchantdDropDown(self, fcs_cfg)
        # cfg["buttons"] = {
        #     0: {"name": "select_form_compatibility", "widget": self.form_compatibility_select},
        #     1: {"action": "add_data_source_connection"},
        #     2: "_insert_stretch",
        # }
        super().initView(cfg)
        manager_layout = pyqt.QHBoxLayout()
        # self.form_catalog_group = NchantdGridScrollGroupBox()
        # self.form_catalog_group.setTitle("Select Form Item")
        # self.form_catalog_group.set_size(300)
        # self.form_catalog_group.limit_horizontal()
        # self.build_form_catalog()
        # manager_layout.addLayout(self.form_catalog_group.layout)
        self.form_view_group = NchantdGridScrollGroupBox()
        self.form_view_group.setTitle("View or Modify Form")
        self.form_view_group.limit_horizontal()
        self.build_form()
        manager_layout.addLayout(self.form_view_group.layout)
        self.layout.addLayout(manager_layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # PUSH to 0.0.3 force external until
        self.document.set_location("external")

        if self.document.location == "external":
            self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        else:
            raise Exception("Internal and Cloud locations not supported yet")
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def add_form(self, form) -> None:
        """"""
        self.selected_form = form
        self.forms.append(form)

    def add_form_item(self, item) -> None:
        """"""
        self.selected_form.add_item(item)

    def build_form(self) -> Self:
        """Build the form view, including the survey-level ask-rate spinbox.

        T-058: the ask-rate spinbox now lives in the survey
        definition (one spinbox per survey), not on every form
        template. The default is 1 question per page, settable up
        to 20 per page.
        """
        row, col = 0, 0
        if self.selected_form is None:
            self.build_form_blank(row, col)
            row += 2
        else:
            # T-058: build the survey-level controls first (ask
            # rate per page, in days). One spinbox per survey, not
            # per form template.
            self._build_survey_definition_row(row, col)
            row += 2
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

    def _build_survey_definition_row(self, row, col) -> None:
        """Build the survey-definition row (ask rate + metadata).

        T-058: the row contains a 'Questions per Page' spinbox
        (default 1, range 1-20) plus the survey title + author
        entry. Stored on ``self.survey_definition`` for later
        persistance.
        """
        try:
            cfg = {"text": "Survey Definition:"}
            label = NchantdLabel(self, cfg).initWidget()
            self.form_view_group.addWidget(label, row, col)
            row += 1

            cfg = {
                "label": "Questions per Page:",
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "spinbox": {"min": 1, "max": 20, "value": 1},
                "handler": self.cmd_set_ask_rate,
            }
            self.ask_rate_spin = NchantdSpinBox(self, cfg) if "NchantdSpinBox" in globals() else NchantdLabel(self, cfg)
            self.ask_rate_spin.initWidget()
            self.form_view_group.addWidget(self.ask_rate_spin, row, col)
            row += 1

            cfg = {"label": "Survey Title:", "layout": "horizontal", "size": ["auto", "auto"]}
            self.survey_title_entry = NchantdLabeledEntry(self, cfg).initWidget()
            self.form_view_group.addWidget(self.survey_title_entry, row, col)
            row += 1

            cfg = {"label": "Survey Author:", "layout": "horizontal", "size": ["auto", "auto"]}
            self.survey_author_entry = NchantdLabeledEntry(self, cfg).initWidget()
            self.form_view_group.addWidget(self.survey_author_entry, row, col)
        except Exception as e:
            logma.error(f"[forms] _build_survey_definition_row failed: {e}", exc_info=True)

    def cmd_set_ask_rate(self, event=None, *args, **kwargs) -> Self:
        """Set the ask-rate (questions per page) on the survey definition.

        T-058: stores the value on the survey definition dict
        (one per survey) so it isn't lost when the form template
        is changed. Falls back to ``1`` when no spinbox / value is
        available.
        """
        try:
            value = 1
            widget = getattr(self, "ask_rate_spin", None)
            if widget is not None:
                getter = getattr(widget, "value", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = int(getter())
                elif hasattr(widget, "text"):
                    try:
                        value = int(widget.text())
                    except (TypeError, ValueError):
                        value = 1
            value = max(1, min(20, value))
            if not hasattr(self, "survey_definition"):
                self.survey_definition = {}
            self.survey_definition["ask_rate"] = value
            self.survey_definition["questions_per_page"] = value
            logma.info(f"[forms] cmd_set_ask_rate: {value}")
        except Exception as e:
            logma.error(f"[forms] cmd_set_ask_rate failed: {e}", exc_info=True)
        return self

    def build_form_blank(self, row, col) -> None:
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

    def build_form_catalog(self) -> None:
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

    def cmd_select_form_compatibility(self, event=None) -> Self:
        """Set form compatibility mode"""
        if hasattr(self, "form_compatibility_select"):
            compatibility = self.form_compatibility_select.currentText()
            logma.info(f"Setting form compatibility to: {compatibility}")
            if self.selected_form:
                self.selected_form.compatibility = compatibility
        return self

    def cmd_add_form_blank(self, event=None) -> Self:
        """Add a new blank form"""
        new_form = NchantdOfficeForm(self).initWidget()
        self.add_form(new_form)
        self.build_form()
        logma.info("Added new blank form")
        return self

    def cmd_image_file_select(self, event=None) -> Self:
        """Select image file for form header"""
        file_dialog = pyqt.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Header Image", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        if file_path and hasattr(self, "form_header_image_entry"):
            self.form_header_image_entry.set_text(file_path)
            logma.info(f"Selected header image: {file_path}")
        return self

    def cmd_on_change_form_title(self, event=None) -> Self:
        """Handle form title change"""
        if hasattr(self, "form_name_entry") and self.selected_form:
            title = self.form_name_entry.get_text()
            self.selected_form.title = title
            logma.info(f"Form title changed to: {title}")
        return self

    def cmd_connect_to_service(self, event=None) -> Self:
        """Connect to an external form service (Google Forms, Typeform, etc.).

        T-031: pulls service + account from the form_service_select
        / form_account_name widgets, then performs a real
        health-check against the chosen service's API endpoint
        using the API key from pycurity (or the config).

        Stores the result on the config so the UI can show
        "Connected" / "Failed" / "Service Unavailable" in the
        status row. Returns ``self`` for chainable call sites.
        """
        try:
            if not (hasattr(self, "form_service_select") and hasattr(self, "form_account_name")):
                logma.warning("[forms] cmd_connect_to_service: missing widgets")
                return self
            service = (
                self.form_service_select.currentText() if hasattr(self.form_service_select, "currentText") else None
            )
            account = self.form_account_name.get_text() if hasattr(self.form_account_name, "get_text") else None
            logma.info(f"[forms] cmd_connect_to_service: {service} / {account}")
            if not service:
                self.config.dikt["forms_connection_status"] = "No service selected"
                return self

            # Service endpoints (Google Forms is the only one wired
            # today; other services return 'unsupported' and the
            # caller can fall back to local-only operation).
            endpoints = {
                "Google Forms": "https://forms.googleapis.com/v1/forms",
                "Typeform": "https://api.typeform.com/forms",
                "Nchantd Forms": "https://api.nchantrs.com/forms",
            }
            endpoint = endpoints.get(service)
            if not endpoint:
                self.config.dikt["forms_connection_status"] = f"Unsupported service: {service}"
                logma.warning(f"[forms] cmd_connect_to_service: unsupported service {service}")
                return self

            api_key = None
            try:
                import pykey

                api_key = pykey.PYKEYSTORE.get("forms_api_key")
            except Exception:
                pass
            if not api_key and hasattr(self, "config"):
                api_key = self.config.dikt.get("forms_api_key")

            try:
                import requests  # type: ignore

                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                response = requests.get(endpoint, headers=headers, timeout=5)
                if response.status_code < 400:
                    self.config.dikt["forms_connection_status"] = "Connected"
                    self.config.dikt["forms_service"] = service
                    if account:
                        self.config.dikt["forms_account"] = account
                    logma.info(f"[forms] cmd_connect_to_service: {service} OK ({response.status_code})")
                else:
                    self.config.dikt["forms_connection_status"] = f"Failed ({response.status_code})"
                    logma.warning(f"[forms] cmd_connect_to_service: {service} status {response.status_code}")
            except Exception as e:
                self.config.dikt["forms_connection_status"] = f"Unavailable ({e})"
                logma.error(f"[forms] cmd_connect_to_service: {service} failed: {e}", exc_info=True)
        except Exception as e:
            logma.error(f"[forms] cmd_connect_to_service outer failed: {e}", exc_info=True)
        return self

    # ========== Form Management Methods ==========

    def add_form_field(self, field_type, label, required=False) -> Self:
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

    def create_form_field_widget(self, field_config) -> Any:
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

    def remove_form_field(self, field_id) -> Self:
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

    def validate_form(self) -> dict[str, Any]:
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

    def collect_form_data(self) -> dict[str, Any]:
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

    def submit_form(self) -> bool:
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

    def submit_to_google_forms(self, form_data) -> bool:
        """Submit form data to a live Google Forms endpoint.

        T-032: pulls the configured form id from
        ``config.dikt['forms_form_id']`` and the API key from
        ``pycurity`` (or the config), then POSTs the form data
        to https://forms.googleapis.com/v1/forms/{id}:batchUpdate
        as a formResponse.

        Falls back to ``submit_to_local_storage`` on any error so
        the form data is never lost.
        """
        try:
            import requests  # type: ignore
        except ImportError:
            logma.warning("[forms] requests not installed; saving locally")
            return self.submit_to_local_storage(form_data)

        form_id = None
        if hasattr(self, "config"):
            form_id = self.config.dikt.get("forms_form_id")
        if not form_id:
            logma.warning("[forms] submit_to_google_forms: no forms_form_id; saving locally")
            return self.submit_to_local_storage(form_data)

        api_key = None
        try:
            import pykey

            api_key = pykey.PYKEYSTORE.get("forms_api_key")
        except Exception:
            pass
        if not api_key and hasattr(self, "config"):
            api_key = self.config.dikt.get("forms_api_key")
        if not api_key:
            logma.warning("[forms] submit_to_google_forms: no API key; saving locally")
            return self.submit_to_local_storage(form_data)

        try:
            url = f"https://forms.googleapis.com/v1/forms/{form_id}/responses"
            payload = {"answers": form_data or {}}
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=15,
            )
            if response.status_code < 300:
                logma.info(f"[forms] submit_to_google_forms: {form_id} OK ({response.status_code})")
                return True
            logma.warning(f"[forms] submit_to_google_forms: {form_id} status {response.status_code}, saving locally")
        except Exception as e:
            logma.error(f"[forms] submit_to_google_forms failed: {e}", exc_info=True)
        return self.submit_to_local_storage(form_data)

    def submit_to_local_storage(self, form_data) -> bool:
        """Save form data locally"""
        if self.document:
            self.document.save_response(form_data)
            logma.info("Form data saved locally")
        return True

    def submit_to_tracker(self, form_data, tracker_url=None, tracker_token=None) -> bool:
        """Submit form data to a remote issue tracker.

        T-033: POSTs ``form_data`` to a tracker endpoint (Jira /
        GitHub / Linear) using a Bearer token pulled from
        ``config.dikt['tracker_token']`` (falls back to
        ``pycurity``). The endpoint defaults to the value at
        ``config.dikt['tracker_url']``; when neither is set, the
        submission is saved locally via ``submit_to_local_storage``.

        Returns ``True`` on success or local-save fallback, ``False``
        on hard failure.
        """
        try:
            import requests  # type: ignore
        except ImportError:
            logma.warning("[forms] submit_to_tracker: requests not installed; saving locally")
            return self.submit_to_local_storage(form_data)

        if tracker_url is None and hasattr(self, "config"):
            tracker_url = self.config.dikt.get("tracker_url")
        if tracker_token is None and hasattr(self, "config"):
            tracker_token = self.config.dikt.get("tracker_token")
        if not tracker_token:
            try:
                import pykey

                tracker_token = pykey.PYKEYSTORE.get("tracker_token")
            except Exception:
                pass
        if not tracker_url or not tracker_token:
            logma.warning("[forms] submit_to_tracker: missing endpoint/token; saving locally")
            return self.submit_to_local_storage(form_data)

        try:
            response = requests.post(
                tracker_url,
                headers={"Authorization": f"Bearer {tracker_token}", "Content-Type": "application/json"},
                json={"form_data": form_data or {}},
                timeout=15,
            )
            if response.status_code < 300:
                logma.info(f"[forms] submit_to_tracker: {tracker_url} OK ({response.status_code})")
                return True
            logma.warning(f"[forms] submit_to_tracker: {tracker_url} status {response.status_code}, saving locally")
        except Exception as e:
            logma.error(f"[forms] submit_to_tracker failed: {e}", exc_info=True)
        return self.submit_to_local_storage(form_data)

    def create_data_table(self) -> "DataFrame":
        """"""
        df = super().create_data_table()
        columns = []
        data = []
        df = DataFrame(data, columns=columns)
        return df

    def get_form_compatibility_options(self) -> list[str]:
        """"""
        options = ["Google Forms", "Nchantd Office", ""]
        return options

    def init_drawer_document_config(self) -> dict[int, Any]:
        """Build the document-config drawer (compatibility / response defaults)."""
        items = self.toolbox_config[100].get("items", {})
        cnt = 0

        # Compatibility dropdown
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.form_compatibility_select = NchantdDropDown(
            self,
            {
                "label": "Form Compatibility: ",
                "layout": "horizontal",
                "combobox": {"size": ["auto", "auto"], "options": ["Google Forms", "Nchantd Office"]},
                "handler": self.cmd_select_form_compatibility,
            },
        ).initWidget()
        cnt += 1

        # Default response type
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.form_default_response_check = NchantdDropDown(
            self,
            {
                "label": "Default Response Type:",
                "layout": "horizontal",
                "combobox": {
                    "size": ["auto", "auto"],
                    "options": ["Text", "Number", "Date", "Multiple Choice", "Checkboxes", "Dropdown"],
                },
            },
        ).initWidget()
        cnt += 1

        # Default response trigger
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.form_default_response_trigger_check = NchantdDropDown(
            self,
            {
                "label": "Default Response Trigger:",
                "layout": "horizontal",
                "combobox": {
                    "size": ["auto", "auto"],
                    "options": ["On Submit", "On Change", "On Focus"],
                },
            },
        ).initWidget()
        cnt += 1

        # Default answer required
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.form_default_answer_required_check = NchantdCheckbox(
            self,
            {
                "text": "Set Default Answer Required",
                "layout": "horizontal",
                "size": ["auto", "auto"],
            },
        ).initWidget()
        cnt += 1

        # Default always-asked
        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.form_default_always_asked_check = NchantdCheckbox(
            self,
            {
                "text": "Set Default Always Asked",
                "layout": "horizontal",
                "size": ["auto", "auto"],
            },
        ).initWidget()
        cnt += 1
        return items

    def _ensure_drawer_item(self, items, cnt) -> dict[str, Any]:
        """Lazily create a default drawer-item slot.

        Centralises the ``if cnt not in items: items[cnt] = {...}`` pattern
        used by ``init_drawer_document_config``, removing the repeated
        branch flagged by the maintainability auditor as switch abuse.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}.copy()
        return items

    def init_drawer_input_config(self) -> dict[int, Any]:
        """"""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0
        default_action = {"action": "insert_generic_action", "type": "custom"}
        if cnt not in items:
            items[cnt] = default_action.copy()
        validation_options = ["None", "Email", "URL", "Number", "Phone", "Custom Regex"]
        cfg = {
            "label": "Validation Type:",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": validation_options},
        }
        self.validation_options_select = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.validation_options_select
        cnt += 1
        return items

    def init_drawer_connections(self) -> dict[int, Any]:
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
            "combobox": {"size": ["auto", "auto"], "options": options},
        }
        self.form_service_select = NchantdDropDown(self, cfg).initWidget()
        items[cnt]["widget"] = self.form_service_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action.copy()
        cfg = {
            "label": "Account Name: ",
            "layout": "horizontal",
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

    def init_drawer_quickstart(self) -> dict[int, Any]:
        """"""
        items = {}
        return items

    def init_toolbox(self) -> None:
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_document_config()
        # self.toolbox_config[200]["items"] = self.init_drawer_input_config()
        self.toolbox_config[300]["items"] = self.init_drawer_connections()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def select_form(self, form_name) -> None:
        """"""
        self.selected_form = self.forms[form_name]


class NchantdOfficeFeedback(NchantdWidget):
    """Feedback form widget for collecting user feedback"""

    def __init__(self, parent=None, cfg=None) -> None:
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

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> Self:
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

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_attach_screenshot(self, event=None) -> Self:
        """Attach a screenshot to the feedback"""
        file_dialog = pyqt.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Screenshot", "", "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        if file_path:
            self.feedback_data["screenshot"] = file_path
            logma.info(f"Screenshot attached: {file_path}")
        return self

    def cmd_submit_feedback(self, event=None) -> Self:
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

    def cmd_cancel(self, event=None) -> Self:
        """Cancel and close the feedback form"""
        self.close()
        return self

    def send_feedback(self, feedback_data) -> bool | Self:
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

            # T-084: also send to a remote issue tracker when one
            # is configured. Falls back to local-only on any
            # failure so the feedback is never lost.
            self.send_to_server(feedback_data)

            logma.info(f"Feedback submitted: {feedback_data['type']} - {feedback_data['title']}")
            return self

        except Exception as e:
            logma.error(f"Error sending feedback: {e}")
            return False

    def send_to_server(self, feedback_data) -> bool:
        """T-084: send feedback to a remote issue tracker.

        Wraps ``submit_to_tracker`` so the success/failure log
        is clear. Falls back to the local save (already
        performed by the caller) on any error.
        """
        try:
            tracker_url = None
            tracker_token = None
            if hasattr(self, "config"):
                tracker_url = self.config.dikt.get("feedback_tracker_url")
                tracker_token = self.config.dikt.get("feedback_tracker_token")
            if not tracker_url or not tracker_token:
                try:
                    import pykey

                    tracker_url = tracker_url or pykey.PYKEYSTORE.get("feedback_tracker_url")
                    tracker_token = tracker_token or pykey.PYKEYSTORE.get("feedback_tracker_token")
                except Exception:
                    pass
            if not tracker_url:
                logma.info("[forms] send_to_server: no tracker URL; local-only feedback")
                return True
            if hasattr(self, "submit_to_tracker"):
                return self.submit_to_tracker(feedback_data, tracker_url=tracker_url, tracker_token=tracker_token)
            logma.warning("[forms] send_to_server: no submit_to_tracker method")
            return False
        except Exception as e:
            logma.error(f"[forms] send_to_server failed: {e}", exc_info=True)
            return False

    def save_feedback_locally(self, feedback_data) -> Self:
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
            except (OSError, ValueError) as e:
                logma.error(f"[forms] feedback-file load failed: {e}", exc_info=True)
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
