# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""  #																			||
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
"""  # ||
# -*- coding: utf-8 -*-#														||
# ===============================Core Modules====================================||
from os.path import abspath, dirname, exists, join
import datetime as dt, time

# ===============================================================================||
from condor import condor
from nchantrs.libraries import pyqt, pandas_profiling, pandasgui, sweetviz
from nchantrs.widgets import annotations, calendars, controls, editors, forms, tables, tabsets, trees

from nchantdtodo.models import NTDTreeModel

from ogma.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), '')  # ||
log = False
logma = Logma(__name__)
# ===============================================================================||
pxcfg = join(here, '_data_', 'widgets.yaml')

class NTDAddConcernTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDAddConcernTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		top_layout = pyqt.QHBoxLayout()
		
		top_layout_left = pyqt.QHBoxLayout()
		cfg = {'label': 'New Concern Name: '}
		top_layout_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())
		
		cfg = {'label': 'New Concern Code: '}
		top_layout_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())
		
		top_layout_left.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		
		top_layout.addLayout(top_layout_left)
		top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		
		cfg = {'label': 'New Concern Description: '}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
		layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		layout.addWidget(controls.NchantdSaveButtons(self).initWidget(None))
		
		bottom_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'List of Concerns: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		
		cfg = {'label': 'Assign Resources: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		
		layout.addLayout(bottom_layout)
		self.setLayout(layout)
		
		return self

class NTDAddEventTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDAddEventTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		gb = pyqt.QGroupBox()
		layout = pyqt.QVBoxLayout()
		layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		top_layout = pyqt.QHBoxLayout()
		top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		top_layout_left = pyqt.QHBoxLayout()
		top_layout_left.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		top_layout_left_left = pyqt.QVBoxLayout()
		top_layout_left_left.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		calendar_time_layout_1 = pyqt.QVBoxLayout()
		calendar_time_layout_2 = pyqt.QVBoxLayout()
		
		cfg = {'label': 'Event Name: '}
		top_layout_left_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())
		cfg = {'label': 'Event Description: '}
		top_layout_left_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		top_layout_left.addLayout(top_layout_left_left)

		top_layout_left_left_right = pyqt.QHBoxLayout()
		cfg = {'label': 'Focus Required: '}
		top_layout_left_left_right.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'small'))
		cfg = {'label': 'Event Location: '}
		top_layout_left_left_right.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'small'))
		top_layout_left_left.addLayout(top_layout_left_left_right)

		calendar_time_layout_1.addWidget(calendars.NchantdDateTimeGroup(self, {}).initWidget())
		calendar_time_layout_2.addWidget(calendars.NchantdDateTimeGroup(self, {}).initWidget())
		
		top_layout_left.addLayout(calendar_time_layout_1)
		top_layout_left.addLayout(calendar_time_layout_2)
		
		top_layout.addLayout(top_layout_left)
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		
		#layout.addLayout(top_layout)
		bottom_layout = pyqt.QVBoxLayout()
		bottom_layout.addWidget(controls.NchantdSaveButtons(self).initWidget(None))
		gb = pyqt.QGroupBox()
		gb.setLayout(bottom_layout)
		layout.addWidget(gb)
		layout_recursion = pyqt.QVBoxLayout()
		cfg = {'label': 'Configuration Recursion: '}
		layout_recursion.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		gb = pyqt.QGroupBox()
		gb.setLayout(layout_recursion)
		layout.addWidget(gb)
		self.setLayout(layout)
		return self

class NTDAddResourceTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDAddResourceTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		top_layout = pyqt.QHBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout_left = pyqt.QHBoxLayout()
		cfg = {'label': 'New Resource Name: '}
		top_layout_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())
		
		cfg = {'label': 'New Resource Code: '}
		top_layout_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())
		
		top_layout_left.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		
		top_layout.addLayout(top_layout_left)
		top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		cfg = {'label': 'New Resource Description: '}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		layout.addWidget(controls.NchantdSaveButtons(self).initWidget(None))
		
		bottom_layout = pyqt.QHBoxLayout()
		gb = pyqt.QGroupBox()
		cfg = {'label': 'List of Concerns: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		
		cfg = {'label': 'Assign Resources: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		gb.setLayout(bottom_layout)
		layout.addWidget(gb)
		self.setLayout(layout)
		
		return self

class NTDAddTaskTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDAddTaskTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		top_layout = pyqt.QHBoxLayout()
		top_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		top_layout_left = pyqt.QVBoxLayout()
		top_layout_left.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		top_layout_left_upper = pyqt.QHBoxLayout()
		top_layout_left_upper.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		top_layout_left_lower = pyqt.QHBoxLayout()
		top_layout_left_lower.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		top_layout_right = pyqt.QVBoxLayout()
		top_layout_right.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		bottom_layout = pyqt.QHBoxLayout()
		bottom_layout.setAlignment(pyqt.Qt.AlignmentFlag.AlignTop)
		
		cfg = {'label': 'Task Name: '}
		top_layout_left_upper.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())
		cfg = {'label': 'Estimated Task Hours: '}
		top_layout_left_upper.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget())
		top_layout_left.addLayout(top_layout_left_upper)
		
		cfg = {'label': 'Due Date: '}
		top_layout_left_lower.addWidget(calendars.NchantdDateSelect(self, cfg).initWidget())
		top_layout_left.addLayout(top_layout_left_lower)
		top_layout.addLayout(top_layout_left)
		
		cfg = {'label': 'Task Notes: '}
		top_layout_right.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Primary Concern: '}
		top_layout_right.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'small'))
		top_layout.addLayout(top_layout_right)
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		layout.addWidget(controls.NchantdSaveButtons(self).initWidget(None))
		gb = pyqt.QGroupBox()
		cfg = {'label': 'Assign Dependencies: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		cfg = {'label': 'Assign Dependants: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		cfg = {'label': 'Assign Resources: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		gb.setLayout(bottom_layout)
		layout.addWidget(gb)
		self.setLayout(layout)
		return self

class NTDAdministrateConcernsTab(tabsets.NchantdTab):
	"""Show A summary of tasks connected to s a specific Concern
	"""
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDConcernTasksTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDAdministrateConcernsTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Operations List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self

class NTDAdministrateEventsTab(tabsets.NchantdTab):
	"""Show A summary of tasks connected to s a specific Concern
	"""
	
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDConcernTasksTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDAdministrateEventsTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Operations List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self

class NTDAdministrateResourcesTab(tabsets.NchantdTab):
	"""Show A summary of tasks connected to s a specific Concern
	"""
	
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDConcernTasksTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDAdministrateResourcesTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Operations List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self


class NTDDailyTaskTrackerTab(forms.NchantdTimeTrackerFormFast):
	""" """
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		if log: logma.info('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('tabsets.NchantdTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NTDDailyTaskTrackerTab, self).__init__(parent, self.config, panestyle)
	
	def initView(self):
		""" """
		self.buildPane(15, 1, '08:00', 4)
		return self


class NTDDaily15MinTrackerTab(forms.NchantdTimeTrackerForm):
	""" """
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		if log: logma.info('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('tabsets.NchantdTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NTDDaily15MinTrackerTab, self).__init__(parent, self.config, panestyle)

	def initView(self):
		""" """
		self.buildPane(15, 1, '08:00', 4)
		return self

class NTDDaily5MinTrackerTab(forms.NchantdTimeTrackerForm):
	""" """
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		if log: logma.info('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('tabsets.NchantdTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NTDDaily5MinTrackerTab, self).__init__(parent, self.config, panestyle)

	def initView(self):
		""" """
		self.buildPane(5, 1, '08:00', 10)
		return self

class NTDDaily30MinTrackerTab(forms.NchantdTimeTrackerForm):
	""" """
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		if log: logma.info('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('tabsets.NchantdTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NTDDaily30MinTrackerTab, self).__init__(parent, self.config, panestyle)
	
	def initView(self):
		""" """
		self.buildPane(30, 1, '08:00', 4)
		return self

class NTDDaily1HrTrackerTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		if log: logma.info('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('tabsets.NchantdTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NTDDaily1HrTrackerTab, self).__init__(parent, self.config, panestyle)
	
	def initView(self):
		""" """
		self.buildPane(60, 1, '08:00', 4)
		return self

class NTDDaily2HrTrackerTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		if log: logma.info('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('tabsets.NchantdTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NTDDaily2HrTrackerTab, self).__init__(parent, self.config, panestyle)
	
	def initView(self):
		""" """
		self.buildPane(60, 2, '08:00', 4)
		return self
	
class NTDDaily4HrTrackerTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		if log: logma.info('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('tabsets.NchantdTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NTDDaily4HrTrackerTab, self).__init__(parent, self.config, panestyle)
	
	def initView(self):
		""" """
		self.buildPane(60, 4, '08:00', 4)
		return self

class NTDHistoryTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, panetype=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDHistoryTab, self).__init__(parent, self.config, panetype)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Yesterdays Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Last Weeks Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Completed Projects'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self

class NTDObjectOrganizationTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDObjectOrganizationTab, self).__init__(parent, self.config)
	
	def buildPane(self):
		""" """
		return self

class NTDMonthCalendarTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDMonthCalendarTab, self).__init__(parent, self.config, panestyle)

	def buildPane(self):
		""""""
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		layout.addWidget(calendars.NchantdMonthCalendar(self).initWidget())
		gb.setLayout(layout)
		
		self.setLayout(layout)
		return self

class NTDMonthlyTaskListTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDMonthlyTaskListTab, self).__init__(parent, self.config)

class NTDMultiWeekCalendarTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDMultiWeekCalendarTab, self).__init__(parent, self.config)
	
	def buildPane(self):
		""" """
		return self

class NTDOperationOverviewTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDOperationOverviewTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDOperationOverviewTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Operation Tasks Overview'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Operations Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self

class NTDOperationsSummaryTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDOperationsSummaryTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDOperationsSummaryTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Project Tasks Overview'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self

class NTDProjectOverviewTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDProjectOverviewTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDProjectOverviewTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Project Tasks Overview'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self
	
	def initModel(self):
		""" """
		return self
	
	def initView(self):
		""" """
		self.buildPane()
		return self

class NTDProjectsSummaryTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDProjectsSummaryTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDProjectsSummaryTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Project Tasks Overview'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self

class NTDRecentCompletedTasksTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDProjectsSummaryTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDRecentCompletedTasksTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Recent Completed Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self

class NTDSplitTaskTab(tabsets.NchantdTab):
	""" """
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDSplitTaskTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		top_layout_left = pyqt.QVBoxLayout()
		top_layout_left.addWidget(editors.NchantdEntryEditor(self, {"label": "Task Name: "}).initWidget())
		orig_due_date = editors.NchantdEntryEditor(self, {"label": "Original Due Date: "})
		top_layout_left.addWidget(orig_due_date.initWidget(None, 'small'))
		cfg = {}
		current_due_date = calendars.NchantdDateSelect(self, cfg).initWidget()
		top_layout_left.addWidget(current_due_date.initWidget())
		
		top_layout_left_center = pyqt.QHBoxLayout()
		hours = editors.NchantdEntryEditor(self, {"label": "Esitmated Hours: "})
		top_layout_left_center.addWidget(hours.initWidget(None, 'small'))
		concern = editors.NchantdEntryEditor(self, {"label": "Expended Hours: "})
		top_layout_left_center.addWidget(concern.initWidget(None, 'small'))
		top_layout_left.addLayout(top_layout_left_center)
		
		top_layout_left_bottom = pyqt.QHBoxLayout()
		top_layout_left_bottom.addWidget(controls.NchantdButton(self, {"text": "Save Task"}).initWidget())
		top_layout_left_bottom.addWidget(controls.NchantdButton(self, {"text": "Split Task"}).initWidget())
		top_layout_left_bottom.addWidget(controls.NchantdButton(self, {"text": "Complete Task"}).initWidget())
		
		top_layout_left.addLayout(top_layout_left_bottom)
		top_layout.addLayout(top_layout_left)
		
		top_layout_center = pyqt.QVBoxLayout()
		description = editors.NchantdEntryEditor(self, {"label": "Description: "})
		top_layout_center.addWidget(description.initWidget(None, 'medium'))
		notes = editors.NchantdEntryEditor(self, {"label": "Notes: "})
		top_layout_center.addWidget(notes.initWidget(None, 'medium'))
		top_layout.addLayout(top_layout_center)
		
		top_layout_right = pyqt.QVBoxLayout()
		description = editors.NchantdEntryEditor(self, {"label": "Status: "})
		top_layout_right.addWidget(description.initWidget(None))
		notes = editors.NchantdEntryEditor(self, {"label": "Concern: "})
		top_layout_right.addWidget(notes.initWidget(None))
		top_layout.addLayout(top_layout_right)
		
		top_layout_right = pyqt.QVBoxLayout()
		top_layout.addLayout(top_layout_right)
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		gb0 = pyqt.QGroupBox()
		split_type = 'children'
		bottom_layout = pyqt.QHBoxLayout()
		new_tasks = 2
		if split_type == 'children':
			bottom_layout = pyqt.QVBoxLayout()
			new_tasks = 3#get number from interface
		for task in range(new_tasks):
			notes = editors.NchantdEntryEditor(self, {"label": "Task A: "})
			bottom_layout.addWidget(notes.initWidget(None, 'medium'))

		gb.setLayout(bottom_layout)
		layout.addWidget(gb)
		self.setLayout(layout)
		return self

class NTDTaskDetailTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDTaskDetailTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		gb = pyqt.QGroupBox()
		top_layout = pyqt.QHBoxLayout()
		top_layout_left = pyqt.QVBoxLayout()
		top_layout_left.addWidget(editors.NchantdEntryEditor(self, {"label": "Task Name: "}).initWidget())
		orig_due_date = editors.NchantdEntryEditor(self, {"label": "Original Due Date: "})
		top_layout_left.addWidget(orig_due_date.initWidget(None, 'small'))
		cfg = {}
		current_due_date = calendars.NchantdDateSelect(self, cfg).initWidget()
		top_layout_left.addWidget(current_due_date.initWidget())
		
		top_layout_left_center = pyqt.QHBoxLayout()
		hours = editors.NchantdEntryEditor(self, {"label": "Esitmated Hours: "})
		top_layout_left_center.addWidget(hours.initWidget(None, 'small'))
		concern = editors.NchantdEntryEditor(self, {"label": "Expended Hours: "})
		top_layout_left_center.addWidget(concern.initWidget(None, 'small'))
		top_layout_left.addLayout(top_layout_left_center)
		
		top_layout_left_bottom = pyqt.QHBoxLayout()
		top_layout_left_bottom.addWidget(controls.NchantdButton(self, {"text": "Save Task"}).initWidget())
		top_layout_left_bottom.addWidget(controls.NchantdButton(self, {"text": "Split Task"}).initWidget())
		top_layout_left_bottom.addWidget(controls.NchantdButton(self, {"text": "Complete Task"}).initWidget())
		
		top_layout_left.addLayout(top_layout_left_bottom)
		top_layout.addLayout(top_layout_left)

		top_layout_center = pyqt.QVBoxLayout()
		description = editors.NchantdEntryEditor(self, {"label": "Description: "})
		top_layout_center.addWidget(description.initWidget(None, 'medium'))
		notes = editors.NchantdEntryEditor(self, {"label": "Notes: "})
		top_layout_center.addWidget(notes.initWidget(None, 'medium'))
		top_layout.addLayout(top_layout_center)

		top_layout_right = pyqt.QVBoxLayout()
		description = editors.NchantdEntryEditor(self, {"label": "Status: "})
		top_layout_right.addWidget(description.initWidget(None))
		notes = editors.NchantdEntryEditor(self, {"label": "Concern: "})
		top_layout_right.addWidget(notes.initWidget(None))
		top_layout.addLayout(top_layout_right)

		top_layout_right = pyqt.QVBoxLayout()
		top_layout.addLayout(top_layout_right)
		gb.setLayout(top_layout)
		layout.addWidget(gb)
		gb0 = pyqt.QGroupBox()
		bottom_layout = pyqt.QHBoxLayout()
		bottom_layout_left = pyqt.QVBoxLayout()
		#need a drag -n- drop widget
		resources = editors.NchantdEntryEditor(self, {"label": "Resources:"})
		bottom_layout_left.addWidget(resources.initWidget(None, 'large'))
		bottom_layout.addLayout(bottom_layout_left)

		bottom_layout_center = pyqt.QVBoxLayout()
		dependants = editors.NchantdEntryEditor(self, {"label": "Dependants:"})
		bottom_layout_center.addWidget(dependants.initWidget(None, 'large'))
		bottom_layout.addLayout(bottom_layout_center)

		bottom_layout_right = pyqt.QVBoxLayout()
		dependancies = editors.NchantdEntryEditor(self, {"label": "Dependancies:"})
		bottom_layout_right.addWidget(dependancies.initWidget(None, 'large'))
		bottom_layout.addLayout(bottom_layout_right)

		gb0.setLayout(bottom_layout)
		layout.addWidget(gb0)
		self.setLayout(layout)
		return self

class NTDTaskGanttTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskGanttTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDTaskGanttTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QHBoxLayout()
		gb = pyqt.QGroupBox()
		left_layout = pyqt.QVBoxLayout()
		left_layout.addWidget(NTDTaskTree(self).initWidget())
		gb.setLayout(left_layout)
		layout.addWidget(gb)

		gb0 = pyqt.QGroupBox()
		right_layout = pyqt.QVBoxLayout()
		right_layout.addWidget(calendars.NchantdGanttCanvas(self).initWidget())
		gb0.setLayout(right_layout)
		layout.addWidget(gb0)

		self.setLayout(layout)
		return self

class NTDTaskTree(trees.NchantdCustomTree):
	""" """
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskGanttTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDTaskTree, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""""""
		
		return self

class NTDTree(trees.NchantdCustomTree):
	""" """
	def __init__(self, parent=None, cfg={}, root=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NTDTree')
		#self.config.override(cfg)
		logma.store(self.config.dikt)
		logma.info(self.config.dikt.keys())
		if parent:
			self.config.override(parent.config)
		super(NTDTree, self).__init__(parent, self.config)
		self.src = self.parent.src
		self.newInstance = self.parent.newInstance
		if log: print('NTDTree\n', self.src, '\n', self.parent)
		self.model = NTDTreeModel(self)
		self.model.initData()

class NTDWeekly1DayTrackerTab(tabsets.NchantdTab):
	""" """
	
	def __init__(self, parent=None, cfg={}, panestyle=None):
		""" """
		self.parent = parent
		if log: logma.info('CFG', cfg)
		self.config = condor.instruct(pxcfg).select('tabsets.NchantdTab')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('Config', self.config.dikt)
		super(NTDWeekly1DayTrackerTab, self).__init__(parent, self.config, panestyle)
	
	def initModel(self):
		""" """
		if log: print('CONFIG', self.config.dikt)
		# self.name = self.config.dikt['tab']['name']
		# self.data = j.loads(self.config.dikt['tab']['widgdata'])
		return self
	
	def initView(self):
		""" """
		self.buildPane()
		# self.setText(self.data['text'])
		return self
	
	def buildPane(self, sections=7):
		""" """
		days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
		layout = pyqt.QVBoxLayout()
		columns, rows, i = 2, 3, 0
		for row in range(rows):
			row_layout = pyqt.QHBoxLayout()
			gb = pyqt.QGroupBox()
			for column in range(columns):
				if row == 2 and column == 1:
					split_layout = pyqt.QVBoxLayout()
					cfg = {'label': 'Saturday', 'size': [500, 25]}
					split_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
					cfg = {'label': 'Sunday', 'size': [500, 25]}
					split_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
					row_layout.addLayout(split_layout)

				else:
					cfg = {'label': days[i], 'size': [500, 25]}
					row_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
				i += 1
			gb.setLayout(row_layout)
			layout.addWidget(gb)
			#layout.addLayout(row_layout)
		self.setLayout(layout)
		return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
		return self

