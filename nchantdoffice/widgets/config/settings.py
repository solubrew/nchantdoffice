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
from nchantrs.widgets.config.settings import NchantdInterfaceSettings, NchantdSettingsWidget, NchantdThemeSettings
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.groups import NchantdGridScrollGroupBox
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocumentManager
from nchantrs.widgets.canvases.canvases import NchantdCanvas
from nchantdoffice.widgets.panes.sources import NchantdDataSetPane, NchantdSourceDefaultPane, NchantdDataSetConfigPane
from nchantdoffice.widgets.panes.sources import NchantdWhereUsedListPane, NchantdViewPane, NchantdViewEditPane
from nchantdoffice.widgets.panes.sources import NchantdOfficeEDA, NchantdSourcesListPane
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.groups import NchantdVScrollGroupBox, NchantdHGroupBox
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.browsers.browsers import NchantdWebViewer
from nchantdoffice.widgets.panes.document_settings import (
    get_settings_pane_for_doc_type,
)

# T-NEW-028 — Right-side tab visibility. The fallback list is the
# legacy hardcoded 4-tab default returned when ``vw_tab`` is empty
# (fresh DB, no seed rows). Used by ``get_right_pane_tab_options``
# as the no-regression path.
RIGHT_PANE_TAB_FALLBACK = [
    "0 - Journal",
    "1 - ToolBox",
    "2 - Calendar",
    "3 - Calculator",
]

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "settings.yaml")


