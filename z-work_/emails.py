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
from os.path import dirname, join
# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from nchantrs.widgets import tabs
from _work import communicationmodels
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, '_data_', '.yaml')

class NchantdEmail(tabs.NchantdTab):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdEmail')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdEmail, self).__init__(self.parent, self.config)
		self.model = communicationmodels.NchantdEmailModel(self, self.config)

	def initModel(self):
		""""""
		return self

	def initView(self):
		""""""

		# self.emailsView = pyqt.QTableView()
		# self.emailsView.setModel(self.emails)
		# self.emailsView.setSelectionBehavior(pyqt.QAbstractItemView.SelectRows)
		# self.emailsView.setSelectionMode(pyqt.QAbstractItemView.SingleSelection)
		# self.emailsView.setSortingEnabled(True)
		# self.emailsView.setAlternatingRowColors(True)
		# self.emailsView.setEditTriggers(pyqt.QAbstractItemView.NoEditTriggers)
		# self.emailsView.verticalHeader().setVisible(False)
		# self.emailsView.horizontalHeader().setStretchLastSection(True)
		# self.emailsView.horizontalHeader().setSectionResizeMode(pyqt.QHeaderView.Stretch)
		return self

	def initWidget(self):
		""""""
		self.initModel()
		self.initView()
		return self

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
