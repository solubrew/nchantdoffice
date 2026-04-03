#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																			||
---  #																			||
<(META)>:  #																	||
	DOCid:   #																	||
	name:   #																	||
	description: >  #															||
		  #			||
	expirary: <[expiration]>  #													||
	version: <[version]>  #														||
	path: <[LEXIvrs]>  #														||
	outline: <[outline]>  #														||
	authority: document|this  #													||
	security: sec|lvl2  #														||
	<(WT)>: -32  #																||
''' #																			||
# -*- coding: utf-8 -*-#														||
#===============================Core Modules====================================||
from os.path import abspath, dirname, exists, join
import simplejson as j
#===============================================================================||
from condor import condor
from condor.thing import thingify
from nchantrs.libraries import pyqt, pandas_profiling, pandasgui, sweetviz
from nchantrs.widgets import annotations, editors, forms, tables, tabsets, trees
import models
#===============================================================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
log = True
#===============================================================================||
pxcfg = f'{here}_data_/widgets.yaml'
class NchantdFundAccountsTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdFundAccountsTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundAccountsTab, self).__init__(parent, cfg)
class NchantdFundCashFlowTrackerTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundCashFlowTrackerTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundCashFlowTrackerTab, self).__init__(parent, cfg)
class NchantdFundExpensesTab():
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundExpensesTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundExpensesTab, self).__init__(parent, cfg)
	def buildPane(self):
		''' '''
		return self
class NchantdFundRevenuesTab():
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundRevenuesTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundRevenuesTab, self).__init__(parent, cfg)
class NchantdFundLiabilitiesTab():
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundLiabilitiesTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundLiabilitiesTab, self).__init__(parent, cfg)
	def buildPane(self):
		''' '''
		return self
class NchantdFundRevenueEntryForm():
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundRevenueEntryForm').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundRevenueEntryForm, self).__init__(parent, cfg)
class NchantdFundExpenseEntryForm(forms.NchantdDynamicRecordEntryForm):
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundExpenseEntryForm').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundExpenseEntryForm, self).__init__(parent, cfg)
class NchantdFundLiabilityEntryForm():
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundLiabilityEntryForm').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundAccountsTab, self).__init__(parent, cfg)
class NchantdFundLedgerTab():
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdFundLedgerTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundAccountsTab, self).__init__(parent, cfg)
class NchantdFundAssetTrackerTab():
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundAssetTrackerTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundAccountsTab, self).__init__(parent, cfg)
class NchantdFundLiabilityTrackerTab():
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdFundLiabilityTrackerTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundAccountsTab, self).__init__(parent, cfg)
class NchantdFundTree(trees.NchantdCustomTree):
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdFundTree')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdFundTree, self).__init__(parent)
		self.src = self.parent.src
		self.newInstance = self.parent.newInstance
		if log: print('NchantdFundTree\n', self.src, '\n', self.parent)
		self.model = models.NchantdFundTreeModel(self)
		self.model.initData()
