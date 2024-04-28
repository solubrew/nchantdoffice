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
from nchantrs.packages.nchantdtodos import models
#===============================================================================||
here = join(dirname(__file__),'')#												||
there = abspath(join('../../..'))#												||set path at pheonix level
version = '0.0.0.0.0.0'#														||
log = True
#===============================================================================||
pxcfg = f'{here}_data_/widgets.yaml'
class NchantdTODOActionTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		if log: print('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('NchantdTODOActionTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NchantdTODOActionTab, self).__init__(parent, self.config)
	def initModel(self):
		''' '''
		if log: print('CONFIG', self.config.dikt)
		# self.name = self.config.dikt['tab']['name']
		# self.data = j.loads(self.config.dikt['tab']['widgdata'])
		return self
	def initView(self):
		''' '''
		self.buildPane()
		#self.setText(self.data['text'])
		return self
	def buildPane(self):
		''' '''
		minutes = ['00', '15', '30', '45']
		windows, sections, hour = 96, 3, 0
		l = pyqt.QHBoxLayout()
		for section in range(sections):
			l0 = pyqt.QVBoxLayout()
			cnt = 1
			for i in range(int(windows/sections)):
				thour = str(hour)
				if len(str(hour)) == 1:
					thour = f'0{hour}'
				minute  = minutes[i%4]
				if log: print('TODO Action', self.config.dikt)
				l1 = pyqt.QHBoxLayout()
				l1.addWidget(annotations.NchantdLabel(f'{thour}:{minute}'))
				l1.addWidget(annotations.NchantdEntryBox(self).initWidget())
				l0.addLayout(l1)
				if cnt == 4:
					hour += 1
					cnt = 0
				cnt += 1
			l.addLayout(l0)
		self.setLayout(l)
		return self
	def onEnterEvent(self):
		'''Run a save of the doc editor data to the database '''
	def mousePressEvent(self, event):
		''' '''
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
		return self
class NchantdTODOCalendarTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODOTree')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOCalendarTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOContactsTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODOContactsTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOContactsTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOContactsLevelSummaryTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdTODOContactsLevelTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOContactLevelSummaryTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOContactTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODOContactTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOContactTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODODelegationTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODODelegationTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODODelegationTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOeMailTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.config = condor.instruct(pxcfg).select('NchantdTODOeMailTab')
		self.config.override(cfg)#		||
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOeMailTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOEntryForm(forms.NchantdDynamicRecordEntryForm):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.config = condor.instruct(pxcfg).select('NchantdTODOEntryForm')
		self.config.override(cfg)#		||
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOEntryForm, self).__init__(parent, cfg)
	def buildPane(self):
		''' '''
		cnt, self.fieldWDGTs = 0, {}
		fields = self.config.dikt['params']['fields']
		self.loadFields(fields)
		for predecessor in self.predecessors:
			self.predecssorForms[predecessor[0]] = NchantdTODOPredecessorEntryForm()
		self.addPredecessorBTN = NchantdButton('Add Predecessor')
		return self
	def initView(self):
		''' '''
		self.predecessorTasks = []
		return self
class NchantdTODOEventsListTab(tables.NchantdTable):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdTODOEventsListTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOFundTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOFundSummaryTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdTODOFundSummaryTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOFundTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOJournalTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.config = condor.instruct(pxcfg).override(cfg)#		||
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOJournalTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODONeedActionTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODOTree').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODONeedActionTab, self).__init__(parent, self.config)
	def buildTab(self):
		''' '''
		self.editors = {}
		self.forms = {}
		layout_b = pyqt.QVBoxLayout()
		labels = ['Yesterday - Monday 2022/01/30', 'Today - Tuesday 2022/01/31',
					'Tommorrow - Wednesday 2022/02/01','Thursday 2022/02/02',
					'Friday 2022/02/03','Saturday 2022/01/04',
					'Sunday 2022/01/05', 'Monday 2022/01/06 - Sunday 2022/01/13',
					'Monday 2022/01/06 - Sunday 2022/01/13',
					'Monday 2022/01/06 - Sunday 2022/01/13',
					'Monday 2022/01/06 - Sunday 2022/01/13']
		cnt = 0
		for label in labels:
			layout_b.addWidget(annotations.NchantdLabel(label))
			self.editors[cnt] = editors.NchandDocEditor(self).initWidget()
			layout_b.addWidget(self.editors[cnt])
			cnt += 1
		layout_c = pyqt.QVBoxLayout()
		self.forms[0] = NchantdTODOEntryForm(self).initWidget()
		self.editors[cnt] = editors.NchandDocEditor(self).initWidget()
		layout_c.addWidget(self.editors[cnt])
		layout_a = pyqt.QHBoxLayout()
		layout_a.addWidget(layout_b)
		layout_a.addWidget(layout_c)
		return self
class NchantdTODOPastSummaryTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODOTree')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOPastSummaryTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOPredecessorEntryForm(forms.NchantdDynamicRecordEntryForm):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdTODOPredecessorEntryForm').override(cfg)#		||
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOPredecessorEntryForm, self).__init__(parent, cfg)
	def buildPane(self):
		''' '''
		cnt, self.fieldWDGTs = 0, {}
		fields = self.config.dikt['params']['fields']
		self.loadFields(fields)
		return self
	def initView(self):
		''' '''
		self.predecessorTasks = []
		return self
class NchantdTODOTaskSplitterTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NchantdTODOTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOTaskSplitterTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
class NchantdTODOTree(trees.NchantdCustomTree):
	''' '''
	def __init__(self, parent=None, cfg={}, root=None):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODOTree')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOTree, self).__init__(parent, self.config)
		self.src = self.parent.src
		self.newInstance = self.parent.newInstance
		if log: print('NchantdTODOTree\n', self.src, '\n', self.parent)
		self.model = models.NchantdTODOTreeModel(self)
		self.model.initData()
class NchantdTODOWaitingOnTab(tabsets.NchantdTab):
	''' '''
	def __init__(self, parent=None, cfg={}):
		''' '''
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTODOWaitingOnTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOWaitingOnTab, self).__init__(parent, self.config)
	def buildPane(self):
		''' '''
		return self
