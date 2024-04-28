#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''
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
'''
# -*- coding: utf-8 -*-
#================================Core Modules===================================||
from os.path import abspath, dirname, exists, join
import simplejson as j
from pandas import DataFrame
#===============================================================================||
from condor import condor#										||

from fxsquirl import collector

from nchantrs import utils
from nchantrs.libraries import pyqt
from nchantrs.models.applicationmodels import NchantdCloakModel
from nchantrs.models import models, treemodels
from nchantrs.dstruct.trees import NchantdTreeGenerator
#===============================================================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
log = True
#===============================================================================||
pxcfg = f'{here}/_data_/models.yaml'
class NchantdTODOAppModel(NchantdCloakModel):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODOAppModel')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('NchantdTODOAppModel Config\n', self.config.dikt.keys())
		super(MBAppModel, self).__init__(parent)
	def buildModel(self):
		''' '''
		return self

class NchantdTODOTreeModel(treemodels.NchantdTreeModel):
	''' '''
	def __init__(self, parent=None, root=None, cfg={}):
		''' '''
		self.config = condor.instruct(pxcfg).select('NchantdTODOTreeModel')
		self.config.override(cfg)
		if log: print('TODOTreeModel\n', parent.src)
		if parent:
			self.config.override(parent.config)
		self.src = parent.src
		super(NchantdTODOTreeModel, self).__init__(parent, root, cfg)
		if log: print('TODOTreeModel\n', self.src)
	def initData(self):
		''' '''
		self.genTreeNodes()
	def genTreeNodes(self):
		base = [0, 1, 0, 1, 0, 1, 1, 0, 0]
		nodes = [
			[1, 'Action', 'appnode', 0, 0, 'NchantdTODOActionTabSet']+base,
			[2, 'Need Action', 'appnode', 0, 1, 'NchantdTODONeedActionTabSet']+base,
			[3, 'Waitng On', 'appnode', 0, 2, 'NchantdTODOWaitingOnTabSet'] + base,
			[4, 'Journal', 'appnode', 1, 0, 'NchantdTODOJournalTabSet'] + base,
			[5, 'Calendar', 'appndoe', 2, 0, 'NchantdTODOCalendarTabSet'] + base,
			[6, 'Fund', 'appnode', 2, 1, 'NchantdTODOFundTabSet'] + base,
			[7, 'eMail', 'appnode', 2, 2, 'NchantdTODOeMailTabSet'] + base,
			[8, 'Procure', 'appnode', 7, 1, 'NchantdTODOProcureTabSet'] + base,
			[9, 'Contacts', 'appnode', 0, 4, 'NchantdTODOContactsTabSet'] + base,
			[10, 'L0', 'appnode', 9, 0, 'NchantdTODOContactsLevelTabSet'] + base,
			[11, 'L1', 'appnode', 9, 1, 'NchantdTODOContactsLevelTabSet'] + base,
			[12, 'L2', 'appnode', 9, 2, 'NchantdTODOContactsLevelTabSet'] + base,
			[13, 'L3', 'appnode', 9, 3, 'NchantdTODOContactsLevelTabSet'] + base,
			[14, 'L4', 'appnode', 9, 4, 'NchantdTODOContactsLevelTabSet'] + base,
			[15, 'L5', 'appnode', 9, 5, 'NchantdTODOContactsLevelTabSet'] + base
		]
		cols = ['nid', 'name', 'ntype', 'parentid', 'position', 'tabset',
			'treeid', 'readonly', 'editable', 'visible', 'moveable',
			'pregnable', 'isparent', 'expanded', 'tabfocus']
		if log: print('SRC', self.src)
		# for acct in email_accts:
		# 	nodes.append()
		# for contact in contacts:
		# 	nodes.append()
		self.src.wrtr({'trnodes': DataFrame(nodes, columns=cols)})
		tabs = []
		base = [0, 1, 1, 1]
		for node in nodes:
			tabs += getattr(self, f'init{node[5]}Model')(base)
		cols = ['name', 'widget', 'widgdata', 'parentid', 'position',
				'readonly', 'editable', 'visible', 'moveable']
		if log: print('TABS', tabs)
		self.src.wrtr({'tabs': DataFrame(tabs, columns=cols)})
		NchantdTreeGenerator().genYearMonthTreeData(self.src, 0, 4, 16)
		return self
	def initNchantdTODOActionTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOActionTab'
		data = j.dumps({'': ''})
		tabs.append(['Actions Summary', widget, data, 1, 0] + base)
		wiget = 'test_nchantrs.widgets.dashboards.NchantdNEWSTab'
		data = j.dumps({})
		tabs.append(['NEWS', widget, data, 1, 1] + base)
		return tabs
	def initNchantdTODOContactTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOContactTab'
		data = j.dumps({'': ''})
		tabs.append(['Contact', widget, data, 9, 0] + base)
		return tabs
	def initNchantdTODOContactsLevelTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOContactLevelSummaryTab'
		data = j.dumps({'': ''})
		tabs.append(['Contacts Level Summary', widget, data, 9, 0] + base)
		return tabs
	def initNchantdTODOContactsTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOContactsTab'
		data = j.dumps({'': ''})
		tabs.append(['Contacts Summary', widget, data, 9, 0] + base)
		return tabs
	def initNchantdTODOeMailTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOeMailTab'
		data = j.dumps({'': ''})
		tabs.append(['eMail Summary', widget, data, 7, 0] + base)
		return tabs
	def initNchantdTODOFundTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOFundSummaryTab'
		data = j.dumps({'': ''})
		tabs.append(['Fund Summary', widget, data, 6, 0] + base)
		return tabs
	def initNchantdTODONeedActionTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODONeedActionTab'
		data = j.dumps({'': ''})
		tabs.append(['Need Actions Summary', widget, data, 2, 0] + base)
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOTaskSplitterTab'
		data = j.dumps({'': ''})
		tabs.append(['Split Tasks', widget, data, 2, 1] + base)
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODODelegationTab'
		data = j.dumps({'': ''})
		tabs.append(['Delegate Tasks', widget, data, 2, 2] + base)
		return tabs
	def initNchantdTODOWaitingOnTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOWaitingOnTab'
		data = j.dumps({'': ''})
		tabs.append(['Waiting On Summary', widget, data, 3, 0] + base)
		return tabs
	def initNchantdTODOJournalTabSetModel(self, base):
		''' '''
		tabs = []
		widget ='test_nchantrs.packages.nchantdtodos.widgets.NchantdTODOJournalTab'
		data = j.dumps({'': ''})
		tabs.append(['Journal Summary', widget, data, 4, 0] + base)
		return tabs
	def initNchantdTODOCalendarTabSetModel(self, base):
		''' '''
		data = j.dumps({'': ''})
		tabs = [
			['This Week', 'test_nchantrs.widgets.calendars.NchantdWeekCalendar', data, 5, 0] + base,
			['Next Week', 'test_nchantrs.widgets.calendars.NchantdWeekCalendar', data, 5, 1] + base,
			['Next Month', 'test_nchantrs.widgets.calendars.NchantdMonthCalendar', data, 5, 2] + base,
			['Yearly Calendar', 'test_nchantrs.widgets.calendars.NchantdYearCalendar', data, 5, 3] + base,
			['Events', 'test_nchantrs.widgets.NchantdEventsList', data, 5, 4] + base
		]
		return tabs
	def initNchantdTODOProcureTabSetModel(self, base):
		''' '''
		data = j.dumps({'': ''})
		tabs = []
		tabs.append(['Procure', 'test_nchantrs.widgets.editors.NchantdDocEditor', data, 8, 0] + base)
		return tabs
