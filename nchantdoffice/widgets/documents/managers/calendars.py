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
from condor import condor
from ogma.logma import Logma
from nchantrs.libraries import pyqt
from nchantrs.widgets.calendars.calendars import NchantdCalendar, NchantdDateTimeSelect
from nchantrs.widgets.controls.buttons import NchantdButton
from nchantrs.widgets.controls.checkboxes import NchantdCheckbox
from nchantdoffice.widgets.documents.documents import NchantdOfficeDocument
from nchantrs.widgets.controls.advanced_buttons import NchantdLabeledSpinBox
from nchantrs.widgets.controls.button_groups import NchantdAcceptButtons
from nchantrs.widgets.media.editors.editors import NchantdLabeledEntry
from nchantrs.widgets.media.editors.selectors import NchantdDropDown
from nchantrs.widgets.panes.panes import NchantdPane
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.tables.lists import NchantdList
from nchantrs.widgets.groups import NchantdCollapsableGroup, NchantdGroup
from nchantrs.widgets.annotations import NchantdLabel
from nchantrs.widgets.calendars.timelines import NchantdJournalEditor

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "../_data_", "calendars.yaml")
pxcfg = {}


class NchantdEventPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdEventPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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
        cfg = {"label": f"Start: {dt.datetime.now()}"}
        self.event_start_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.event_start_label, 0, 0)
        cfg = {"label": f"End: {dt.datetime.now()}"}
        self.event_end_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.event_end_label, 1, 0)
        cfg = {"label": f"Alarm: 10 minutes before"}
        self.event_alarm_label = NchantdLabel(self, cfg).initWidget()
        self.layout.addWidget(self.event_alarm_label, 2, 0)
        cfg = {"label": "Task: "}
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
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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
        cfg = {"data": self.config.dikt.get("data", [])}
        cfg["data"].append("Add New Alarm")
        self.layers_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.layers_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdAlarmsEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(self)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdEventRecursionEditPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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
        cfg = {"label": "Alarm Name: "}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        cfg = {
            "layout": "horizontal",
            "label": "Alert ",
            "options": [
                "Minutely",
                "Quarter-Hourly",
                "Hourly",
                "Daily",
                "Weekly",
                "Monthly",
                "Quarter-Yearly",
                "Yearly",
            ],
        }
        self.scope_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.scope_select)
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


class NchantdEventGroup(NchantdWidget):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdEventGroup"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

    def initModel(self, cfg=None):
        """"""
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
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
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdEventsListPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
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

        # if self.events == {}:
        #    self.events = self.app.model.store.get_events()
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
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
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdAlarmsListPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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
        self.layers_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.layers_list)
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
        super().__init__(self)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdTasksListPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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
        cfg = {"data": self.config.dikt.get("data", [])}
        self.layers_list = NchantdList(self, cfg).initWidget()
        layout.addWidget(self.layers_list)
        self.layout.addWidget(group)
        return self

    def initWidget(self):
        """"""
        self.initModel()
        self.initView()
        return self


