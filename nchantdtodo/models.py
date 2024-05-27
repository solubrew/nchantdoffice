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
		
		self.initModel()

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
#		base = [0, 1, 0, 1, 0, 1, 1, 0, 0, 0]#9
		nodes = [
			['1', 'Timeline', 'appnode', 0, 0, 'NTDTimelineTabSet'] + self.nodebase,
			['2', 'Concern', 'appnode', 0, 0, 'NTDConcernTabSet'] + self.nodebase,
			['3', 'History', 'appnode', 0, 0, 'NTDHistoryTabSet'] + self.nodebase
		]
		if log: logma.info(f'SRC {self.src}')
		# for acct in email_accts:
		# 	nodes.append()
		# for contact in contacts:
		# 	nodes.append()
		df = qpandas.DataFrame(nodes, columns=self.nodecolumns)
		if log: logma.info(f"TRNODES_DF {trnodes_df}")
		df = df[~df['nid'].isin(trnodes_df['nid'].values.tolist())]
		df['uuid'] = df['nid'].apply(lambda x: uuid.UUID(str(uuid.uuid4())).hex)
		df.reset_index(inplace=True, drop=True)
		if log: logma.info(f"DF {df}")
		if not df.empty:
			self.src.docs['db'].write({'trnodes': df})
		tabs = []
		#base = [0, 1, 1, 1, 0]
		for node in nodes:
			#TODO: build out tid identification
			tabs += getattr(self, f'init{node[5]}Model')(self.tabbase)
		if log: logma.info(f'TABS {tabs}')
		tabs_df = qpandas.DataFrame(tabs, columns=self.tabcolumns)
		tabs_df['uuid'] = tabs_df['name'].apply(lambda x: uuid.UUID(str(uuid.uuid4())).hex)
		if not tabs_df.empty:
			self.src.docs['db'].write({'tabs': tabs_df})
		NchantdTreeGenerator().genYearMonthTreeData(self.src, 0, 4, 16)
		return self

	def initModel(self):
		self.buildNodes()
		super().initModel()
		return self

	def initNTDActionTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDActionTab'
		data = j.dumps({'': ''})
		tabs.append(['Actions Summary', widget, data, 1, 0] + base)
		wiget = 'nchantrs.widgets.dashboards.NchantdNEWSTab'
		data = j.dumps({})
		tabs.append(['NEWS', widget, data, 1, 1] + base)
		return tabs
	
	def initNTDContactTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDContactTab'
		data = j.dumps({'': ''})
		tabs.append(['Contact', widget, data, 9, 0] + base)
		return tabs
	
	def initNTDContactsLevelTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDContactLevelSummaryTab'
		data = j.dumps({'': ''})
		tabs.append(['Contacts Level Summary', widget, data, 9, 0] + base)
		return tabs
	
	def initNTDContactsTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDContactsTab'
		data = j.dumps({'': ''})
		tabs.append(['Contacts Summary', widget, data, 9, 0] + base)
		return tabs

	def initNTDTimelineTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDeMailTab'
		data = j.dumps({'': ''})
		tabs.append(['eMail Summary', widget, data, 7, 0] + base)
		return tabs

	def initNTDConcernTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDeMailTab'
		data = j.dumps({'': ''})
		tabs.append(['eMail Summary', widget, data, 7, 0] + base)
		return tabs

	def initNTDHistoryTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDeMailTab'
		data = j.dumps({'': ''})
		tabs.append(['eMail Summary', widget, data, 7, 0] + base)
		return tabs

	def initNTDeMailTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDeMailTab'
		data = j.dumps({'': ''})
		tabs.append(['eMail Summary', widget, data, 7, 0] + base)
		return tabs
	
	def initNTDFundTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDFundSummaryTab'
		data = j.dumps({'': ''})
		tabs.append(['Fund Summary', widget, data, 6, 0] + base)
		return tabs
	
	def initNTDNeedActionTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDNeedActionTab'
		data = j.dumps({'': ''})
		tabs.append(['Need Actions Summary', widget, data, 2, 0] + base)
		widget = 'nchantrs.packages.NTDs.widgets.NTDTaskSplitterTab'
		data = j.dumps({'': ''})
		tabs.append(['Split Tasks', widget, data, 2, 1] + base)
		widget = 'nchantrs.packages.NTDs.widgets.NTDDelegationTab'
		data = j.dumps({'': ''})
		tabs.append(['Delegate Tasks', widget, data, 2, 2] + base)
		return tabs
	
	def initNTDWaitingOnTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDWaitingOnTab'
		data = j.dumps({'': ''})
		tabs.append(['Waiting On Summary', widget, data, 3, 0] + base)
		return tabs
	
	def initNTDJournalTabSetModel(self, base):
		""" """
		tabs = []
		widget = 'nchantrs.packages.NTDs.widgets.NTDJournalTab'
		data = j.dumps({'': ''})
		tabs.append(['Journal Summary', widget, data, 4, 0] + base)
		return tabs
	
	def initNTDCalendarTabSetModel(self, base):
		""" """
		data = j.dumps({'': ''})
		tabs = [
			['This Week', 'nchantrs.widgets.calendars.NchantdWeekCalendar', data, 5, 0] + base,
			['Next Week', 'nchantrs.widgets.calendars.NchantdWeekCalendar', data, 5, 1] + base,
			['Next Month', 'nchantrs.widgets.calendars.NchantdMonthCalendar', data, 5, 2] + base,
			['Yearly Calendar', 'nchantrs.widgets.calendars.NchantdYearCalendar', data, 5, 3] + base,
			['Events', 'nchantrs.widgets.NchantdEventsList', data, 5, 4] + base
		]
		return tabs
	
	def initNTDProcureTabSetModel(self, base):
		""" """
		data = j.dumps({'': ''})
		tabs = []
		tabs.append(['Procure', 'nchantrs.widgets.editors.NchantdDocEditor', data, 8, 0] + base)
		return tabs

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