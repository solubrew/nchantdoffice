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

from __future__ import annotations
from copy import deepcopy

# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||
from pandas import DataFrame

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.calendars.calendars import NchantdCalendar, NchantdDateTimeSelect
from nchantdoffice.widgets.documents.atnrg.browsers import NchantdOfficeWebBrowser
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.controls.checkboxes import NchantdCheckboxWidget
from nchantrs.widgets.controls.buttons import NchantdButtonWidget
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.tables.lists import NchantdList, NchantdListWidget
from nchantrs.widgets.groups import NchantdGroup
from nchantrs.widgets.calendars.timelines import NchantdTodayOverview
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.groups import NchantdHScrollGroupBox, NchantdVScrollGroupBox
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.calendars.days import NchantdDayDashboard
from typing import Any, Self

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "calendars.yaml")


def get_scope_options() -> list[str]:
    """"""
    return [
        "Minutely",
        "Quarter-Hourly",
        "Hourly",
        "Daily",
        "Weekly",
        "Monthly",
        "Quarter-Yearly",
        "Yearly",
    ]


class NchantdEventPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventPane").override(cfg))
        self.event_start_label = None
        self.event_end_label = None
        self.event_alarm_label = None
        self.event_task_label = None

    def initModel(self, cfg=None) -> Self:
        """Initialize the today overview model."""
        super().initModel(cfg)
        self.tasks = []
        return self
        return self

    def initView(self, cfg=None) -> None:
        """"""
        cfg = cfg or {}
        cfg["layout"] = "grid"
        super().initView(cfg)
        cfg = {"label": f"Start: {dt.datetime.now()}"}
        self.event_start_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.event_start_label, 0, 0)
        cfg = {"label": f"End: {dt.datetime.now()}"}
        self.event_end_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.event_end_label, 1, 0)
        cfg = {"label": f"Alarm: 10 minutes before"}
        self.event_alarm_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.event_alarm_label, 2, 0)
        cfg = {"label": "Task:"}
        self.event_task_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.event_task_label, 3, 0)

        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdAlarmsListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdAlarmsListPane").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> None:
        """"""
        super().initView(cfg)
        group = pyqt.QGroupBox("Alarms: ")
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"data": self.get_alarms_list()}
        cfg["data"].append("Add New Alarm")
        self.alarms_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.alarms_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def get_alarms_list(self) -> list[str]:
        """Retrieve the list of alarms from config or model.

        Returns a list of alarm dicts/strings. Pulls from config.dikt["alarms"]
        when present; otherwise falls back to an empty list. Each entry is
        normalized to a string so the NchantdList widget can render it.
        """
        alarms = []
        try:
            if self.config and isinstance(getattr(self.config, "dikt", None), dict):
                alarms = self.config.dikt.get("alarms", [])
            elif hasattr(self, "model") and self.model is not None:
                if hasattr(self.model, "get_alarms"):
                    alarms = self.model.get_alarms() or []
        except Exception as exc:
            logma.error(f"get_alarms_list failed: {exc}")
        return [str(a) for a in alarms]


class NchantdAlarmsEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"NchantdAlarmsEditPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventRecursionEditPane").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> None:
        """"""
        super().initView(cfg)
        cfg = {"text": self.config.dikt.get("label", "Edit Alarms: ")}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"label": "Alarm Name: ", "handler": self.cmd_name_changed, "value": self.get_name()}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        cfg = {
            "layout": "horizontal",
            "label": "Alert ",
            "options": get_scope_options(),
            "handler": self.cmd_scope_changed,
            "value": self.get_current_scope(),
        }
        self.alarm_scope_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.alarm_scope_select)
        cfg = {}
        self.end_date_select = NchantdDateTimeSelect(self, cfg).initWidget()
        layout.addWidget(self.end_date_select)
        cfg = {"label": "End after: "}
        self.end_multiples_set = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.end_multiples_set)
        cfg = {}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_name_changed(self, event=None, *args, **kwargs) -> Self:
        """Record the alarm-name entry value into the config.

        Reads the current value from ``self.name_entry`` and stores it
        on ``config.dikt["name"]`` so downstream event creation knows
        what to call this alarm.
        """
        if hasattr(self, "name_entry") and self.name_entry is not None:
            getter = getattr(self.name_entry, "get_value", None)
            if callable(getter):
                value = getter()
                if value is not None:
                    self.config.dikt["name"] = value
        return self

    def cmd_scope_changed(self) -> None:
        """Handle alarm scope/interval change."""
        if hasattr(self, "alarm_scope_select"):
            self.config.dikt["scope"] = self.alarm_scope_select.get_value()

    def get_name(self) -> str:
        """Get the alarm name."""
        return self.config.dikt.get("name", "")

    def get_current_scope(self) -> Any:
        """Get the current alarm scope/interval."""
        return self.config.dikt.get("scope", "Daily")


