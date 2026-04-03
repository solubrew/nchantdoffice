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

from worldbridger.source import etherscanSRC

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
class NchantdFundTreeModel(treemodels.NchantdTreeModel):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.config = condor.instruct(pxcfg).select('NchantdFundTreeModel')
		self.config.override(cfg)
		if log: print('FundTreeModel\n', parent.src)
		if parent:
			self.config.override(parent.config)
		self.src = parent.src
		super(NchantdFundTreeModel, self).__init__(parent)
		if log: print('FundTreeModel\n', self.src)
	def initData(self):
		''' '''
		self.genTreeNodes()
	def genTreeNodes(self):
		base = [0, 1, 0, 1, 0, 1, 1, 0, 0]
		nodes = [
			[1, 'Fund', 'appnode', 0, 0, 'NchantdFundSummaryTabSet']+base,
			[2, 'Tools', 'appnode', 1, 0, 'NchantdFundToolsTabSet']+base,
		]
		cols = ['nid', 'name', 'ntype', 'parentid', 'position', 'tabset',
			'treeid', 'readonly', 'editable', 'visible', 'moveable',
			'pregnable', 'isparent', 'expanded', 'tabfocus']
		self.src.wrtr({'trnodes': DataFrame(nodes, columns=cols)})
		tabs = []
		base = [0, 1, 1, 1]
		for node in nodes:
			tabs += getattr(self, f'init{node[5]}Model')(base)
		cols = ['name', 'widget', 'widgdata', 'parentid', 'position',
				'readonly', 'editable', 'visible', 'moveable']
		self.src.wrtr({'tabs': DataFrame(tabs, columns=cols)})
		return self
	def initNchantdFundSummaryTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'nchantdfund.widgets.NchantdFundCashFlowTrackerTab'
		data = j.dumps({'': ''})
		tabs.append(['CashFlow Tracker', widget, data, 1, 0] + base)
		widget = 'nchantdfund.widgets.NchantdFundRevenuesTab'
		data = j.dumps({})
		tabs.append(['Revenues', widget, data, 1, 1] + base)
		widget = 'nchantdfund.widgets.NchantdFundLiabilitiesTab'
		data = j.dumps({})
		tabs.append(['Liabilities', widget, data, 1, 2] + base)
		widget = 'nchantdfund.widgets.NchantdFundDebitCreditLedgerTab'
		data = j.dumps({})
		tabs.append(['Debit/Credit Ledger', widget, data, 1, 3] + base)
		return tabs
	def initNchantdFundToolsTabSetModel(self, base):
		''' '''
		tabs = []
		widget = 'nchantdfund.widgets.NchantdFundLoanCalculatorTab'
		data = j.dumps({})
		tabs.append(['Loan Calculator', widget, data, 2, 0] + base)
		widget = 'nchantdfund.widgets.NchantdFundAnnuityCalculatorTab'
		data = j.dumps({})
		tabs.append(['Annuity Calculator', widget, data, 2, 1] + base)
		return tabs
class NchantdFundExpensesTabModel():
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundLiabilitiesTabModel').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundLiabilitiesTabModel, self).__init__(parent, cfg)
	def initData(self):
		''' '''

class NchantdFundLiabilitiesTabModel():
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundLiabilitiesTabModel').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundLiabilitiesTabModel, self).__init__(parent, cfg)
	def initData(self):
		''' '''
