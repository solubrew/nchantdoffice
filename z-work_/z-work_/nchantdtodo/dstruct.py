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

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


def setupNodes():
    """"""


def setupTabs():
    """
    Sets up tabs in the application by comparing existing tabs in the database with the provided tabs list.
    If a tab does not exist in the database, it is added.

    :return: None
    """

    data = j.dumps({})
    tabs.append(["Projects Summary", "nchantdtodo.widgets.NTDProjectsSummaryTab", data, pid, 0] + self.tabbase)
    data = j.dumps({})
    tabs.append(["Operations Summary", "nchantdtodo.widgets.NTDOperationsSummaryTab", data, pid, 1] + self.tabbase)
    data = j.dumps({})
    tabs.append(["Events Admin", "nchantdtodo.widgets.NTDAdministrateEventsTab", data, pid, 4] + self.tabbase)
    data = j.dumps({"": ""})
    tabs.append(["Concerns Admin", "nchantdtodo.widgets.NTDAdministrateConcernsTab", data, pid, 2] + self.tabbase)
    data = j.dumps({})
    tabs.append(["New Concern", "nchantdtodo.widgets.NTDAddConcernTab", data, pid, 3] + self.tabbase)
    data = j.dumps({})
    tabs.append(["Resource Admin", "nchantdtodo.widgets.NTDAdministrateResourcesTab", data, pid, 4] + self.tabbase)
    data = j.dumps({})
    tabs.append(["New Resource", "nchantdtodo.widgets.NTDAddResourceTab", data, pid, 5] + self.tabbase)
    data = j.dumps({"": ""})
    tabs.append(["Actions", "nchantdtodo.widgets.NTDDailyTaskTrackerTab", data, pid, 0] + self.tabbase)
    data = j.dumps({})
    tabs.append(["NEWS", "nchantrs.widgets.dashboards.NchantdNEWSTab", data, pid, 1] + self.tabbase)
    data = j.dumps({})
    tabs.append(["Daily Tracker", "nchantdtodo.widgets.NTDDaily15MinTrackerTab", data, pid, 2] + self.tabbase)
    data = j.dumps({})
    tabs.append(["Weekly Tracker", "nchantdtodo.widgets.NTDWeekly1DayTrackerTab", data, pid, 3] + self.tabbase)
    data = j.dumps({})
    tabs.append(["New Concern", "nchantdtodo.widgets.NTDAddConcernTab", data, pid, 5] + self.tabbase)
    data = j.dumps({})
    tabs.append(["New Event", "nchantdtodo.widgets.NTDAddEventTab", data, pid, 5] + self.tabbase)
    data = j.dumps({})
    tabs.append(["New Resource", "nchantdtodo.widgets.NTDAddResourceTab", data, pid, 5] + self.tabbase)
    data = j.dumps({})
    tabs.append(["New Task", "nchantdtodo.widgets.NTDAddTaskTab", data, pid, 5] + self.tabbase)
    data = j.dumps({"": ""})
    tabs.append(["Summary", "nchantdtodo.widgets.NTDHistoryTab", data, pid, 0] + self.tabbase)
    data = j.dumps({"": ""})
    tabs.append(["Recent", "nchantdtodo.widgets.NTDRecentCompletedTasksTab", data, pid, 1] + self.tabbase)

    widget = "nchantrs.packages.NTDs.widgets.NTDJournalTab"
    data = j.dumps({"": ""})
    tabs.append(["Journal Summary", widget, data, 4, 0] + self.tabbase)
    data = j.dumps({"": ""})
    tabs = [
        ["This Week", "nchantrs.widgets.calendars.NchantdWeekCalendar", data, 5, 0] + self.tabbase,
        ["Next Week", "nchantrs.widgets.calendars.NchantdWeekCalendar", data, 5, 1] + self.tabbase,
        ["Next Month", "nchantrs.widgets.calendars.NchantdMonthCalendar", data, 5, 2] + self.tabbase,
        ["Yearly Calendar", "nchantrs.widgets.calendars.NchantdYearCalendar", data, 5, 3] + self.tabbase,
        ["Events", "nchantrs.widgets.NchantdEventsList", data, 5, 4] + self.tabbase,
    ]

    tabs_df = qpandas.DataFrame(tabs, columns=self.tabcolumns)
    data = next(self.src.docs["db"].read({"table": ["tabs"]})).dikt
    db_tabs_df = qpandas.DataFrame(data["tabs"]["records"], columns=data["tabs"]["columns"])
    tabs_df["uuid"] = tabs_df["name"].apply(lambda x: uuid.UUID(str(uuid.uuid4())).hex)
    if log:
        logma.info(f"Columns {tabs_df.columns}")
    if log:
        logma.info(f"Tabs DF\n{tabs_df}")
    if log:
        logma.info(f"Tabs DF\n{db_tabs_df}")
    # TODO: this needs to be name and parent
    tabs_df = tabs_df[~tabs_df["name"].isin(db_tabs_df["name"].values.tolist())]

    # TODO: This should be a function of a base model in nchantrs and check against already stored tabs
    if not tabs_df.empty:
        self.src.docs["db"].write({"tabs": tabs_df})