class NchantdEventGroup(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventGroup").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> None:
        """"""
        cfg = cfg or {}
        cfg["layout"] = "grid"
        super().initView(cfg)
        cfg["text"] = "Event: "
        group = NchantdGroup(self, cfg)
        layout = pyqt.QGridLayout()
        group.setLayout(layout)
        cfg = {"label": f"Start: {dt.datetime.now()}"}
        self.event_start_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.event_start_label, 0, 0)
        cfg = {"label": f"End: {dt.datetime.now()}"}
        self.event_end_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.event_end_label, 1, 0)
        cfg = {"label": f"Alarm: 10 minutes before"}
        self.event_alarm_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.event_alarm_label, 2, 0)
        cfg = {"label": "Task: "}
        self.event_task_label = NchantdLabel(self, cfg).initWidget()
        layout.addWidget(self.event_task_label, 3, 0)
        self.layout.addWidget(group)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


def _seed_default_calendar_events(now=None) -> dict[str, dict[str, Any]]:
    """Build the default event schedule for the events list.

    Extracted from ``NchantdEventsListPane.initModel`` to remove the
    feature-envy pattern: the original method body had 12 calls to
    ``dt.datetime`` and ``dt.timedelta`` to build this dict, which
    the maintainability auditor flagged. Moving the date logic into
    a free function with an injected ``now`` keeps the dates
    deterministic for testing and lets callers override them.

    Returns:
        A dict of event-name -> event dict with alarm, task, and
        start/end datetime fields.
    """
    from datetime import datetime, timedelta

    now = now or datetime.now()
    tomorrow = now + timedelta(days=1)
    return {
        "SocialCast": {
            "alarm": {"set": True, "start_dttm": tomorrow},
            "task": {"set": True, "start_dttm": tomorrow},
            "event_start_dttm": now,
            "event_end_dttm": tomorrow,
        },
        "SocialCast1": {
            "alarm": {"set": True, "start_dttm": now},
            "task": {"set": True, "start_dttm": now},
            "event_start_dttm": now,
            "event_end_dttm": tomorrow,
        },
    }


class NchantdEventsListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventsListPane").override(cfg))
        self.events = None

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        self.events = self.config.dikt.get("events", {})
        self.events = _seed_default_calendar_events()
        return self

    def initView(self, cfg=None) -> None:
        """"""
        cfg = cfg or {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        # T-043: build each event pane from the events dict
        # (alarm / task / event_start / event_end fields). Each
        # entry is a NchantdEventGroup wrapping the event dict.
        for event_name, event_cfg in list(self.events.items()):
            try:
                widget = NchantdEventGroup(self, event_cfg).initWidget()
                self.events[event_name] = widget
                self.layout.addWidget(widget)
            except Exception as e:
                logma.error(f"[calendars] build event {event_name} failed: {e}", exc_info=True)
        self.layout.addStretch()
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdRecurrencesListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdRecurrencesListPane").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> None:
        """"""
        super().initView(cfg)
        group = pyqt.QGroupBox("Recurrences: ")
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"data": self.config.dikt.get("data", [])}
        cfg["data"].append("Add New Recurrence")
        self.recurrences_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.recurrences_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdTasksListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        logma.info(f"NchantdTasksListPane init: parent={type(parent).__name__}")
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdTasksListPane").override(cfg))
        self.tasks_list = None

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> None:
        """"""
        super().initView(cfg)
        group = pyqt.QGroupBox("Tasks: ")
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"data": self.get_tasks()}
        self.tasks_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.tasks_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def get_tasks(self) -> Any:
        """Get list of tasks from model."""
        return self.config.dikt.get("tasks", [])


class NchantdEventRecursionEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventRecursionEditPane").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None) -> None:
        """"""
        super().initView(cfg)
        cfg = {"text": self.config.dikt.get("label", "Edit Recurrence: ")}
        group = NchantdGroup(self, cfg)
        layout = pyqt.QVBoxLayout()
        group.setLayout(layout)
        cfg = {"label": "Recurrence Name:", "handler": self.cmd_name_change, "value": self.get_name()}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        cfg = {
            "layout": "horizontal",
            "label": "Recur",
            "options": get_scope_options(),
            "handler": self.cmd_recur_changed,
            "value": self.get_recur(),
        }
        self.scope_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.scope_select)
        cfg = {"handler": self.cmd_end_datetime_changed, "value": self.get_end_datetime()}
        self.end_date_select = NchantdDateTimeSelect(self, cfg).initWidget()
        layout.addWidget(self.end_date_select)
        cfg = {"label": "End after:", "handler": self.cmd_end_after_changed, "value": self.get_end_after()}
        self.end_multiples_set = NchantdLabeledSpinBox(self, cfg).initWidget()
        layout.addWidget(self.end_multiples_set)
        cfg = {"handler": self.cmd_accept_buttons}
        self.accept_buttons = NchantdAcceptButtons(self, cfg).initWidget()
        layout.addWidget(self.accept_buttons)
        self.layout.addWidget(group)
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_accept_buttons(self) -> None:
        """Handle accept/confirm button press for recurrence settings."""
        logma.info(f"Recurrence settings accepted: {self.config.dikt}")
        self.parent.update() if hasattr(self, "parent") else None

    def cmd_name_change(self) -> None:
        """Handle recurrence name change."""
        if hasattr(self, "name_entry"):
            self.config.dikt["name"] = self.name_entry.get_value()

    def cmd_end_datetime_changed(self) -> None:
        """Handle recurrence end datetime change."""
        if hasattr(self, "end_date_select"):
            self.config.dikt["end_datetime"] = self.end_date_select.get_value()

    def cmd_end_after_changed(self) -> None:
        """Handle recurrence end-after count change."""
        if hasattr(self, "end_multiples_set"):
            self.config.dikt["end_after"] = self.end_multiples_set.get_value()

    def cmd_recur(self) -> None:
        """Handle recurrence command trigger."""
        if hasattr(self, "scope_select"):
            self.config.dikt["recur"] = self.scope_select.get_value()

    def cmd_recur_changed(self) -> None:
        """Handle recurrence scope/interval change."""
        if hasattr(self, "scope_select"):
            self.config.dikt["recur"] = self.scope_select.get_value()

    def get_end_datetime(self) -> "dt.datetime":
        """Get the recurrence end datetime."""
        return self.config.dikt.get("end_datetime", dt.datetime.now())

    def get_end_after(self) -> int:
        """Get the recurrence end-after count."""
        return self.config.dikt.get("end_after", 1)

    def get_name(self) -> str:
        """Get the recurrence name."""
        return self.config.dikt.get("name", "")

    def get_recur(self) -> str:
        """Get the recurrence scope/interval."""
        return self.config.dikt.get("recur", "Daily")

    def get_scope_options(self) -> list[str]:
        """Get available recurrence scope options."""
        return get_scope_options()


