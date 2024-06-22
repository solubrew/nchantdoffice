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
import datetime as dt

# ===============================================================================||
import simplejson as j
from pandas import DataFrame

# ===============================================================================||
from condor import condor  # ||
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.models import models, treemodels
from nchantrs.models.tabsetmodels import NchantdTabSetModel
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
	"""Nchantd Todo Tree Model"""
	def __init__(self, parent=None, root=None, cfg={}):
		"""An Outlined but dynamic set of tree nodes based on data from the database"""
		self.config = condor.instruct(pxcfg).select('NTDTreeModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDTreeModel, self).__init__(parent, root, 'nchantdtodos')
		if log: logma.info(f'TODOTreeModel\n {self.src}')
		self.today = None

	def initData(self):
		""" """
		self.genTreeNodes()
	


	def initModel(self):
		super().initModel()
		self.buildNodes()
		return self
	
	def setToday(self, nid):
		""""""
		self.now = dt.datetime.now()
		if self.today != self.now.strftime('%Y-%m-%d'):
			self.updateActionNode(nid)
		self.today = self.now.strftime('%Y-%m-%d')
		return self
	
	def updateActionNode(self, nid):
		"""Dynamicaly change the child nodes of Action based on the current date.
		children nodes:
			todays_date:
			need to get current children of action node
		"""
		
		self.deleteChildren(1)
		logma.info(f"Create Today Node")
		self.addNode(nid, self.today, 'livenode', 1, 0, self.nodebase, 'NTDActionTabSet', 1)
		self.addTab()
		return self
	
	def updateTimeline(self):
		""""""
		self.now = dt.datetime.now()
		return self


class NTDTabSetModel(NchantdTabSetModel):
	""""""
	def __init__(self):
		""""""
		self.config = condor.instruct(pxcfg).select('NTDTabSetModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDTabSetModel, self).__init__(parent, root, cfg, '')

	def initModel(self):
		""""""
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
		tabs.append(['Summary', 'nchantdtodo.widgets.NTDHistoryTab', data, pid, 0] + self.tabbase)
		data = j.dumps({'': ''})
		tabs.append(['Recent', 'nchantdtodo.widgets.NTDRecentCompletedTasksTab', data, pid, 1] + self.tabbase)
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


class NTDConcernModel():
	""""""
	def __init__(self):
		""""""

	def deleteConcern(self):
		""""""
	
	def getConcerns(self):
		""""""
	
	def newConcern(self):
		""""""

	def selectConcern(self):
		""""""

	def updateConcern(self):
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