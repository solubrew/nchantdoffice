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

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", "calendars.yaml")


def get_scope_options():
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

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventPane").override(cfg))
        self.event_start_label = None
        self.event_end_label = None
        self.event_alarm_label = None
        self.event_task_label = None

    def initModel(self, cfg=None):
        """Initialize the today overview model."""
        super().initModel(cfg)
        self.tasks = []
        return self
        return self

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdAlarmsListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdAlarmsListPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_alarms_list(self):
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

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventRecursionEditPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_name_changed(self):
        """"""
        # TODO implement method

    def cmd_scope_changed(self):
        """Handle alarm scope/interval change."""
        if hasattr(self, "alarm_scope_select"):
            self.config.dikt["scope"] = self.alarm_scope_select.get_value()

    def get_name(self):
        """Get the alarm name."""
        return self.config.dikt.get("name", "")

    def get_current_scope(self):
        """Get the current alarm scope/interval."""
        return self.config.dikt.get("scope", "Daily")


class NchantdEventGroup(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventGroup").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdEventsListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventsListPane").override(cfg))
        self.events = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        self.events = self.config.dikt.get("events", {})
        self.events = {
            "SocialCast": {
                "alarm": {"set": True, "start_dttm": dt.datetime.now() + dt.timedelta(days=1)},
                "task": {"set": True, "start_dttm": dt.datetime.now() + dt.timedelta(days=1)},
                "event_start_dttm": dt.datetime.now(),
                "event_end_dttm": dt.datetime.now() + dt.timedelta(days=1),
            },
            "SocialCast1": {
                "alarm": {"set": True, "start_dttm": dt.datetime.now()},
                "task": {"set": True, "start_dttm": dt.datetime.now()},
                "event_start_dttm": dt.datetime.now(),
                "event_end_dttm": dt.datetime.now() + dt.timedelta(days=1),
            },
        }
        return self

    def initView(self, cfg=None):
        """"""
        cfg = cfg or {}
        cfg["layout"] = "vertical"
        super().initView(cfg)
        for event in self.events:
            self.events[event] = NchantdEventGroup(self, self.events[event]).initWidget()
            self.layout.addWidget(self.events[event])
        self.layout.addStretch()
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdRecurrencesListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdRecurrencesListPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdTasksListPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdTasksListPane").override(cfg))
        self.tasks_list = None

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def get_tasks(self):
        """Get list of tasks from model."""
        return self.config.dikt.get("tasks", [])


class NchantdEventRecursionEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdEventRecursionEditPane").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)
        return self

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_accept_buttons(self):
        """Handle accept/confirm button press for recurrence settings."""
        logma.info(f"Recurrence settings accepted: {self.config.dikt}")
        self.parent.update() if hasattr(self, "parent") else None

    def cmd_name_change(self):
        """Handle recurrence name change."""
        if hasattr(self, "name_entry"):
            self.config.dikt["name"] = self.name_entry.get_value()

    def cmd_end_datetime_changed(self):
        """Handle recurrence end datetime change."""
        if hasattr(self, "end_date_select"):
            self.config.dikt["end_datetime"] = self.end_date_select.get_value()

    def cmd_end_after_changed(self):
        """Handle recurrence end-after count change."""
        if hasattr(self, "end_multiples_set"):
            self.config.dikt["end_after"] = self.end_multiples_set.get_value()

    def cmd_recur(self):
        """Handle recurrence command trigger."""
        if hasattr(self, "scope_select"):
            self.config.dikt["recur"] = self.scope_select.get_value()

    def cmd_recur_changed(self):
        """Handle recurrence scope/interval change."""
        if hasattr(self, "scope_select"):
            self.config.dikt["recur"] = self.scope_select.get_value()

    def get_end_datetime(self):
        """Get the recurrence end datetime."""
        return self.config.dikt.get("end_datetime", dt.datetime.now())

    def get_end_after(self):
        """Get the recurrence end-after count."""
        return self.config.dikt.get("end_after", 1)

    def get_name(self):
        """Get the recurrence name."""
        return self.config.dikt.get("name", "")

    def get_recur(self):
        """Get the recurrence scope/interval."""
        return self.config.dikt.get("recur", "Daily")

    def get_scope_options(self):
        """Get available recurrence scope options."""
        return get_scope_options()