class NchantdEventRecursionEditPane(NchantdPane):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdEventRecursionEditPane"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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
        cfg = {"label": "Recurrence Name: "}
        self.name_entry = NchantdLabeledEntry(self, cfg).initWidget()
        layout.addWidget(self.name_entry)
        cfg = {
            "layout": "horizontal",
            "label": "Recur ",
            "options": [
                "Minutely",
                "Quarter-Hourly",
                "Hourly",
                "Daily",
                "Weekly",
                "Monthly",
                "Quarter-Yearly",
                "Yearly",
            ],
        }
        self.scope_select = NchantdDropDown(self, cfg).initWidget()
        layout.addWidget(self.scope_select)
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
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeCalendar"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)
        self.calendar = None

    def initModel(self):
        """"""
        super().initModel()
        self.context_menu.get_menu("document_calendar_context")
        return self

    def initView(self, cfg=None):
        """"""
        if cfg is None:
            cfg = {}
        if cfg.get("buttons", None) is None:
            cfg["buttons"] = {}
        options = ["Year", "Quarter Year", "Month", "Week", "Day", "Hour", "Quarter Hour"]
        css_cfg = {
            "label": "Select Calendar Scope: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
            "value": self.get_calendar_scope_select_value(),
            "handler": self.cmd_on_change_scope,
        }
        self.calendar_scope_select = NchantdDropDown(self, css_cfg)
        cfg["buttons"][0] = {
            "name": "select_calendar_scope",
            "type": "dropdown",
            "widget": self.calendar_scope_select,
        }
        options = [
            "Year",
            "Quarter Year",
            "Month",
            "Week",
            "Day",
            "Hour",
            "Quarter Hour",
            "Event",
        ]  # Alter based on scope select ie. year scope can have qy and month

        cus_cfg = {
            "label": "Select Calendar Unit: ",
            "layout": "horizontal",
            "combobox": {"size": ["auto", "auto"], "options": options},
            "value": self.get_calendar_unit_select_value(),
            "handler": self.cmd_select_calendar_unit,
        }
        self.calendar_unit_select = NchantdDropDown(self, cus_cfg)
        cfg["buttons"][1] = {
            "name": "select_calendar_unit",
            "type": "dropdown",
            "widget": self.calendar_unit_select,
        }
        cfg["buttons"][49] = "_insert_stretch"
        super().initView(cfg)
        self.calendar = NchantdCalendar(self).initWidget()
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
        self.set_scope(self.calendar_scope_select.get_value())
        return self

    def cmd_select_calendar_unit(self, event, *args, **kwargs):
        """"""
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

    def get_event_datetime_select_value(self):
        """"""
        datetime_ = dt.datetime.now()
        return datetime_

    def init_drawer_events(self):
        """"""
        items = self.toolbox_config[100].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {"text": "", "layout": "horizontal", "justify": "center"}
        self.new_event_date_select = NchantdDateTimeSelect(self, cfg)
        items[cnt]["widget"] = self.new_event_date_select
        cnt += 1
        if cnt not in items:
            items[cnt] = deepcopy(default_action)
        cfg = {"text": "Create New Event", "layout": "horizontal", "justify": "center"}
        self.new_event_button = NchantdButton(self, cfg)
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

    def init_drawer_event_config(self):
        """"""
        items = self.toolbox_config[200].get("items", {})
        default_action = {"action": "insert_generic_action", "type": "custom"}
        cnt = 0
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "layout": "horizontal",
        }
        self.event_config_accept_button = NchantdAcceptButtons(self, cfg)
        items[cnt]["widget"] = self.event_config_accept_button
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "layout": "horizontal",
            "value": self.get_event_datetime_select_value(),
        }
        self.date_select = NchantdDateTimeSelect(self, cfg)
        items[cnt]["widget"] = self.date_select
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
        cfg = {
            "text": "Event is Required",
            "layout": "horizontal",
            "size": ["auto", "auto"],
        }
        self.event_required_checkbox = NchantdCheckbox(self, cfg)
        items[cnt]["widget"] = self.event_required_checkbox
        cnt += 1
        if cnt not in items:
            items[cnt] = default_action
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
        self.service_connect_button = NchantdButton(self, cfg)
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
        self.toolbox_config[300]["items"] = self.init_drawer_external_calendar_config()
        self.toolbox_config[400]["items"] = self.init_drawer_quickstart()

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
            scope = self.scope
        cfg = {"scope": scope}
        self.calendar = NchantdCalendar(self, cfg).initWidget()
        self.layout.insertWidget(1, self.calendar)
        self.update()


class NchantdOfficeJournalEditor(NchantdJournalEditor):
    """"""

    def __init__(self, parent=None, cfg=None):
        """ """
        super().__init__(parent, cfg)
        self.parent = parent
        self.config.override(condor.Instruct(pxcfg).select("NchantdOfficeJournalEditor"))
        if self.parent:
            self.config.override(parent.config)
        self.config.override(cfg)

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

    def parse(self):
        """"""
        for entry in self.entries:
            # write doc_media entry to table
            pass
        # need to identify the entry
        return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
