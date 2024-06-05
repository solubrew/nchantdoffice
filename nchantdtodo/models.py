# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid: <^(UUID)^>
	name:
	description: >
	expirary: <[expiration]>
	version: <[version]>
	path: <[LEXIvrs]>
	outline: <[outline]>
	authority: document|this
	security: sec|lvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
from os.path import abspath, dirname, exists, join
import uuid

# ===============================================================================||
import simplejson as j
from pandas import DataFrame

# ===============================================================================||
from condor import condor  # ||
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.models import models, treemodels
from nchantrs.dstruct.trees import NchantdTreeGenerator
from nchantrs.libraries import qpandas
from ogma.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), '')  # ||
log = False
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, '_data_', 'models.yaml')

class NTDAppModel(NchantdCloakModel):
	""" """
	
	def __init__(self, parent=None, cfg={}):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NTDAppModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: logma.info(f"NTDAppModel Config\n {self.config.dikt.keys()}")
		super(NTDAppModel, self).__init__(parent)

	def buildModel(self):
		""" """
		return self

class NTDTreeModel(treemodels.NchantdTreeModel):
	""" """
	
	def __init__(self, parent=None, root=None, cfg={}):
		""" """
		self.config = condor.instruct(pxcfg).select('NTDTreeModel')
		self.config.override(cfg)
		if log: logma.info(f'TODOTreeModel\n {parent.src}')
		if parent:
			self.config.override(parent.config)
		self.src = parent.src
		super(NTDTreeModel, self).__init__(parent, root, cfg)
		if log: logma.info(f'TODOTreeModel\n {self.src}')
		
		self.nodes = []
		self.tabsets = self.config.dikt['gui']['desktop']['tabsets']
		self.base = [0, 0, 1, 1, 1, 1, 0, 0]
		self.tbase = ['center', 0, 1, 1]
		self.src = self.parent.src
		self.name = 'nchantdtodos'
		#nid = models.getLastNodeId(self.src, self.name)
		self.rows, self.tabs = [], []
		