def genTreeNodes(self):
    """
    :param self: The current instance of the object.
    :return: Returns the current instance of the object.

    The `genTreeNodes` method generates tree nodes for the given instance of the object. It retrieves data from
    the 'trnodes' and 'tabs' tables of the `docs` attribute within the `src` attribute of the instance. It uses
    this data to create a `trnodes_df` DataFrame using the qpandas library.
    It initializes the `icon` variable and creates a list of nodes with specific information. Each node consists
    of several elements, including a unique identifier generated using the `uuid.UUID(str(uuid.uuid4())).hex`
    method. The method then logs the retrieved data, the `src` attribute, and the `nodecolumns` attribute if
    the `log` flag is set to True. It creates a DataFrame `df` using the nodes list and columns from the `
    nodecolumns` attribute. It filters out nodes that already exist in the `trnodes_df` DataFrame. It also
    adds a unique identifier to each node using the `uuid.UUID(str(uuid.uuid4())).hex` method. If the `df`
    DataFrame is not empty, it writes the data to the 'trnodes' table of the `docs` attribute within the `src`
    attribute. The method then generates a `nid` using the `NchantdTreeGenerator` class and its
    `genYearMonthTreeData` method, passing in the `src` attribute, and specific parameters. It sets the current
    date as today using the `setToday` method of the current instance. Finally, the method returns the current
    instance of the object.
    """
    data = next(self.src.docs["db"].read({"table": ["trnodes", "tabs"]})).dikt
    trnodes_df = qpandas.DataFrame(data["trnodes"]["records"], columns=data["trnodes"]["columns"])
    if log:
        logma.info(f"DATA {data}")
    icon = ""
    nodes = [
        ["1", icon, "Action", "appnode", 0, 0, "NTDActionTabSet"] + self.nodebase + [uuid.UUID(str(uuid.uuid4())).hex],
        ["2", icon, "Concern", "appnode", 0, 1, "NTDConcernTabSet"]
        + self.nodebase
        + [uuid.UUID(str(uuid.uuid4())).hex],
        ["3", icon, "Timeline", "appnode", 0, 2, "NTDHistoryTabSet"]
        + self.nodebase
        + [uuid.UUID(str(uuid.uuid4())).hex],
    ]
    if log:
        logma.info(f"SRC {self.src}")
    logma.info(f"Columns {self.nodecolumns}")
    df = qpandas.DataFrame(nodes, columns=self.nodecolumns)
    if log:
        logma.info(f"TRNODES_DF {trnodes_df}")
    df = df[~df["nid"].isin(trnodes_df["nid"].values.tolist())]
    df["uuid"] = df["nid"].apply(lambda x: uuid.UUID(str(uuid.uuid4())).hex)  # TODO: upgrade to 7 or 8
    df.reset_index(inplace=True, drop=True)
    if log:
        logma.info(f"DF {df}")
    if not df.empty:
        self.src.docs["db"].write({"trnodes": df})
    # TODO: need to create a node for today and then transfer information to the timeline node for that date
    nid = NchantdTreeGenerator(self, trnodes_df).genYearMonthTreeData(self.src, 0, 3, 4)
    self.setToday(nid)
    return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