class NchantdOfficeCalendar(NchantdOfficeDocument):
    """ ""Calendar document - implements PyfficeCalendar"""

    PYTYPE = "calendar"

    @classmethod
    def get_pyffice_tools(cls):
        """Get toolbox tools for calendar documents"""
        return [
            {"id": "views", "icon": "calendar", "label": "Views", "method": "set_scope"},
            {"id": "timezone", "icon": "globe", "label": "Time Zone", "method": "set_timezone"},
            {"id": "reminders", "icon": "bell", "label": "Reminders", "method": "manage_reminders"},
            {"id": "events", "icon": "event", "label": "Events", "method": "manage_events"},
            {"id": "tasks", "icon": "task", "label": "Tasks", "method": "manage_tasks"},
            {"id": "gantt", "icon": "chart", "label": "Gantt", "method": "show_gantt"},
        ]

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__("Nchantd Calendar", parent, cfg)
        self.parent = parent
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeCalendar").override(cfg))
        self.calendar = None

    def initModel(self):
        """"""
        super().initModel()
        cfg = {}
        self.document = self.app.model.codex.init_calendar(cfg)
        self.document.load_document()
        self.context_menu.get_menu("document_calendar_context")
        return self

    def initView(self, cfg=None):
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
        super().initView(cfg)
        cfg = {}
        self.calendar = NchantdCalendar(self, cfg).initWidget()
        self.layout.addWidget(self.calendar)
        self.layout.setSpacing(3)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self

    def cmd_on_change_scope(self, event, *args, **kwargs):
        """"""
        scope = self.calendar_scope_select.get_value()
        self.set_scope(scope)
        self.update_unit_options(scope)
        return self

    def cmd_config_accept(self):
        """Handle config accept button press."""
        logma.info(f"Calendar config accepted: {self.config.dikt}")
        self.update() if hasattr(self, "update") else None

    def cmd_select_calendar_unit(self, event, *args, **kwargs):
        """Handle calendar unit selection change."""
        unit = self.calendar_unit_select.get_value()
        self.set_calendar_unit_select_value(unit)
        logma.info(f"Calendar unit changed to: {unit}")
        return self

    def create_data_table(self):
        """"""
        df = super().create_data_table()
        columns = []
        data = []
        df = DataFrame(data, columns=columns)
        return df

    def get_calendar_scope_select_value(self):
        """"""
        value = self.config.dikt.get("calendar_scope_select_value", "Week")
        return value

    def get_calendar_unit_select_value(self):
        """"""
        return self.config.dikt.get("calendar_unit_select_value", "Day")

    def get_content(self):
        """"""
        return {}

    def get_event_datetime_select_value(self):
        """"""
        datetime_ = dt.datetime.now()
        return datetime_

    def init_drawer_events(self):
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

    def cmd_create_new_event(self, event=None, *args, **kwargs):
        """Handle create new event button press."""
        logma.info("Creating new calendar event")
        if hasattr(self, "new_event_date_select"):
            event_dt = self.new_event_date_select.get_value()
            logma.info(f"New event datetime: {event_dt}")
        return self

    def cmd_event_datetime_change(self):
        """"""
        # TODO: implement method

    def init_drawer_event_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {"layout": "horizontal", "handler": self.cmd_config_accept}
        self.event_config_accept_button = NchantdAcceptButtons(self, cfg)
        items[cnt]["widget"] = self.event_config_accept_button
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "layout": "horizontal",
            "value": self.get_event_datetime_select_value(),
            "handler": self.cmd_event_datetime_change(),
        }
        self.date_select = NchantdDateTimeSelect(self, cfg)
        items[cnt]["widget"] = self.date_select
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "text": "Event is Required",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.event_required_checkbox = NchantdCheckboxWidget(self, cfg)
        items[cnt]["widget"] = self.event_required_checkbox
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "label": "Alarms List: ",
            "layout": "horizontal",
        }
        self.event_alarms_list = NchantdAlarmsListPane(self, cfg)
        items[cnt]["widget"] = self.event_alarms_list
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "label": "Edit Alarm: ",
            "layout": "horizontal",
        }
        self.event_recurrence_edit_pane = NchantdAlarmsEditPane(self, cfg)
        items[cnt]["widget"] = self.event_recurrence_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "label": "Recurrences: ",
            "layout": "horizontal",
        }
        self.event_recurrences_pane = NchantdRecurrencesListPane(self, cfg)
        items[cnt]["widget"] = self.event_recurrences_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "label": "Edit Recurrence: ",
            "layout": "horizontal",
        }
        self.event_recurrence_edit_pane = NchantdEventRecursionEditPane(self, cfg)
        items[cnt]["widget"] = self.event_recurrence_edit_pane
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {
            "text": "Tasks: ",
            "layout": "horizontal",
        }
        self.event_tasks_pane = NchantdTasksListPane(self, cfg)
        items[cnt]["widget"] = self.event_tasks_pane
        return items

    def cmd_event_datetime_change(self):
        """Handle event datetime selection change."""
        if hasattr(self, "date_select"):
            self.config.dikt["event_datetime"] = self.date_select.get_value()
        return self

    def init_drawer_external_calendar_config(self):
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
        }
        self.calendar_service_select = NchantdDropDown(self, cfg)
        items[cnt]["widget"] = self.calendar_service_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "label": "Name: ",
            "layout": "horizontal",
        }
        self.calendar_account_name = NchantdLabeledEntry(self, cfg)
        items[cnt]["widget"] = self.calendar_account_name
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "text": "Connect to Service: ",
            "layout": "horizontal",
        }
        self.service_connect_button = NchantdButtonWidget(self, cfg)
        items[cnt]["widget"] = self.service_connect_button
        return items

    def init_drawer_quickstart(self):
        """"""
        items = self.toolbox_config[400].get("items", {})
        return items

    def init_toolbox(self):
        """"""
        super().init_toolbox()
        self.toolbox_config[100]["items"] = self.init_drawer_events()
        self.toolbox_config[200]["items"] = self.init_drawer_event_config()
        # PUSH to 0.0.3
        # self.toolbox_config[300]["items"] = self.init_drawer_external_calendar_config()
        # self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

    def set_calendar_scope_select_value(self, value):
        """"""
        self.config.dikt["calendar_scope_select_value"] = value
        return self

    def set_calendar_unit_select_value(self, value):
        """"""
        self.config.dikt["calendar_unit_select_value"] = value
        return self

    def set_scope(self, scope):
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

    def update_unit_options(self, scope):
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

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.config.override(kahndor.Instruct(pxcfg).select("NchantdOfficeJournalSettings").override(cfg))

    def initModel(self, cfg=None):
        """"""
        super().initModel(cfg)

    def initView(self, cfg=None):
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

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
