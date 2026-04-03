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
import datetime as dt
# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from nchantrs.libraries import pyqt
from nchantrs.widgets import tabs
from nchantrs.widgets.media import editors
from nchantrs.widgets.controls import controls
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, '_data_', 'concerns.yaml')


class NchantdAddConcernTab(tabs.NchantdTab):
	"""
	"""
	# TODO: Move tab to Concerns Node
	def __init__(self, parent=None, cfg={}, singlepane=False):
		"""
		Initializes an instance of the NTDAddConcernTab class.

		:param parent: The parent widget (default value is None).
		:type parent: QWidget
		:param cfg: The configuration dictionary (default value is an empty dictionary).
		:type cfg: dict
		:param singlepane: Controls whether the tab uses a single pane layout (default value is False).
		:type singlepane: bool
		"""
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDTaskSplitterTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super().__init__(parent, self.config, singlepane)

	def initView(self):
		"""
		Builds the pane for the application.

		:return: The built pane.
		"""
		layout = pyqt.QVBoxLayout()
		top_layout = pyqt.QHBoxLayout()

		top_layout.addWidget(controls.NchantdSaveButtons(self).initWidget(None))
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

		bottom_layout = pyqt.QHBoxLayout()
		cfg = {'label': 'List of Concerns: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))

		cfg = {'label': 'Assign Resources: '}
		bottom_layout.addWidget(editors.NchantdEntryEditor(self, cfg).initWidget(None, 'large'))

		layout.addLayout(bottom_layout)
		self.setLayout(layout)

		return self


class NchantdConcernManagementTab(tabs.NchantdTab):
	"""

	"""
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDConcernManagementTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super().__init__(parent, self.config, singlepane)

	def initModel(self):
		""""""
		return self

	def initView(self):
		"""
		Builds a pane layout for the GUI.

		:return: The built pane layout.
		:rtype: PyQt5.QtWidgets.QVBoxLayout
		"""
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

	def initWidget(self):
		""""""
		return self


class NchantdConcernsManagementTab(tabs.NchantdTab):
	"""
	"""
	def __init__(self, parent=None, cfg={}, singlepane=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg)
		self.config.select('NTDConcernsManagementTab').override(cfg)
		if parent:
			self.config.override(parent.config)
		super().__init__(parent, self.config, singlepane)

	def initModel(self):
		""""""
		return self

	def initView(self):
		"""
		Builds a pane layout for the GUI.

		:return: The built pane layout.
		:rtype: PyQt5.QtWidgets.QVBoxLayout
		"""
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

	def initWidget(self):
		""""""
		return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
