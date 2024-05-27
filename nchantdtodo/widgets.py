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
		super(NTDAdministrateConcernTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Operations List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
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
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Operations List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
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
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Operations List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects List'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
		cfg = {'label': 'Near Term Tasks List'}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		self.setLayout(layout)
		return self


class NTDDailyTaskTrackerTab(tabsets.NchantdTab):
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
	
	def buildPane(self):
		""" """
		start_tm = time.strptime('08:00', '%H:%M')
		if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
		minutes = ['00', '15', '30', '45']
		
		def buildPane(self, minutes=['00', ], hour_inc=4):
			""" """
			start_tm = time.strptime('08:00', '%H:%M')
			if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
			windows, sections, hour = 24 * len(minutes), 4, 8
			layout = pyqt.QVBoxLayout()
			l = pyqt.QHBoxLayout()
			for section in range(sections):
				if log: logma.info(f"Section {section}")
				l0 = pyqt.QVBoxLayout()
				cnt = 1
				rows = int(windows / sections)
				if log: logma.info(f"Rows {rows}")
				for i in range(0, rows, hour_inc):
					if log: logma.info(f"I {i}")
					thour = str(hour)
					if len(str(hour)) == 1:
						thour = f'0{hour}'
					j = i % len(minutes)
					if log: logma.info(f"J {j}")
					minute = minutes[j]
					if log: logma.info(f"Minute {minute}")
					# if log: print('TODO Action', self.config.dikt)
					l1 = pyqt.QHBoxLayout()
					l1.addWidget(annotations.NchantdLabel().initWidget({'text': f'{thour}:{minute}'}))
					l1.addWidget(editors.NchantdEntryBox(self).initWidget(None))
					l0.addLayout(l1)
					if cnt == len(minutes):
						hour += hour_inc
						if hour == 24:
							hour = 0
						cnt = 0
					cnt += 1
				l.addLayout(l0)
			layout.addLayout(l)
			cfg = {'label': 'Select Task', 'size': [500, 25]}
			layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
			self.setLayout(layout)
			return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
		return self


class NTDDaily15MinTrackerTab(tabsets.NchantdTab):
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

	def buildPane(self):
		""" """
		start_tm = time.strptime('08:00', '%H:%M')
		if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
		minutes = ['00', '15', '30', '45']
		
		def buildPane(self, minutes=['00', ], hour_inc=4):
			""" """
			start_tm = time.strptime('08:00', '%H:%M')
			if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
			windows, sections, hour = 24 * len(minutes), 4, 8
			layout = pyqt.QVBoxLayout()
			l = pyqt.QHBoxLayout()
			for section in range(sections):
				if log: logma.info(f"Section {section}")
				l0 = pyqt.QVBoxLayout()
				cnt = 1
				rows = int(windows / sections)
				if log: logma.info(f"Rows {rows}")
				for i in range(0, rows, hour_inc):
					if log: logma.info(f"I {i}")
					thour = str(hour)
					if len(str(hour)) == 1:
						thour = f'0{hour}'
					j = i % len(minutes)
					if log: logma.info(f"J {j}")
					minute = minutes[j]
					if log: logma.info(f"Minute {minute}")
					# if log: print('TODO Action', self.config.dikt)
					l1 = pyqt.QHBoxLayout()
					l1.addWidget(annotations.NchantdLabel().initWidget({'text': f'{thour}:{minute}'}))
					l1.addWidget(editors.NchantdEntryBox(self).initWidget(None))
					l0.addLayout(l1)
					if cnt == len(minutes):
						hour += hour_inc
						if hour == 24:
							hour = 0
						cnt = 0
					cnt += 1
				l.addLayout(l0)
			layout.addLayout(l)
			cfg = {'label': 'Select Task', 'size': [500, 25]}
			layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
			self.setLayout(layout)
			return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
		return self

class NTDDaily5MinTrackerTab(tabsets.NchantdTab):
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
	
	def buildPane(self, minutes=5, hour_inc=1):
		""" """
		minutes = [str(x) if len(str(x)) == 2 else f"0{x}" for x in range(0, 60, minutes)]
		start_tm = time.strptime('08:00', '%H:%M')
		if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
		windows, sections, hour = 24 * len(minutes), 10, 8
		layout = pyqt.QVBoxLayout()
		l = pyqt.QHBoxLayout()
		for section in range(sections):
			if log: logma.info(f"Section {section}")
			l0 = pyqt.QVBoxLayout()
			cnt = 1
			rows = int(windows / sections)
			if log: logma.info(f"Rows {rows}")
			for i in range(0, rows, hour_inc):
				if log: logma.info(f"I {i}")
				thour = str(hour)
				if len(str(hour)) == 1:
					thour = f'0{hour}'
				j = i % len(minutes)
				if log:    logma.info(f"J {j}")
				minute = minutes[j]
				if log: logma.info(f"Minute {minute}")
				# if log: print('TODO Action', self.config.dikt)
				l1 = pyqt.QHBoxLayout()
				l1.addWidget(annotations.NchantdLabel().initWidget({'text': f'{thour}:{minute}'}))
				l1.addWidget(editors.NchantdSmallEntryBox(self).initWidget(None))
				l0.addLayout(l1)
				if cnt == len(minutes):
					hour += hour_inc
					if hour == 24:
						hour = 0
					cnt = 0
				cnt += 1
			l.addLayout(l0)
		layout.addLayout(l)
		cfg = {'label': 'Select Task', 'size': [500, 25]}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
		self.setLayout(layout)
		return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
		return self

class NTDDaily30MinTrackerTab(tabsets.NchantdTab):
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
	
	def buildPane(self, start_hour=8, minutes=30, hour_inc=1, sections=4):
		""" """
		minutes = [str(x) if len(str(x)) == 2 else f"0{x}" for x in range(0, 60, minutes)]
		start_tm = time.strptime('08:00', '%H:%M')
		if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
		windows = 24 * len(minutes)
		layout = pyqt.QVBoxLayout()
		l = pyqt.QHBoxLayout()
		hour = start_hour
		for section in range(sections):
			if log: logma.info(f"Section {section}")
			l0 = pyqt.QVBoxLayout()
			cnt = 1
			rows = int(windows / sections)
			if log: logma.info(f"Rows {rows}")
			for i in range(0, rows, hour_inc):
				if log: logma.info(f"I {i}")
				thour = str(hour)
				if len(str(hour)) == 1:
					thour = f'0{hour}'
				j = i % len(minutes)
				if log: logma.info(f"J {j}")
				minute = minutes[j]
				if log: logma.info(f"Minute {minute}")
				# if log: print('TODO Action', self.config.dikt)
				l1 = pyqt.QHBoxLayout()
				l1.addWidget(annotations.NchantdLabel().initWidget({'text': f'{thour}:{minute}'}))
				l1.addWidget(editors.NchantdSmallEntryBox(self).initWidget(None))
				l0.addLayout(l1)
				if cnt == len(minutes):
					hour += hour_inc
					if hour == 24:
						hour = 0
					cnt = 0
				cnt += 1
			l.addLayout(l0)
		layout.addLayout(l)
		cfg = {'label': 'Select Task', 'size': [500, 25]}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
		self.setLayout(layout)
		return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
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
	
	def buildPane(self, minutes=['00', ]):
		""" """
		start_tm = time.strptime('08:00', '%H:%M')
		if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
		windows, sections, hour = 24 * len(minutes), 4, 8
		layout = pyqt.QVBoxLayout()
		l = pyqt.QHBoxLayout()
		for section in range(sections):
			l0 = pyqt.QVBoxLayout()
			cnt = 1
			for i in range(int(windows / sections)):
				thour = str(hour)
				if len(str(hour)) == 1:
					thour = f'0{hour}'
				j = i % len(minutes)
				if log: logma.info(f"J {j}")
				minute = minutes[j]
				if log: logma.info(f"Minute {minute}")
				# if log: print('TODO Action', self.config.dikt)
				l1 = pyqt.QHBoxLayout()
				l1.addWidget(annotations.NchantdLabel().initWidget({'text': f'{thour}:{minute}'}))
				l1.addWidget(editors.NchantdEntryBox(self).initWidget(None))
				l0.addLayout(l1)
				if cnt == len(minutes):
					hour += 1
					if hour == 24:
						hour = 0
					cnt = 0
				cnt += 1
			l.addLayout(l0)
		layout.addLayout(l)
		cfg = {'label': 'Select Task', 'size': [500, 25]}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
		self.setLayout(layout)
		return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
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
	
	def buildPane(self, minutes=['00', ], hour_inc=2):
		""" """
		start_tm = time.strptime('08:00', '%H:%M')
		if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
		windows, sections, hour = 24 * len(minutes), 4, 8
		layout = pyqt.QVBoxLayout()
		l = pyqt.QHBoxLayout()
		for section in range(sections):
			if log: logma.info(f"Section {section}")
			l0 = pyqt.QVBoxLayout()
			cnt = 1
			rows = int(windows / sections)
			if log: logma.info(f"Rows {rows}")
			for i in range(0, rows, hour_inc):
				if log: logma.info(f"I {i}")
				thour = str(hour)
				if len(str(hour)) == 1:
					thour = f'0{hour}'
				j = i % len(minutes)
				if log: logma.info(f"J {j}")
				minute = minutes[j]
				if log: logma.info(f"Minute {minute}")
				# if log: print('TODO Action', self.config.dikt)
				l1 = pyqt.QHBoxLayout()
				l1.addWidget(annotations.NchantdLabel().initWidget({'text': f'{thour}:{minute}'}))
				l1.addWidget(editors.NchantdEntryBox(self).initWidget(None))
				l0.addLayout(l1)
				if cnt == len(minutes):
					hour += hour_inc
					if hour == 24:
						hour = 0
					cnt = 0
				cnt += 1
			l.addLayout(l0)
		layout.addLayout(l)
		cfg = {'label': 'Select Task', 'size': [500, 25]}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
		self.setLayout(layout)
		return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
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
	
	def buildPane(self, minutes=['00', ], hour_inc=4):
		""" """
		start_tm = time.strptime('08:00', '%H:%M')
		if log: logma.info(f"Start TM {start_tm} {type(start_tm)}")
		windows, sections, hour = 24 * len(minutes), 4, 8
		layout = pyqt.QVBoxLayout()
		l = pyqt.QHBoxLayout()
		for section in range(sections):
			if log: logma.info(f"Section {section}")
			l0 = pyqt.QVBoxLayout()
			cnt = 1
			rows = int(windows / sections)
			if log: logma.info(f"Rows {rows}")
			for i in range(0, rows, hour_inc):
				if log: logma.info(f"I {i}")
				thour = str(hour)
				if len(str(hour)) == 1:
					thour = f'0{hour}'
				j = i % len(minutes)
				if log: logma.info(f"J {j}")
				minute = minutes[j]
				if log: logma.info(f"Minute {minute}")
				# if log: print('TODO Action', self.config.dikt)
				l1 = pyqt.QHBoxLayout()
				l1.addWidget(annotations.NchantdLabel().initWidget({'text': f'{thour}:{minute}'}))
				l1.addWidget(editors.NchantdEntryBox(self).initWidget(None))
				l0.addLayout(l1)
				if cnt == len(minutes):
					hour += hour_inc
					if hour == 24:
						hour = 0
					cnt = 0
				cnt += 1
			l.addLayout(l0)
		layout.addLayout(l)
		cfg = {'label': 'Select Task', 'size': [500, 25]}
		layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
		self.setLayout(layout)
		return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
		return self

class NTDInputConcernTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDInputConcernTab, self).__init__(parent, self.config, singlepane)
	
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

class NTDInputEventTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDInputEventTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
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
		cfg = {'label': 'Focus Required: '}
		top_layout_left_left.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'small'))
		top_layout_left.addLayout(top_layout_left_left)

		calendar_time_layout_1.addWidget(calendars.NchantdDateTimeGroup(self, {}).initWidget())
		calendar_time_layout_2.addWidget(calendars.NchantdDateTimeGroup(self, {}).initWidget())
		
		top_layout_left.addLayout(calendar_time_layout_1)
		top_layout_left.addLayout(calendar_time_layout_2)
		
		top_layout.addLayout(top_layout_left)
		layout.addLayout(top_layout)
		layout.addWidget(controls.NchantdSaveButtons(self).initWidget(None))
		layout_recursion = pyqt.QVBoxLayout()
		cfg = {'label': 'Configuration Recursion: '}
		layout_recursion.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		layout.addLayout(layout_recursion)

		self.setLayout(layout)
		
		return self

class NTDInputResourceTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDInputResourceTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
		top_layout = pyqt.QHBoxLayout()
		
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

class NTDInputTaskTab(tabsets.NchantdTab):
	""""""
	
	def __init__(self, parent=None, cfg={}, singlepane=False):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDInputTaskTab, self).__init__(parent, self.config, singlepane)
	
	def buildPane(self):
		""" """
		layout = pyqt.QVBoxLayout()
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
		
		layout.addLayout(top_layout)
		layout.addWidget(controls.NchantdSaveButtons(self).initWidget(None))

		cfg = {'label': 'Assign Dependencies: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		cfg = {'label': 'Assign Dependants: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		cfg = {'label': 'Assign Resources: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))
		layout.addLayout(bottom_layout)
		self.setLayout(layout)
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
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Yesterdays Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Last Weeks Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
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
		layout.addWidget(calendars.NchantdMonthCalendar(self).initWidget())
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
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Operation Tasks Overview'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Operations Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
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
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Project Tasks Overview'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
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
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Project Tasks Overview'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
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
		top_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'Project Tasks Overview'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		cfg = {'label': 'Projects Top Level Tasks'}
		top_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
		layout.addLayout(top_layout)
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
		layout.addLayout(top_layout)
		
		split_type = 'children'
		bottom_layout = pyqt.QHBoxLayout()
		new_tasks = 2
		if split_type == 'children':
			bottom_layout = pyqt.QVBoxLayout()
			new_tasks = 3#get number from interface
		for task in range(new_tasks):
			notes = editors.NchantdEntryEditor(self, {"label": "Task A: "})
			bottom_layout.addWidget(notes.initWidget(None, 'medium'))

		layout.addLayout(bottom_layout)
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
		layout.addLayout(top_layout)
		
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

		layout.addLayout(bottom_layout)
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
		left_layout = pyqt.QVBoxLayout()
		left_layout.addWidget(NTDTaskTree(self).initWidget())
		layout.addLayout(left_layout)

		right_layout = pyqt.QVBoxLayout()
		right_layout.addWidget(calendars.NchantdGanttCanvas(self).initWidget())
		layout.addLayout(right_layout)

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
		self.config.override(cfg)
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
		layout = pyqt.QVBoxLayout()
		columns, rows = 2, 3
		for column in range(columns):
			row_layout = pyqt.QHBoxLayout()
			for row in range(rows):
				if row == 2 and column == 1:
					split_layout = pyqt.QVBoxLayout()
					cfg = {'label': 'Saturday', 'size': [500, 25]}
					split_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
					cfg = {'label': 'Sunday', 'size': [500, 25]}
					split_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None))
					row_layout.addLayout(split_layout)
				else:
					cfg = {'label': 'Day', 'size': [500, 25]}
					row_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'medium'))
				
			layout.addLayout(row_layout)
		self.setLayout(layout)
		return self
	
	def onEnterEvent(self):
		"""Run a save of the doc editor data to the database """
	
	def mousePressEvent(self, event):
		""" """
		editor.mousePressEventLog(event)
		super().mousePressEvent(event)
		return self