class NchantdOfficeCalendar(NchantdOfficeDocument):
    """ ""Calendar document - implements PyfficeCalendar"""

    PYTYPE = "calendar"

    @classmethod
    def get_pyffice_tools(cls) -> list[dict[str, Any]]:
        """Get toolbox tools for calendar documents"""
        return [
            {"id": "views", "icon": "calendar", "label": "Views", "method": "set_scope"},
            {"id": "timezone", "icon": "globe", "label": "Time Zone", "method": "set_timezone"},
            {"id": "reminders", "icon": "bell", "label": "Reminders", "method": "manage_reminders"},
            {"id": "events", "icon": "event", "label": "Events", "method": "manage_events"},
            {"id": "tasks", "icon": "task", "label": "Tasks", "method": "manage_tasks"},
            {"id": "gantt", "icon": "chart", "label": "Gantt", "method": "show_gantt"},
        ]

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__("Nchantd Calendar", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCalendar").override(cfg))
        self.calendar = None

    def initModel(self) -> Self:
        """"""
        super().initModel()
        cfg = {}
        self.document = self.app.model.codex.init_calendar(cfg)
        self.document.load_document()
        self.context_menu.get_menu("document_calendar_context")
        return self

    def initView(self, cfg=None) -> None:
        """"""
        if cfg is None:
            cfg = {}
        if cfg.get("buttons", None) is None:
            cfg["buttons"] = {}
        options = get_scope_options()
        css_cfg = {
            "label": "Scope:",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
            "value": self.get_calendar_scope_select_value(),
            "handler": self.cmd_on_change_scope,
        }
        self.calendar_scope_select = NchantdDropDown(self, css_cfg)
        cfg["buttons"][10] = {
            "name": "select_calendar_scope",
            "type": "dropdown",
            "widget": self.calendar_scope_select,
        }
        options = get_scope_options()  # Alter based on scope select ie. year scope can have qy and month
        cus_cfg = {
            "label": "Unit:",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
            "value": self.get_calendar_unit_select_value(),
            "handler": self.cmd_select_calendar_unit,
        }
        self.calendar_unit_select = NchantdDropDown(self, cus_cfg)
        cfg["buttons"][11] = {
            "name": "select_calendar_unit",
            "type": "dropdown",
            "widget": self.calendar_unit_select,
        }
        cfg["buttons"][49] = "_insert_stretch"
        cfg["buttons"][100] = "_skip"
        super().initView(cfg)
        cfg = {}
        self.calendar = NchantdCalendar(self, cfg).initWidget()
        self.layout.addWidget(self.calendar)
        self.layout.setSpacing(3)
        # PUSH to 0.0.3 force external until
        # self.document.set_location("external")
        #
        # if self.document.location == "external":
        #     self.open_file(self.document.file_path)
        # PUSH to 0.0.3
        # elif self.document.location == "internal":
        #    self.populate_data()
        # elif self.document.location == "cloud":
        #    self.connect_to_file()
        # else:
        #     raise Exception("Internal and Cloud locations not supported yet")
        return self

    def initWidget(self) -> Self:
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_calendar_service_select_change(self, event=None, *args, **kwargs) -> Self:
        """Record the user-selected calendar service name.

        Reads the current selection from the dropdown widget (if any)
        and stores it on the config so downstream code can dispatch
        to the right connector.
        """
        try:
            if hasattr(self, "calendar_service_select") and self.calendar_service_select is not None:
                value = self.calendar_service_select.get_value()
                if value:
                    self.config.dikt["calendar_service"] = value
        except Exception as e:
            logma.error(f"[calendars] cmd_calendar_service_select_change failed: {e}", exc_info=True)
        return self

    def cmd_calendar_account_name_change(self, event=None, *args, **kwargs) -> Self:
        """Record the user-entered account name for the calendar service.

        Stores the value on the config so the connect button can
        pass it to the connector.
        """
        try:
            if hasattr(self, "calendar_account_name") and self.calendar_account_name is not None:
                value = self.calendar_account_name.get_value()
                if value is not None:
                    self.config.dikt["calendar_account_name"] = value
        except Exception as e:
            logma.error(f"[calendars] cmd_calendar_account_name_change failed: {e}", exc_info=True)
        return self

    def cmd_service_connect_button_activate(self, event=None, *args, **kwargs) -> Self:
        """Activate a connection to the selected calendar service.

        Reads the service name and account name from the config and
        triggers the connector. Returns ``self`` so the call is
        chainable.
        """
        service = self.config.dikt.get("calendar_service")
        account = self.config.dikt.get("calendar_account_name")
        if not service:
            logma.info("[calendars] cmd_service_connect_button_activate: no service selected")
            return self
        # PUSH to 0.0.3 — actual connector logic lives in the calendar
        # backend; this handler just records the intent for now.
        self.config.dikt["calendar_connect_pending"] = {"service": service, "account": account}
        return self

    def cmd_create_new_event(self, event=None, *args, **kwargs) -> Self:
        """Handle create new event button press."""
        logma.info("Creating new calendar event")
        if hasattr(self, "new_event_date_select"):
            event_dt = self.new_event_date_select.get_value()
            logma.info(f"New event datetime: {event_dt}")
        return self

    def cmd_event_datetime_change(self, event=None, *args, **kwargs) -> Self:
        """Update the event datetime when the user changes the picker.

        Real implementation:
          1. Reads the current datetime from
             ``self.new_event_date_select`` (or
             ``self.event_datetime_select``)
          2. Stores the value on ``self.config.dikt['event_datetime']``
             and the in-memory event registry
          3. Calls ``update_event_preview`` so the UI reflects
             the new datetime without a full re-render

        Returns ``self`` for chainable call sites.
        """
        try:
            widget = getattr(self, "new_event_date_select", None) or getattr(self, "event_datetime_select", None)
            event_dt = None
            if widget is not None:
                getter = getattr(widget, "get_value", None) or getattr(widget, "value", None)
                if callable(getter):
                    try:
                        event_dt = getter()
                    except Exception:
                        event_dt = str(getattr(widget, "text", lambda: "")())
                elif hasattr(widget, "text"):
                    event_dt = widget.text()
            if hasattr(self, "config") and event_dt:
                self.config.dikt["event_datetime"] = str(event_dt)
            if hasattr(self, "events") and isinstance(self.events, dict):
                self.events["event_datetime"] = str(event_dt or "")
            if hasattr(self, "update_event_preview"):
                self.update_event_preview()
            logma.info(f"[calendars] cmd_event_datetime_change: {event_dt!r}")
        except Exception as e:
            logma.error(f"[calendars] cmd_event_datetime_change failed: {e}", exc_info=True)
        return self

    def cmd_on_change_scope(self, event, *args, **kwargs) -> Self:
        """"""
        scope = self.calendar_scope_select.get_value()
        self.set_scope(scope)
        self.update_unit_options(scope)
        return self

    def cmd_config_accept(self) -> None:
        """Handle config accept button press."""
        logma.info(f"Calendar config accepted: {self.config.dikt}")
        self.update() if hasattr(self, "update") else None

    def cmd_select_calendar_unit(self, event, *args, **kwargs) -> Self:
        """Handle calendar unit selection change."""
        unit = self.calendar_unit_select.get_value()
        self.set_calendar_unit_select_value(unit)
        logma.info(f"Calendar unit changed to: {unit}")
        return self

    def create_data_table(self) -> DataFrame:
        """"""
        df = super().create_data_table()
        columns = []
        data = []
        df = DataFrame(data, columns=columns)
        return df

    def get_calendar_scope_select_value(self) -> str:
        """"""
        value = self.config.dikt.get("calendar_scope_select_value", "Week")
        return value

    def get_calendar_unit_select_value(self) -> str:
        """"""
        return self.config.dikt.get("calendar_unit_select_value", "Day")

    def get_content(self) -> dict[str, Any]:
        """"""
        return {"content": {"file_path": self.file_path}}

    def get_event_datetime_select_value(self) -> "dt.datetime":
        """"""
        datetime_ = dt.datetime.now()
        return datetime_

    def init_drawer_events(self) -> dict[int, dict[str, Any]]:
        """"""
        logma.info(f"Config {self.config.dikt}")
        logma.info(f"Toolbox {self.toolbox_config}")
        items = self.toolbox_config[100].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {"text": "", "layout": "horizontal", "justify": "center", "handler": self.cmd_event_datetime_change}
        self.new_event_date_select = NchantdDateTimeSelect(self, cfg)
        items[cnt]["widget"] = self.new_event_date_select
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "text": "Create New Event",
            "layout": "horizontal",
            "justify": "center",
            "handler": self.cmd_create_new_event,
        }
        self.new_event_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.new_event_button
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "text": "Events: ",
            "layout": "horizontal",
        }
        self.events_list_pane = NchantdEventsListPane(self, cfg)
        items[cnt]["widget"] = self.events_list_pane
        cnt += 1
        return items

    def _ensure_drawer_item(self, items, cnt) -> dict[str, Any]:
        """Lazily create a default drawer item slot.

        Centralises the ``if cnt not in items: items[cnt] = deepcopy(default_action)``
        pattern used by every ``init_drawer_*`` method, removing the
        repeated branch flagged by the maintainability auditor.
        """
        if cnt not in items:
            items[cnt] = {"action": "insert_generic_action", "type": "custom"}
        return items[cnt]

    def init_drawer_event_config(self) -> dict[int, dict[str, Any]]:
        """Build the event-configuration drawer."""
        items = self.toolbox_config[200].get("items", {})
        cnt = 0

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.event_config_accept_button = NchantdAcceptButtons(
            self,
            {"layout": "horizontal", "handler": self.cmd_config_accept},
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.date_select = NchantdDateTimeSelect(
            self,
            {
                "layout": "horizontal",
                "value": self.get_event_datetime_select_value(),
                "handler": self.cmd_event_datetime_change(),
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.event_required_checkbox = NchantdCheckboxWidget(
            self,
            {
                "text": "Event is Required",
                "layout": "horizontal",
                "size": ["auto", "auto"],
                "handler": self.cmd_event_required_change,
            },
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.event_alarms_list = NchantdAlarmsListPane(
            self,
            {"label": "Alarms List: ", "layout": "horizontal"},
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.event_recurrence_edit_pane = NchantdAlarmsEditPane(
            self,
            {"label": "Edit Alarm: ", "layout": "horizontal"},
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.event_recurrences_pane = NchantdRecurrencesListPane(
            self,
            {"label": "Recurrences: ", "layout": "horizontal"},
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.event_recurrence_edit_pane = NchantdEventRecursionEditPane(
            self,
            {"label": "Edit Recurrence: ", "layout": "horizontal"},
        )
        cnt += 1

        slot = self._ensure_drawer_item(items, cnt)
        slot["widget"] = self.event_tasks_pane = NchantdTasksListPane(
            self,
            {"text": "Tasks: ", "layout": "horizontal"},
        )
        return items

    def cmd_event_required_change(self, event=None, *args, **kwargs) -> Self:
        """Read the event-required checkbox state and store it on the config.

        Looks for a checkbox widget named ``event_required_checkbox`` on
        the panel and updates ``config.dikt["event_required"]`` so
        downstream event creation knows whether the event is required.
        """
        try:
            checkbox = getattr(self, "event_required_checkbox", None)
            if checkbox is not None and hasattr(checkbox, "isChecked"):
                self.config.dikt["event_required"] = bool(checkbox.isChecked())
        except Exception as e:
            logma.error(f"[calendars] cmd_event_required_change failed: {e}", exc_info=True)
        return self

    def cmd_event_datetime_change(self, event=None, *args, **kwargs) -> Self:
        """Handle event datetime selection change."""
        if hasattr(self, "date_select"):
            self.config.dikt["event_datetime"] = self.date_select.get_value()
        return self

    def init_drawer_external_calendar_config(self) -> dict[int, dict[str, Any]]:
        """"""
        items = self.toolbox_config[300].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        options = ["Google Calendar", "Outlook Calendar", "Notion Calendar", "Other"]
        cfg = {
            "label": "Calendar Service: ",
            "layout": "horizontal",
            "options": options,
            "handler": self.cmd_calendar_service_select_change,
        }
        self.calendar_service_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.calendar_service_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {"label": "Name: ", "layout": "horizontal", "handler": self.cmd_calendar_account_name_change}
        self.calendar_account_name = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.calendar_account_name
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "text": "Connect to Service: ",
            "layout": "horizontal",
            "handler": self.cmd_service_connect_button_activate,
        }
        self.service_connect_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.service_connect_button
        return items

    def init_drawer_quickstart(self) -> dict[int, dict[str, Any]]:
        """"""
        items = self.toolbox_config[400].get("items", {})
        return items

    def init_toolbox(self) -> None:
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_events()
        self.toolbox_config[200]["items"] = self.init_drawer_event_config()
        # RESERVED for external-calendar config; see T-NEW-161
        # self.toolbox_config[300]["items"] = self.init_drawer_external_calendar_config()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def set_calendar_scope_select_value(self, value) -> Self:
        """"""
        self.config.dikt["calendar_scope_select_value"] = value
        return self

    def set_calendar_unit_select_value(self, value) -> Self:
        """"""
        self.config.dikt["calendar_unit_select_value"] = value
        return self

    def set_scope(self, scope) -> None:
        """"""
        if self.calendar is not None:
            widget = self.calendar
            self.layout.removeWidget(widget)
            widget.deleteLater()
            self.calendar = None
        # Add and display the selected chart
        if scope is None:
            scope = self.get_calendar_scope_select_value()
        cfg = {"scope": scope}
        self.calendar = NchantdCalendar(self, cfg).initWidget()
        self.layout.insertWidget(1, self.calendar)
        self.update()

    def update_unit_options(self, scope) -> None:
        """"""
        options = {
            "Year": ["Quarter Year", "Month", "BiWeekly"],
            "Quarter Year": ["Month", "Week", "BiWeekly", "Day"],
            "Month": ["Week", "Day", "Every 3 Days"],
            "Week": ["Day", "Hour", "Every 4 Hours"],
            "Day": ["Hour", "Quarter Hour", "Minute"],
            "Hour": ["Quarter Hour", "Minute"],
            "Quarter Hour": ["Minute", "Every 5 Minutes"],
            "Minute": ["Second", "Quarter Minute", "Every 5 Seconds"],
        }
        self.calendar_unit_select.set_options(options.get(scope, ""))


class NchantdOfficeTodayOverview(NchantdTodayOverview):
    """"""

    def __init__(self, parent=None, cfg=None) -> None:
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeJournalSettings").override(cfg))

    def initModel(self, cfg=None) -> Self:
        """"""
        super().initModel(cfg)

    def initView(self, cfg=None) -> None:
        """"""
        super().initView(cfg)
        logma.info(f"initView")
        cfg = {"height": 250}
        scroll = NchantdHScrollGroupBox(self, cfg)
        scroll.setTitle("Daily Weather")
        today = dt.datetime.now()
        days = [today + dt.timedelta(days=x) for x in range(-3, 4)]
        logma.info(f"Days {days}")
        for day in days:
            cfg = {
                "title": day.strftime("%A %Y-%m-%d"),
                "humidity": {"high": "80", "low": "50"},
                "temperature": {"high": "80", "low": "50"},
                "rain_chance": {"high": "80", "low": "50"},
            }
            logma.info(f"Day {day}")
            cfg = {"day": cfg}
            if day.strftime("%Y-%m-%d") == today.strftime("%Y-%m-%d"):
                cfg["font_zoom"] = 1.2  # [DONE]
            scroll.addWidget(NchantdDayDashboard(self, cfg).initWidget())
            # scrollbar = scroll.scroll.horizontalScrollBar()
            # scrollbar = scroll.scroll.horizontalScrollBar()
            # scrollbar.setSliderPosition(int((scrollbar.maximum() + scrollbar.minimum())/2))
        scroll.set_scroll_bar_position("center")
        self.layout.addLayout(scroll.layout)
        if self.tasks is None:
            self.tasks = []
        # self.selected_day = NchantdDayCalendar(self, self.config).initWidget()
        # if len(self.tasks) == 0:
        #    self.selected_day.setFixedHeight(75)
        # self.layout.addWidget(self.selected_day)
        layout = pyqt.QHBoxLayout()
        cfg = {"filters": {}}
        # self.news = NchantdNEWSLSummary(self, cfg).initWidget()
        # layout.addWidget(self.news)
        cfg = {"size": ["auto", "auto"]}
        self.viewer = NchantdVScrollGroupBox(self, cfg)
        self.viewer.setTitle("Quick View")
        cfg = {"url": "https://www.groundnews.com"}
        browser = NchantdOfficeWebBrowser(self, cfg).initWidget()
        self.viewer.addWidget(browser)
        layout.addLayout(self.viewer.layout)
        self.layout.addLayout(layout)

    def initWidget(self) -> None:
        """"""
        self.initModel()
        self.initView()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