#		self.initModel()

	def buildNodes(self):
		""""""
		pos = 0
		#nid = models.getLastNodeId(self.src, 'nchantdtodos')
		nid = 0
		nodes = self.config.dikt['gui']['desktop']['nodes']
		for node in nodes.keys():
			if nodes[node]:
				nid = getattr(self, f"build{node}Nodes")(nid, 0, pos)
				pos += 1

		#self.tabs += self.buildRightTabSet()
		super().buildNodes()

		return self

	def buildTimelineNodes(self, nid, pid, pos):
		""""""
		tset = 'NTDTimelineTabSet'
		nid = self.buildNode(nid, 'Timeline', 'appnode', pid, pos, tset)
		return nid

	def buildConcernsNodes(self, nid, pid, pos):
		""""""
		tset = 'NTDConcernTabSet'
		nid = self.buildNode(nid, 'Timeline', 'appnode', pid, pos, tset)
		return nid

	def buildHistoryNodes(self, nid, pid, pos):
		""""""
		tset = 'NTDHistoryTabSet'
		nid = self.buildNode(nid, 'Timeline', 'appnode', pid, pos, tset)
		return nid

	def initData(self):
		""" """
		self.genTreeNodes()
	
	def genTreeNodes(self):
		data = next(self.src.docs['db'].read({'table': ['trnodes', 'tabs']})).dikt
		trnodes_df = qpandas.DataFrame(data['trnodes']['records'], columns=data['trnodes']['columns'])
		if log: logma.info(f"DATA {data}")
		nodes = [
			['1', 'Action', 'appnode', 0, 0, 'NTDActionTabSet'] + self.nodebase,
			['2', 'Concern', 'appnode', 0, 1, 'NTDConcernTabSet'] + self.nodebase,
			['3', 'History', 'appnode', 0, 2, 'NTDHistoryTabSet'] + self.nodebase
		]
		if log: logma.info(f'SRC {self.src}')
		df = qpandas.DataFrame(nodes, columns=self.nodecolumns)
		if log: logma.info(f"TRNODES_DF {trnodes_df}")
		df = df[~df['nid'].isin(trnodes_df['nid'].values.tolist())]
		df['uuid'] = df['nid'].apply(lambda x: uuid.UUID(str(uuid.uuid4())).hex)
		df.reset_index(inplace=True, drop=True)
		if log: logma.info(f"DF {df}")
		if not df.empty:
			self.src.docs['db'].write({'trnodes': df})
		tabs = []
		for node in nodes:
			#TODO: build out tid identification...this is a larger problem in matching nodes being generated
			#
			tabs += getattr(self, f'init{node[5]}Model')(node[0])
		if log: logma.info(f'TABS {tabs}')
		tabs_df = qpandas.DataFrame(tabs, columns=self.tabcolumns)
		data = next(self.src.docs['db'].read({'table': ['tabs']})).dikt
		db_tabs_df = qpandas.DataFrame(data['tabs']['records'], columns=data['tabs']['columns'])
		tabs_df['uuid'] = tabs_df['name'].apply(lambda x: uuid.UUID(str(uuid.uuid4())).hex)
		if log: logma.info(f"Columns {tabs_df.columns}")
		if log: logma.info(f"Tabs DF\n{tabs_df}")
		if log: logma.info(f"Tabs DF\n{db_tabs_df}")
		#TODO: this needs to be name and parent
		tabs_df = tabs_df[~tabs_df['name'].isin(db_tabs_df['name'].values.tolist())]
		
		#TODO: This should be a function of a base model in nchantrs and check against already stored tabs
		if not tabs_df.empty:
			self.src.docs['db'].write({'tabs': tabs_df})
			
		NchantdTreeGenerator(self, trnodes_df).genYearMonthTreeData(self.src, 0, 1, 4)
		return self

	def initModel(self):
		self.buildNodes()
		super().initModel()
		return self

	def initNTDActionTabSetModel(self, pid):
		""" """
		tabs = []
		data = j.dumps({'': ''})
		tabs.append(['Actions', 'nchantdtodo.widgets.NTDDailyTaskTrackerTab', data, pid, 0] + self.tabbase)
		data = j.dumps({})
		tabs.append(['NEWS', 'nchantrs.widgets.dashboards.NchantdNEWSTab', data, pid, 1] + self.tabbase)
		data = j.dumps({})
		tabs.append(['Daily Tracker', 'nchantdtodo.widgets.NTDDaily15MinTrackerTab', data, pid, 2] + self.tabbase)
		data = j.dumps({})
		tabs.append(['Weekly Tracker', 'nchantdtodo.widgets.NTDWeekly1DayTrackerTab', data, pid, 3] + self.tabbase)
		data = j.dumps({})
		tabs.append(['New Concern', 'nchantdtodo.widgets.NTDAddConcernTab', data, pid, 5] + self.tabbase)
		data = j.dumps({})
		tabs.append(['New Event', 'nchantdtodo.widgets.NTDAddEventTab', data, pid, 5] + self.tabbase)
		data = j.dumps({})
		tabs.append(['New Resource', 'nchantdtodo.widgets.NTDAddResourceTab', data, pid, 5] + self.tabbase)
		data = j.dumps({})
		tabs.append(['New Task', 'nchantdtodo.widgets.NTDAddTaskTab', data, pid, 5] + self.tabbase)
		return tabs

	def initNTDConcernTabSetModel(self, pid):
		""" """
		tabs = []
		data = j.dumps({})
		tabs.append(['Projects Summary', 'nchantdtodo.widgets.NTDProjectsSummaryTab', data, pid, 0] + self.tabbase)
		data = j.dumps({})
		tabs.append(['Operations Summary', 'nchantdtodo.widgets.NTDOperationsSummaryTab', data, pid, 1] + self.tabbase)
		data = j.dumps({})
		tabs.append(['Events Admin', 'nchantdtodo.widgets.NTDAdministrateEventsTab', data, pid, 4] + self.tabbase)
		data = j.dumps({'': ''})
		tabs.append(['Concerns Admin', 'nchantdtodo.widgets.NTDAdministrateConcernsTab', data, pid, 2] + self.tabbase)
		data = j.dumps({})
		tabs.append(['New Concern', 'nchantdtodo.widgets.NTDAddConcernTab', data, pid, 3] + self.tabbase)
		data = j.dumps({})
		tabs.append(['Resource Admin', 'nchantdtodo.widgets.NTDAdministrateResourcesTab', data, pid, 4] + self.tabbase)
		data = j.dumps({})
		tabs.append(['New Resource', 'nchantdtodo.widgets.NTDAddResourceTab', data, pid, 5] + self.tabbase)
		return tabs

	def initNTDHistoryTabSetModel(self, pid):
		""" """
		tabs = []
		data = j.dumps({'': ''})
		tabs.append(['Summary', 'nchantd.widgets.NTDHistoryTab', data, pid, 0] + self.tabbase)
		data = j.dumps({'': ''})
		tabs.append(['Recent', 'nchantd.widgets.NTDRecentCompletedTasksTab', data, pid, 1] + self.tabbase)
		return tabs

	def initNTDJournalTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDJournalTab'
		data = j.dumps({'': ''})
		tabs.append(['Journal Summary', widget, data, 4, 0] + self.tabbase)
		return tabs
	
	def initNTDCalendarTabSetModel(self, base):
		""" """
		data = j.dumps({'': ''})
		tabs = [
			['This Week', 'nchantrs.widgets.calendars.NchantdWeekCalendar', data, 5, 0] + self.tabbase,
			['Next Week', 'nchantrs.widgets.calendars.NchantdWeekCalendar', data, 5, 1] + self.tabbase,
			['Next Month', 'nchantrs.widgets.calendars.NchantdMonthCalendar', data, 5, 2] + self.tabbase,
			['Yearly Calendar', 'nchantrs.widgets.calendars.NchantdYearCalendar', data, 5, 3] + self.tabbase,
			['Events', 'nchantrs.widgets.NchantdEventsList', data, 5, 4] + self.tabbase
		]
		return tabs

	def updateTimeline(self):
		""""""
		self.now = dt.datetime.now()

class NTDConcernModel():
	""""""
	def __init__(self):
		""""""


class NTDDailyTrackerModel():
	""""""
	
	def __init__(self):
		""""""


class NTDTaskModel():
	""""""
	
	def __init__(self):
		""""""

class NTDEventModel():
	""""""
	
	def __init__(self):
		""""""


class NTDprojectModel():
	""""""
	
	def __init__(self):
		""""""


class NTDProjectsModel():
	""""""
	
	def __init__(self):
		""""""


class NTDOperationModel():
	""""""
	
	def __init__(self):
		""""""


class NTDOperationsModel():
	""""""
	
	def __init__(self):
		""""""


class NTDSplitTaskModel():
	""""""
	
	def __init__(self):
		""""""


class NTDCalendarModel():
	""""""
	
	def __init__(self):
		""""""