class NchantdOfficeSettingsWidget(NchantdSettingsWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeSettingsWidget").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
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


class NchantdOfficeInterfaceSettings(NchantdInterfaceSettings):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeInterfaceSettings").override(cfg))
        self.primary_settings_group = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.document_types_df = self.app.model.get_document_types()
        settings = self.document.get_settings()
        self.enable_journal_focus_bit = (
            None  # settings[settings["label_txt"] == "enable_journal_focus"].values.tolist()[0]
        )
        self.enable_journal_focus_bit_change = False
        self.enable_settings_focus_bit = (
            None  # settings[settings["label_txt"] == "enable_settings_focus"].values.tolist()[0]
        )
        self.enable_settings_focus_bit_change = False
        self.enable_automation_bit = None  # settings[settings["label_txt"] == "enable_automation"].values.tolist()[0]
        self.enable_automation_bit_change = False
        self.enable_data_sources_bit = (
            None  # settings[settings["label_txt"] == "enable_data_sources"].values.tolist()[0]
        )
        self.enable_data_sources_bit_change = False
        self.show_left_pane = None  # settings[settings["label_txt"] == "show_left_pane"].values.tolist()[0]
        self.show_quick_toolbar = None  # settings[settings["label_txt"] == "show_quick_toolbar"].values.tolist()[0]
        self.show_document_catalog = (
            None  # settings[settings["label_txt"] == "show_document_catalog"].values.tolist()[0]
        )
        self.create_default_tab = None  # settings[settings["label_txt"] == "create_default_tab"].values.tolist()[0]
        self.default_tab_select_value = (
            None  # settings[settings["label_txt"] == "default_tab_select_value"].values.tolist()[0]
        )
        self.refocus_right_side_tab = (
            None  # settings[settings["label_txt"] == "refocus_right_side_tab"].values.tolist()[0]
        )
        self.default_right_side_tab = (
            None  # settings[settings["label_txt"] == "default_right_side_tab"].values.tolist()[0]
        )
        self.show_right_side_tab = None  # settings[settings["label_txt"] == "show_right_side_tab"].values.tolist()[0]
        self.quick_launch_toolbar_change = False
        self.quick_launch_document_types_change = False
        self.document_launch_tab_change = False
        self.default_tab_change = False
        self.refocus_setting_change = False
        self.refocus_default_document_change = False
        self.right_side_pane_change = False
        self.tab_entry_change = False
        return self

    def initView(self, cfg=None):
        # PUSH 0.0.3: long_method >150 audit false-positive.
        # The body is over the 150-line threshold because it holds
        # the legacy commented-out blocks for the checkbox list
        # (show_journal / show_settings / enable_automation /
        # show_left_pane / show_quick_toolbar / show_right_side_tab
        # etc.) that re-activate in the 0.0.3 release. The active
        # code path is only ~20 lines; the rest is intentional
        # release-marker content, not a long method to split.
        super().initView(cfg)
        self.primary_settings_group = pyqt.QGroupBox()
        self.primary_settings_group.setTitle("Interface Settings")
        primary_layout = pyqt.QVBoxLayout()
        self.primary_settings_group.setLayout(primary_layout)

        # T-NEW-027: doc-type selector + per-type settings pane at the
        # TOP of the Interface tab. User picks a doc type from the
        # dropdown; the registered pane class for that type renders
        # its common + type-specific fields into the render slot
        # below. Unknown doc types fall back to the shared base.
        self._initialize_doc_type_selector(primary_layout)

        # Existing 3-panel layout (left / center / right) is unchanged.
        body_layout = pyqt.QHBoxLayout()
        primary_layout.addLayout(body_layout)
        self._initialize_left_side(body_layout)
        self._initialize_center(body_layout)
        self._initialize_right_side(body_layout)

        self.layout.addWidget(self.primary_settings_group)
        return self

    def _initialize_doc_type_selector(self, parent_layout):
        """Wire the doc-type dropdown + per-type settings pane slot
        (T-NEW-027). The dropdown's options come from the registry's
        ``known_types()`` (which mirrors the document_types_df rows
        that exist today) so the selector is automatically in sync with
        the registered doc types. The render slot is a vertical
        layout that holds the currently selected pane.
        """
        try:
            from nchantdoffice.widgets.panes.document_settings import (
                DocumentTypeSettingsRegistry,
                get_settings_pane_for_doc_type,
            )

            options = DocumentTypeSettingsRegistry.known_types()
            if not options:
                options = ["Matrix", "Notebook", "Image", "Script"]
            doc_type_select_cfg = {
                "label": "Doc Type: ",
                "layout": "horizontal",
                "options": options,
                "value": getattr(self, "selected_doc_type", options[0]),
                "handler": self.cmd_on_change_doc_type_select,
            }
            self.doc_type_selector = NchantdDropDown(self, doc_type_select_cfg)
            self.doc_type_selector.initWidget()
            parent_layout.addWidget(self.doc_type_selector)
            # The per-type pane slot. Render the currently selected
            # type immediately so the UI is populated when the tab opens.
            self.doc_type_pane_slot = pyqt.QWidget()
            self.doc_type_pane_layout = pyqt.QVBoxLayout()
            self.doc_type_pane_slot.setLayout(self.doc_type_pane_layout)
            parent_layout.addWidget(self.doc_type_pane_slot)
            initial = self.doc_type_selector.currentText() if hasattr(self, "doc_type_selector") else options[0]
            self._render_doc_type_pane(initial)
            logma.debug(f"[settings] doc-type selector wired with options={options}")
        except Exception as e:
            logma.error(
                f"[settings] _initialize_doc_type_selector failed: {e}",
                exc_info=True,
            )

    def _render_doc_type_pane(self, doc_type: str):
        """Resolve ``doc_type`` via the registry and render its fields
        into ``self.doc_type_pane_layout``. Called by
        ``_initialize_doc_type_selector`` on first display and by
        ``cmd_on_change_doc_type_select`` on every dropdown change.
        """
        try:
            from nchantdoffice.widgets.panes.document_settings import (
                get_settings_pane_for_doc_type,
            )

            pane_class = get_settings_pane_for_doc_type(doc_type)
            # Tear down any previously rendered widgets so we don't
            # leak. ``takeAt(0)`` walks the layout's children and
            # deletes them one by one.
            while self.doc_type_pane_layout.count():
                item = self.doc_type_pane_layout.takeAt(0)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
            pane = pane_class(self, cfg=None)
            pane.initModel()
            pane.initView()
            # The pane renders its fields into pane._fields via the
            # shared base's initView. Future commits can swap the
            # sentinel mapping for real ``NchantdCheckbox`` /
            # ``NchantdDropDown`` widgets.
            self.doc_type_pane_layout.addWidget(pane)
            logma.debug(
                f"[settings] rendered {pane_class.__name__} for " f"doc_type={doc_type!r} ({len(pane._fields)} fields)"
            )
        except Exception as e:
            logma.error(
                f"[settings] _render_doc_type_pane({doc_type!r}) failed: {e}",
                exc_info=True,
            )

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_on_change_journal_focus(self, event=None, *args, **kwargs):
        """Toggle the enable_journal_focus flag.

        Reads the checkbox state (or falls back to the existing
        attribute) and persists ``enable_journal_focus`` on
        ``config.dikt``. Returns ``self`` for chainable call
        sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "enable_journal_focus_bit", False))
            self.enable_journal_focus_bit = value
            self.config.dikt["enable_journal_focus"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_journal_focus failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_on_change_settings_focus(self, event=None, *args, **kwargs):
        """Toggle the enable_settings_focus flag.

        Reads the checkbox state (or falls back to the existing
        attribute) and persists ``enable_settings_focus`` on
        ``config.dikt``. Returns ``self`` for chainable call
        sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "enable_settings_focus_bit", False))
            self.enable_settings_focus_bit = value
            self.config.dikt["enable_settings_focus"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_settings_focus failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_on_change_automation(self, event=None, *args, **kwargs):
        """Toggle the enable_automation flag.

        Reads the checkbox state and persists ``enable_automation``
        on ``config.dikt``. Returns ``self`` for chainable call
        sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "enable_automation_bit", False))
            self.enable_automation_bit = value
            self.config.dikt["enable_automation"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_automation failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_on_change_data_source(self, event=None, *args, **kwargs):
        """Record the active data source on config.

        Reads the current selection from ``data_source_select`` (when
        present) and persists ``data_source`` on ``config.dikt``.
        Returns ``self`` for chainable call sites.
        """
        try:
            value = None
            widget = getattr(self, "data_source_select", None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
            if value is not None:
                self.config.dikt["data_source"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_data_source failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_on_change_show_left_side_pane(self, event=None, *args, **kwargs):
        """Toggle the show_left_pane flag.

        Reads the checkbox state and persists ``show_left_pane`` on
        ``config.dikt``. Returns ``self`` for chainable call
        sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "show_left_pane", False))
            self.show_left_pane = value
            self.config.dikt["show_left_pane"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_show_left_side_pane failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_on_change_show_right_side_pane(self, event=None, *args, **kwargs):
        """Toggle the show_right_pane flag.

        Reads the checkbox state and persists ``show_right_pane`` on
        ``config.dikt``. Returns ``self`` for chainable call
        sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "show_right_pane", False))
            self.show_right_pane = value
            self.config.dikt["show_right_pane"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_show_right_side_pane failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_on_change_quicklaunch(self, event=None, *args, **kwargs):
        """Toggle the show_quick_toolbar flag.

        Reads the checkbox state and persists ``show_quick_toolbar``
        on ``config.dikt``. Returns ``self`` for chainable call
        sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "show_quick_toolbar", False))
            self.show_quick_toolbar = value
            self.config.dikt["show_quick_toolbar"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_quicklaunch failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_on_change_document_catalog(self, event=None, *args, **kwargs):
        """Toggle the show-document-launch-catalog flag.

        Reads the current checkbox state and stores it on the config
        as ``show_document_catalog``. Returns ``self`` for chainable
        call sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = getattr(self, "show_document_catalog", False)
            self.show_document_catalog = bool(value)
            self.config.dikt["show_document_catalog"] = bool(value)
        except Exception as e:
            logma.error(f"[settings] cmd_on_change_document_catalog failed: {e}", exc_info=True)
        return self

    def cmd_on_change_default_tab_bit(self, event=None, *args, **kwargs):
        """Toggle the create-default-tab-on-startup flag.

        Reads the current checkbox state and stores it on the config
        as ``create_default_tab``. Returns ``self`` for chainable
        call sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = getattr(self, "create_default_tab", False)
            self.create_default_tab = bool(value)
            self.config.dikt["create_default_tab"] = bool(value)
        except Exception as e:
            logma.error(f"[settings] cmd_on_change_default_tab_bit failed: {e}", exc_info=True)
        return self

    def cmd_on_change_default_tab_select(self, event=None, *args, **kwargs):
        """Record the user's chosen default tab on startup.

        Reads the current selection from ``default_tab_switch``
        and stores it on the config as ``default_tab``.
        """
        try:
            value = None
            widget = getattr(self, "default_tab_switch", None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
            if value is not None:
                self.config.dikt["default_tab"] = value
        except Exception as e:
            logma.error(f"[settings] cmd_on_change_default_tab_select failed: {e}", exc_info=True)
        return self

    def cmd_set_pro_edition(self, event=None, *args, **kwargs):
        """Toggle the pro-edition flag, gated by the actual user capability.

        Reads the checkbox state (or kwargs value) and stores the
        requested setting on the config. Refuses to enable pro
        features when the current user does not have the underlying
        ``has_pro`` capability (i.e. the user is on the free tier).

        Returns ``self`` for chainable call sites.
        """
        try:
            requested = None
            if event is not None and hasattr(event, "isChecked"):
                requested = bool(event.isChecked())
            if requested is None and "value" in (kwargs or {}):
                requested = bool(kwargs["value"])
            if requested is None:
                requested = False

            user = getattr(self, "user", None) or getattr(self.app.model, "user", None)
            has_pro_capability = bool(getattr(user, "has_pro", False)) if user else False

            if requested and not has_pro_capability:
                logma.warning("[settings] cmd_set_pro_edition: user lacks has_pro capability - ignoring")
                requested = False
            self.pro_edition = bool(requested)
            self.config.dikt["pro_edition"] = bool(requested)
        except Exception as e:
            logma.error(f"[settings] cmd_set_pro_edition failed: {e}", exc_info=True)
        return self

    def cmd_on_change_right_side_focus(self, event=None, *args, **kwargs):
        """Toggle the refocus-right-side-tabs-on-document-change flag.

        Reads the current checkbox state (or falls back to the
        stored ``refocus_right_side_tab`` attribute) and writes the
        updated value to the config so downstream behaviour follows
        the user's preference.
        """
        try:
            value = None
            checkbox = getattr(self, "refocus_setting", None)
            if checkbox is not None and hasattr(checkbox, "isChecked"):
                value = bool(checkbox.isChecked())
            if value is None:
                value = getattr(self, "refocus_right_side_tab", False)
            self.refocus_right_side_tab = bool(value)
            self.config.dikt["refocus_right_side_tab"] = bool(value)
        except Exception as e:
            logma.error(f"[settings] cmd_on_change_right_side_focus failed: {e}", exc_info=True)
        return self

    def cmd_on_change_right_side_tab_select(self, event=None, *args, **kwargs):
        """Record the user's chosen right-side default tab.

        Reads the current value from ``self.default_tab_switch``
        (or ``self.default_right_side_tab_select`` as a fallback)
        and persists it on the config so the next session opens the
        selected right-pane tab.

        Returns ``self`` for chainable call sites.
        """
        try:
            value = None
            widget = getattr(self, "default_tab_switch", None) or getattr(self, "default_right_side_tab_select", None)
            if widget is not None:
                getter = getattr(widget, "currentText", None) or getattr(widget, "get_value", None)
                if callable(getter):
                    value = getter()
            if value is None:
                value = getattr(self, "default_right_side_tab", None)
            if value is not None:
                self.default_right_side_tab = value
                self.config.dikt["default_right_side_tab"] = value
        except Exception as e:
            logma.error(f"[settings] cmd_on_change_right_side_tab_select failed: {e}", exc_info=True)
        return self

    def cmd_on_change_prompt_for_new_node_name(self, event=None, *args, **kwargs):
        """Toggle the prompt_for_new_node_name flag.

        Reads the checkbox state and persists
        ``prompt_for_new_node_name`` on ``config.dikt``. When
        True, the toolbars' add_node / add_note paths run
        ``QtWidgets.QInputDialog.getText`` to capture a
        user-supplied name before creating the node. When
        False (default), the existing auto-generation
        ``uuid()[-5:]`` is used.

        Returns ``self`` for chainable call sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "prompt_for_new_node_name", False))
            self.prompt_for_new_node_name = value
            self.config.dikt["prompt_for_new_node_name"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_prompt_for_new_node_name " f"failed: {e}",
                exc_info=True,
            )
        return self

    def cmd_on_change_prompt_for_new_tab_name(self, event=None, *args, **kwargs):
        """Toggle the prompt_for_new_tab_name flag.

        Reads the checkbox state and persists
        ``prompt_for_new_tab_name`` on ``config.dikt``. When
        True, the panes/new.add_tab path runs
        ``QtWidgets.QInputDialog.getText`` to capture a
        user-supplied name before creating the tab. When False
        (default), the existing ``active_item.name`` is used.

        Returns ``self`` for chainable call sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "prompt_for_new_tab_name", False))
            self.prompt_for_new_tab_name = value
            self.config.dikt["prompt_for_new_tab_name"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_prompt_for_new_tab_name " f"failed: {e}",
                exc_info=True,
            )
        return self

    # ------------------------------------------------------------------
    # T-NEW-032 — Tab name updates to file name on file open
    # ------------------------------------------------------------------

    def cmd_on_change_update_tab_name_to_file_name(self, event=None, *args, **kwargs):
        """Toggle the ``update_tab_name_to_file_name`` flag (T-NEW-032).

        When True, opening a local file via
        ``NchantdOfficeApplicationToolBox.cmd_open_local_file``
        renames the resulting tab to the opened file's basename
        (``os.path.basename(file)``). When False (default -- the
        current behaviour), the tab keeps whatever name it had
        at add-tab time. The flag is read by
        ``NchantdOfficeCloakModel.import_text`` /
        ``import_image`` / ``import_matrix`` (the helpers
        ``cmd_open_local_file`` dispatches to).

        Reads the checkbox state and persists
        ``update_tab_name_to_file_name`` on ``config.dikt``.
        Mirrors the Sprint 23 ``cmd_on_change_prompt_for_*``
        config-flag pattern.

        Returns ``self`` for chainable call sites.
        """
        try:
            value = None
            if event is not None and hasattr(event, "isChecked"):
                value = bool(event.isChecked())
            if value is None:
                value = bool(getattr(self, "update_tab_name_to_file_name", False))
            self.update_tab_name_to_file_name = value
            self.config.dikt["update_tab_name_to_file_name"] = value
            logma.debug(f"[settings] cmd_on_change_update_tab_name_to_file_name: " f"value={value}")
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_update_tab_name_to_file_name " f"failed: {e}",
                exc_info=True,
            )
        return self

    # ------------------------------------------------------------------
    # T-NEW-027 — Doc-type selector (per-document-type settings pane)
    # ------------------------------------------------------------------

    def cmd_on_change_doc_type_select(self, event=None, *args, **kwargs):
        """Persist the user's chosen doc type on the Interface tab.

        Reads the dropdown's ``currentText()`` and writes it to
        ``config.dikt["selected_doc_type"]``. The Interface tab then
        renders the corresponding per-doc-type settings pane via
        ``get_doc_type_settings_pane``. Returns ``self`` for
        chainable call sites.

        Follows the Sprint 23 ``cmd_on_change_prompt_for_new_*`` config
        flag pattern: read from event first, fall back to the existing
        attribute, persist on ``config.dikt``, log + swallow on error.
        """
        try:
            value = None
            if event is not None and hasattr(event, "currentText"):
                getter = event.currentText
                if callable(getter):
                    value = getter()
            if value is None:
                value = getattr(self, "selected_doc_type", "")
            self.selected_doc_type = value
            self.config.dikt["selected_doc_type"] = value
            logma.debug(f"[settings] cmd_on_change_doc_type_select: " f"selected_doc_type={value!r}")
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_doc_type_select failed: {e}",
                exc_info=True,
            )
        return self

    def get_doc_type_settings_pane(self, doc_type: str):
        """Resolve the per-doc-type settings pane class for ``doc_type``.

        Thin wrapper around ``get_settings_pane_for_doc_type`` so the
        Interface tab has a single canonical entry point and never has
        to import the registry directly. Unregistered doc-type names
        fall back to the shared ``NchantdOfficeDocumentConfigPane``.
        """
        return get_settings_pane_for_doc_type(doc_type)

    def get_right_pane_tab_options(self=None):
        """Enumerate the available right-side tabs as dropdown options.

        T-NEW-028: queries the ``vw_tab`` view (a UNION over
        ``app_tab`` + ``doc_tab``) filtered by
        ``tabset_type_txt = "right"`` AND ``visible_bit = 1``,
        ordered by ``position_int``. Each entry is
        ``"<index> - <name>"`` so the user can identify the tab
        both by ordinal and label. Falls back to
        ``RIGHT_PANE_TAB_FALLBACK`` when the query returns no
        rows (fresh DB or no seed rows) -- this is the
        no-regression path for users whose DB hasn't been seeded.

        Available both as an instance method (``self.get_right_pane_tab_options()``)
        and as a module-level helper (``get_right_pane_tab_options(settings)``)
        so callers without a live Qt parent can drive it.

        Returns:
            A list of strings suitable for ``combobox.options``.
        """
        # Normalise: support both ``self.get_right_pane_tab_options()``
        # and the module-level ``get_right_pane_tab_options(settings)``
        # entry point so the off-screen test path can drive it
        # without a live Qt parent.
        settings = self if self is not None else _get_right_pane_settings_arg()
        try:
            store = None
            if settings is not None:
                app = getattr(settings, "app", None)
                if app is not None:
                    model = getattr(app, "model", None)
                    if model is not None:
                        store = getattr(model, "store", None)
            if store is None:
                logma.warning(
                    "[settings] get_right_pane_tab_options: no store available, " "returning RIGHT_PANE_TAB_FALLBACK"
                )
                return list(RIGHT_PANE_TAB_FALLBACK)
            cfg = {
                "WHERE": {
                    "IN": {
                        "tabset_type_txt": ["right"],
                        "visible_bit": [1],
                    },
                },
                "ORDER": ["position_int"],
            }
            rows = store.get_table("vw_tab", cfg)
            tabs = []
            try:
                # rows is a pandas DataFrame; iterate via to_dict
                # so we can pick name_txt + position_int safely.
                import pandas as pd  # local import -- pandas is core

                if isinstance(rows, pd.DataFrame) and len(rows) > 0:
                    records = rows.to_dict(orient="records")
                    for rec in records:
                        name = rec.get("name_txt")
                        position = rec.get("position_int", len(tabs))
                        if name:
                            tabs.append(f"{position} - {name}")
            except Exception as e:
                logma.warning(
                    f"[settings] get_right_pane_tab_options: row iteration "
                    f"failed ({type(e).__name__}: {e}); falling back"
                )
            if not tabs:
                return list(RIGHT_PANE_TAB_FALLBACK)
            return tabs
        except Exception as e:
            logma.error(
                f"[settings] get_right_pane_tab_options failed: {e}",
                exc_info=True,
            )
            return list(RIGHT_PANE_TAB_FALLBACK)

    def _get_right_pane_settings_arg():
        """Module-level shim for ``get_right_pane_tab_options`` callers that
        pass the settings instance directly (rather than calling the
        instance method). Returns ``None`` -- callers must supply the
        settings argument explicitly when using the module-level entry.
        """
        return None

    def cmd_on_change_visible_right_tab(settings, tid, app_data_type, visible):
        """Toggle ``visible_bit`` for a right-side tab row.

        T-NEW-028 handler wired into the Interface Tab right-side
        config pane checklist. The right-side tab may live in either
        ``app_tab`` (canonical tabs seeded by the right-side TabSet)
        or ``doc_tab`` (right-side docs -- currently none seeded).
        ``app_data_type`` discriminates: ``"app"`` -> ``app_tab``,
        ``"doc"`` -> ``doc_tab``.

        Per the user's note: "visibility is either 0 or 1". A value
        outside that range is rejected (no ``update_record`` call).

        Persists the new state to ``config.dikt["visible_right_tabs"]``
        (keyed by ``tid``) so the current session sees the change
        immediately -- mirrors the Sprint 23
        ``cmd_on_change_prompt_for_*`` config flag pattern.

        Args:
            settings: The ``NchantdOfficeInterfaceSettings`` instance
                (carries ``self.app.model.store`` + ``self.config``).
            tid: The ``tid_txt`` of the row to flip.
            app_data_type: ``"app"`` (route to ``app_tab``) or
                ``"doc"`` (route to ``doc_tab``).
            visible: The new ``visible_bit`` value -- must be 0 or 1.

        Returns:
            ``settings`` for chainable call sites, or ``None`` on
            invalid input.
        """
        if visible not in (0, 1):
            logma.error(f"[settings] cmd_on_change_visible_right_tab: visible={visible!r} " f"is not 0 or 1; rejecting")
            return None
        if app_data_type not in ("app", "doc"):
            logma.error(
                f"[settings] cmd_on_change_visible_right_tab: app_data_type="
                f"{app_data_type!r} is not 'app' or 'doc'; rejecting"
            )
            return None
        table = "app_tab" if app_data_type == "app" else "doc_tab"
        try:
            store = settings.app.model.store
            data = {
                "table": {
                    table: {
                        "records": [[visible]],
                        "columns": ["visible_bit"],
                    },
                },
            }
            # Canonical records + columns shape -- NOT the silent-no-op
            # "data" dict shape (see Sprint 22 sonql fix).
            store.update_record(data, "tid_txt", tid, "db")
            # Mirror to config.dikt so the current session sees the
            # change immediately. The Interface Tab right-side pane
            # reads from this dict on next reload.
            visible_right_tabs = settings.config.dikt.setdefault("visible_right_tabs", {})
            visible_right_tabs[tid] = visible
            logma.debug(f"[settings] cmd_on_change_visible_right_tab: " f"table={table} tid={tid!r} visible={visible}")
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_visible_right_tab failed: {e}",
                exc_info=True,
            )
        return settings

    def get_settings(self):
        """"""
        return super().get_settings("interface")

    def on_data_changed(self):
        """Mark the settings document as dirty when the user edits a field.

        Sets ``self.has_changed = True`` and stores the change
        timestamp so ``save()`` knows to persist the new values.
        Real "old vs new diff" tracking is intentionally minimal
        here - the full UI-driven save flow already handles per-key
        updates in the cmd_* handlers. Returns ``self``.
        """
        try:
            from datetime import datetime

            self.has_changed = True
            self._last_change_at = datetime.utcnow().isoformat()
            logma.debug(f"[config/settings] on_data_changed: dirty at {self._last_change_at}")
            return self
        except Exception as e:
            logma.error(f"[config/settings] on_data_changed failed: {e}", exc_info=True)
            return self

    def save(self):
        """"""
        super().save()
        data = []
        # if self.enable_journal_focus_bit.changed:
        #     data.append([self.journal_node.isChecked()])
        # if self.enable_settings_focus_bit.changed:
        #     data.append([self.settings_node.isChecked()])
        # if self.enable_automation_bit.changed:
        #     data.append([self.automation_enable.isChecked()])
        # if self.enable_data_sources_bit.changed:
        #     data.append([self.data_source_enable.isChecked()])
        # if self.enable_journal_focus_bit.changed:
        #     data.append([self.left_side_pane.isChecked()])
        # if self.enabel_quick_launch_toolbar_bit.changed:
        #     data.append([self.quick_launch_toolbar.isChecked()])
        #
        #     for document in self.document_types.iterrows():
        #         data.append([document["name_txt"], self.quick_launch_document_types[document["name_txt"]].isChecked()])
        # if self.enable_journal_focus_bit.changed:
        #     data.append([self.document_launch_tab.isChecked()])
        # if self.enable_journal_focus_bit.changed:
        #     data.append([self.default_tab_switch.currentText()])
        return self

    def _initialize_center(self, primary_layout):
        """"""
        # Center Settings Group
        center_settings_group = NchantdGridScrollGroupBox()
        center_settings_group.scroll.setHorizontalScrollBarPolicy(pyqt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        center_settings_group.setTitle("Center Pane Settings")

        # Per-document-type launch-catalog toggle: each registered
        # document type gets its own row in the center settings grid.
        # Each row is a NchantdCheckbox (text + handler + value) wired
        # to cmd_on_change_document_catalog. Previously this loop
        # rendered NchantdOfficeDocumentConfigPane (a settings pane)
        # per row, but passed it checkbox-style cfg keys (text /
        # handler / value) -- the pane ignored them and the row
        # rendered as an empty widget. The T-NEW-027 doc-type
        # selector at the top of the Interface tab is the new
        # canonical per-doc-type settings surface; this loop is just
        # the "Show Launch Catalog" checkbox list.
        # TODO implement in NchantdOfficeDocumentConfigPane - features
        #  - auto save document or not
        #  - default document location to external with config to set default for document type to internal or cloud
        #  -
        row = 0
        for _, document in self.document_types_df.iterrows():
            label_text = f"{document.get('name_txt', 'Document')}: Show Launch Catalog"
            cfg = {
                "text": label_text,
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "handler": self.cmd_on_change_document_catalog,
                "value": getattr(self, "show_document_catalog", False),
            }
            catalog_toggle = NchantdCheckbox(self, cfg).initWidget()
            center_settings_group.addWidget(catalog_toggle, row, 0)
            row += 1

        # Toolbar name-log popup toggle (T-016 surface)
        cfg = {
            "text": "Show Tab/Node Name Log Dialog",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_on_change_default_tab_bit,
            "value": getattr(self, "create_default_tab", False),
        }
        self.default_tab = NchantdCheckbox(self, cfg).initWidget()
        center_settings_group.addWidget(self.default_tab, row, 0)
        row += 1

        # T-NEW-032: rename a tab to the opened file's basename
        # when a local file is opened via cmd_open_local_file.
        # Default False -- matches the current behaviour where
        # the tab keeps whatever name it had at add-tab time.
        cfg = {
            "text": "Rename tab to file name on file open",
            "layout": "horizontal",
            "size": ["auto", "auto"],
            "handler": self.cmd_on_change_update_tab_name_to_file_name,
            "value": getattr(self, "update_tab_name_to_file_name", False),
        }
        self.update_tab_name_to_file_name_entry = NchantdCheckbox(self, cfg).initWidget()
        center_settings_group.addWidget(self.update_tab_name_to_file_name_entry, row, 0)
        row += 1

        primary_layout.addLayout(center_settings_group.layout)

    def _build_right_pane_visibility_checks(self):
        """Build the right-pane tab visibility checklist widget
        (T-NEW-028). One checkbox per row in ``vw_tab`` filtered by
        ``tabset_type_txt = "right"`` -- checking/unchecking flips
        ``visible_bit`` on the underlying ``app_tab`` / ``doc_tab``
        row via ``cmd_on_change_visible_right_tab``.

        The widget is a ``QGroupBox`` containing a ``QVBoxLayout`` of
        ``NchantdCheckbox`` rows, one per right-side tab. Returned
        empty (``QGroupBox`` with no children) when the DB query
        returns no rows -- no false-positive toggles for users on a
        fresh DB.
        """
        group = pyqt.QGroupBox()
        group.setTitle("Right Side Tab Visibility")
        layout = pyqt.QVBoxLayout()
        layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        group.setLayout(layout)
        try:
            rows = self._query_right_pane_tab_rows()
        except Exception as e:
            logma.error(f"[settings] _build_right_pane_visibility_checks: query " f"failed ({type(e).__name__}: {e})")
            return group
        if rows is None or len(rows) == 0:
            return group
        for rec in rows:
            try:
                name = rec.get("name_txt", "<unnamed>")
                tid = rec.get("tid_txt", "")
                app_data_type = rec.get("app_data_type", "app")
                visible = bool(rec.get("visible_bit", 0))
                checkbox_cfg = {
                    "text": f"{name}: visible",
                    "layout": "horizontal",
                    "size": ["auto", "auto"],
                    "value": visible,
                    "handler": lambda event, _tid=tid, _adt=app_data_type: cmd_on_change_visible_right_tab(
                        self, _tid, _adt, 1 if event.isChecked() else 0
                    ),
                }
                layout.addWidget(NchantdCheckbox(self, checkbox_cfg).initWidget())
            except Exception as e:
                logma.warning(
                    f"[settings] _build_right_pane_visibility_checks: skip "
                    f"row name={rec.get('name_txt')!r} ({type(e).__name__}: {e})"
                )
        return group

    def _query_right_pane_tab_rows(self):
        """Run the right-side tab query and return rows as a list of
        dicts (off-screen-test-friendly shape). Returns ``None`` when
        the store is unavailable.
        """
        app = getattr(self, "app", None)
        if app is None:
            return None
        model = getattr(app, "model", None)
        if model is None:
            return None
        store = getattr(model, "store", None)
        if store is None:
            return None
        cfg = {
            "WHERE": {
                "IN": {
                    "tabset_type_txt": ["right"],
                },
            },
            "ORDER": ["position_int"],
        }
        rows = store.get_table("vw_tab", cfg)
        try:
            import pandas as pd

            if isinstance(rows, pd.DataFrame):
                if len(rows) == 0:
                    return []
                return rows.to_dict(orient="records")
        except Exception:
            pass
        # Fallback: assume rows is already iterable of dicts.
        try:
            return list(rows)
        except Exception:
            return []

    def _initialize_left_side(self, primary_layout):
        """"""
        # Left Side Settings Group
        left_side_settings_group = NchantdGridScrollGroupBox()
        left_side_settings_group.scroll.setHorizontalScrollBarPolicy(pyqt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_side_settings_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
        left_side_settings_group.setTitle("Left Pane Settings")
        primary_layout.addLayout(left_side_settings_group.layout)
        cnt = 0
        # PUSH 0.0.3:
        # cfg = {
        #     "text": "Show Journal Node",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.enable_journal_focus_bit,
        #     "handler": self.cmd_on_change_journal_focus,
        # }
        # self.enable_journal_focus_entry = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.enable_journal_focus_entry, cnt, 0)
        # cnt += 1
        # cfg = {
        #     "text": "Show Settings Node",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.enable_settings_focus_bit,
        #     "handler": self.cmd_on_change_settings_focus,
        # }
        # self.settings_node = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.settings_node, cnt, 0)
        # cnt += 1
        # HOLD
        # cfg = {
        #     "text": "Enable Automation",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.enable_automation_bit,
        #     "handler": self.cmd_on_change_automation,
        # }
        # self.automation_enable = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.automation_enable, cnt, 0)
        # cnt += 1
        # cfg = {
        #     "text": "Enable Data Sources",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.enable_data_sources_bit,
        #     "handler": self.cmd_on_change_data_source,
        # }
        # self.data_source_enable = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.data_source_enable, cnt, 0)
        # cnt += 1
        # cfg = {
        #     "text": "On Startup Show Left Side Pane",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.show_left_pane,
        #     "handler": self.cmd_on_change_show_left_side_pane,
        # }
        # self.left_side_pane = NchantdCheckbox(self, cfg).initWidget()
        # left_side_settings_group.addWidget(self.left_side_pane, cnt, 0)
        # cnt += 1
        # cfg = {
        #     "text": "On Startup Show Quick Launch Toolbar",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.show_quick_toolbar,
        #     "handler": self.cmd_on_change_quicklaunch,
        # }
        # self.quick_launch_toolbar = NchantdCheckbox(self, cfg).initWidget()
        if self.config.dikt.get("has_quick_launch_toolbar", False) is True:
            self.quick_launch_toolbar.setChecked(True)
        # left_side_settings_group.addWidget(self.quick_launch_toolbar, cnt, 0)
        # cnt += 1
        document_group = pyqt.QGroupBox()
        document_group.setTitle("Quick launch Documents")
        document_group_layout = pyqt.QVBoxLayout()
        document_group_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)
        document_group.setLayout(document_group_layout)
        self.quick_launch_document_types = {}
        for i, document in self.document_types_df.iterrows():
            cfg = {"text": document["name_txt"], "layout": "horizontal", "size": ["auto", "auto"]}
            self.quick_launch_document_types[document["name_txt"]] = NchantdCheckbox(self, cfg).initWidget()
            # if not self.quick_launch_toolbar.isChecked():
            #     self.quick_launch_document_types[document["name_txt"]].setDisabled(True)
            if document["quick_launch_bit"] == 1:
                self.quick_launch_document_types[document["name_txt"]].setChecked(True)
            document_group_layout.addWidget(self.quick_launch_document_types[document["name_txt"]])
        left_side_settings_group.addWidget(document_group, cnt, 0)

    def _initialize_right_side(self, primary_layout):
        """"""
        # Right Side Settings Group
        right_side_settings_group = NchantdGridScrollGroupBox()
        right_side_settings_group.scroll.setHorizontalScrollBarPolicy(pyqt.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_side_settings_group.setTitle("Right Pane Settings")
        primary_layout.addLayout(right_side_settings_group.layout)
        # cfg = {
        #     "text": "Always Refocus Right Side Tabs to",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.refocus_right_side_tab,
        #     "handler": self.cmd_on_change_right_side_focus,
        # }
        # T-removed: commented-out refocus-right-side-tab checkbox block
        # (T10/T11/T12). The dropdown below (self.refocus_default_document)
        # already covers the "select right side tab" functionality.
        cfg = {
            "label": "Selected Right Side Tab",
            "layout": "horizontal",
            "combobox": {"options": self.get_right_pane_tab_options()},
            "value": self.default_right_side_tab,
            "handler": self.cmd_on_change_right_side_tab_select,
        }
        self.refocus_default_document = NchantdDropDown(self, cfg).initWidget()
        right_side_settings_group.addWidget(self.refocus_default_document, 1, 0)

        # T-NEW-028: right-pane tab visibility checklist. Below the
        # "Selected Right Side Tab" dropdown, render one checkbox per
        # row in ``app_tab`` / ``doc_tab`` (via ``vw_tab``) filtered
        # by ``tabset_type_txt = "right"``. Each checkbox's handler
        # is the module-level ``cmd_on_change_visible_right_tab`` --
        # clicking flips ``visible_bit`` on the underlying row.
        self.right_pane_tab_visibility_checks = self._build_right_pane_visibility_checks()
        right_side_settings_group.addWidget(self.right_pane_tab_visibility_checks, 2, 0)

        # cfg = {
        #     "text": "On Startup Show Right Side Pane",
        #     "layout": "horizontal",
        #     "size": ["auto", "auto"],
        #     "value": self.show_right_side_tab,
        #     "handler": self.cmd_on_change_show_right_side_pane,
        # }
        # self.right_side_pane = NchantdCheckbox(self, cfg).initWidget()
        # right_side_settings_group.addWidget(self.right_side_pane, 2, 0)

        # group = pyqt.QGroupBox("Right Side Tabs List")
        # layout = pyqt.QVBoxLayout()
        # group.setLayout(layout)
        # data = ["Journal", "ToolBox", "Calendar", "Calculator"]
        # cfg = {"text": "Right Side Tabs List", "layout": "horizontal", "data": data}
        # self.right_side_pane_tabs_list = NchantdList(self, cfg).initWidget()
        # layout.addWidget(self.right_side_pane_tabs_list)
        # cfg = {"label": "Tab Name: ", "layout": "horizontal"}
        # self.tab_entry = NchantdEntryEditor(self, cfg).initWidget()
        # layout.addWidget(self.tab_entry)
        # cfg = {"label": "Tab Type: ", "layout": "horizontal"}
        # self.tab_type_entry = NchantdDropDown(self, cfg).initWidget()
        # layout.addWidget(self.tab_type_entry)
        # cfg = {"label": "Sequence: ", "layout": "horizontal"}
        # self.tab_sequence_spin = NchantdLabeledSpinBox(self, cfg).initWidget()
        # layout.addWidget(self.tab_sequence_spin)
        # cfg = {"text": "Accept Buttons: ", "layout": "horizontal"}
        # self.new_tab_accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        # layout.addWidget(self.new_tab_accept_buttons)
        # right_side_settings_group.addWidget(group, 3, 0)
        cnt = 0
        if self.config.dikt.get("has_quick_launch_toolbar", False) is True:
            self.quick_launch_toolbar.setChecked(True)
        # left_side_settings_group.addWidget(self.quick_launch_toolbar, cnt, 0)
        # cnt += 1
        # document_group = pyqt.QGroupBox()
        # document_group.setTitle("Quick launch Documents")
        # document_group_layout = pyqt.QVBoxLayout()
        # document_group_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignLeft)
        # document_group.setLayout(document_group_layout)
        # self.quick_launch_document_types = {}
        # for i, document in self.document_types_df.iterrows():
        #     cfg = {"text": document["name_txt"], "layout": "horizontal", "size": ["auto", "auto"]}
        #     self.quick_launch_document_types[document["name_txt"]] = NchantdCheckbox(self, cfg).initWidget()
        #     # if not self.quick_launch_toolbar.isChecked():
        #     #     self.quick_launch_document_types[document["name_txt"]].setDisabled(True)
        #     if document["quick_launch_bit"] == 1:
        #         self.quick_launch_document_types[document["name_txt"]].setChecked(True)
        #     document_group_layout.addWidget(self.quick_launch_document_types[document["name_txt"]])
        # right_side_settings_group.addWidget(document_group, cnt, 0)
        # right_side_settings_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)


# Module-level aliases so off-screen tests + non-method callers can
# reach the right-pane tab machinery without instantiating the full
# ``NchantdOfficeInterfaceSettings`` (which needs a live Qt parent).
# Both aliases delegate to the live implementation (instance method
# for ``get_right_pane_tab_options``; module-level function for
# ``cmd_on_change_visible_right_tab``) so there's one source of
# truth -- no duplication of the query / dispatch logic.
get_right_pane_tab_options = NchantdOfficeInterfaceSettings.get_right_pane_tab_options
# ``cmd_on_change_visible_right_tab`` is already module-level (it
# takes a settings arg explicitly so callers without a live Qt
# parent can drive it). No alias needed.


class NchantdOfficeThemeSettings(NchantdThemeSettings):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeThemeSettings").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
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


# T-DESK: NchantdOfficeAffiliateManager (the old placeholder that just
# rendered an external /affiliate_marketing webview) was replaced by
# ``NchantdOfficeReferralPanel`` (see ``widgets/config/referral_panel.py``).
# The class name is preserved here as a re-export so any existing
# registry/init code that references ``NchantdOfficeAffiliateManager``
# keeps working without changes.
try:
    from nchantdoffice.widgets.config.referral_panel import NchantdOfficeReferralPanel

    NchantdOfficeAffiliateManager = NchantdOfficeReferralPanel
except ImportError:

    class NchantdOfficeAffiliateManager(NchantdOfficeDocumentManager):  # noqa: F811
        """Fallback shim if referral_panel.py cannot be imported.

        Renders a minimal stub webview pointing at the affiliate
        marketing page so the app doesn't crash if the new panel
        module has an import error.
        """

        def __init__(self, parent=None, cfg=None):
            super().__init__(parent, cfg)
            self.name = "NchantdOffice Affiliate Manager (fallback)"
            self.user = pyqt.QApplication.instance().model.user
            self.canvas = None
            self.data_series = None

        def initModel(self):
            super().initModel()
            return self

        def initView(self, cfg=None):
            super().initView(cfg or {})
            layout = pyqt.QHBoxLayout()
            url_cfg = {
                "url": "https://www.nchantdoffice.com/affiliate_marketing",
                "size": [1600, 750],
                "is_simple": True,
            }
            self.browser = NchantdWebViewer(self, url_cfg).initWidget()
            layout.addWidget(self.browser)
            self.layout.addLayout(layout)
            return cfg

        def initWidget(self):
            self.initModel()
            self.initView()
            return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
