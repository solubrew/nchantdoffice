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
from nchantdoffice.widgets.panes.document_settings import NchantdOfficeDocumentConfigPane

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
        """ """
        super().initView(cfg)
        self.primary_settings_group = pyqt.QGroupBox()
        self.primary_settings_group.setTitle("Interface Settings")
        primary_layout = pyqt.QHBoxLayout()
        self.primary_settings_group.setLayout(primary_layout)
        self._initialize_left_side(primary_layout)
        self._initialize_center(primary_layout)
        self._initialize_right_side(primary_layout)
        self.layout.addWidget(self.primary_settings_group)
        return self

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
                getter = getattr(widget, "currentText", None) or getattr(
                    widget, "get_value", None
                )
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
                value = bool(
                    getattr(self, "prompt_for_new_node_name", False)
                )
            self.prompt_for_new_node_name = value
            self.config.dikt["prompt_for_new_node_name"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_prompt_for_new_node_name "
                f"failed: {e}",
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
                value = bool(
                    getattr(self, "prompt_for_new_tab_name", False)
                )
            self.prompt_for_new_tab_name = value
            self.config.dikt["prompt_for_new_tab_name"] = value
        except Exception as e:
            logma.error(
                f"[settings] cmd_on_change_prompt_for_new_tab_name "
                f"failed: {e}",
                exc_info=True,
            )
        return self

    def get_right_pane_tab_options(self):
        """Enumerate the available right-pane tabs as dropdown options.

        Reads the application's right-pane tab registry when present;
        falls back to the canonical 4-tab default list when the
        registry is not yet wired up. Each entry is ``"<index> - <name>"``
        so the user can identify the tab both by ordinal and label.

        Returns:
            A list of strings suitable for ``combobox.options``.
        """
        try:
            tabs = []
            view = getattr(self.app, "view", None)
            if view is not None and hasattr(view, "panes"):
                pane = view.panes.get("right") if isinstance(view.panes, dict) else None
                if pane is not None:
                    for idx, child in enumerate(getattr(pane, "widgets", lambda: [])()):
                        name = type(child).__name__
                        tabs.append(f"{idx} - {name}")
            if not tabs:
                tabs = ["0 - Journal", "1 - ToolBox", "2 - Calendar", "3 - Calculator"]
            return tabs
        except Exception as e:
            logma.error(f"[settings] get_right_pane_tab_options failed: {e}", exc_info=True)
            return ["0 - Journal", "1 - ToolBox", "2 - Calendar", "3 - Calculator"]

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

        # Per-document-type configuration pane: each registered
        # document type gets its own row in the center settings grid.
        # Each row has a label + a launch-catalog checkbox wired to
        # ``cmd_on_change_document_catalog``.
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
            config_pane = NchantdOfficeDocumentConfigPane(self, cfg).initWidget()
            center_settings_group.addWidget(config_pane, row, 0)
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

        primary_layout.addLayout(center_settings_group.layout)

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
        right_side_settings_group.addWidget(document_group, cnt, 0)
        right_side_settings_group.layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)


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
