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
from nchantrs.widgets import controls, tabs
from nchantrs.widgets.media import editors
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, '_data_', 'humans.yaml')

class NchantdHumanTimeUsageOverviewTab(tabs.NchantdTab):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('Nchantd')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdHumanTimeUsageOverviewTab, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		return self

	def initView(self):
		""""""
		return self

	def initWidget(self):
		""""""
		self.initModel()
		self.initView()
		return self

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
