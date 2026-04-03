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
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.groups import NchantdVScrollGroupBox
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, '_data_', 'socials.yaml')


class NchantdCommunityOverview(NchantdWidget):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdCommunityOverview')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdCommunityOverview, self).__init__(self.parent, self.config)
		self.communities = {}

	def initModel(self):
		""""""
		return self

	def initView(self):
		"""Show information across all possible socials for the given community

		looking for groups in the following socials


		show user counts etc any other data that can be pulled

		"""
		box = NchantdVScrollGroupBox()
		box.setTitle('Known Communities')
		for community in self.communities:
			cfg = {}
			communityW = NchantdCommunityCatalogItem(self, cfg).initWidget()
			box.addWidget(communityW)
		self.layout.addLayout(box.layout)
		return self

	def initWidget(self):
		""""""
		self.initModel()
		self.initView()
		return self

class NchantdTodayComms(NchantdWidget):
	""""""
	def __init__(self, parent=None, cfg=None):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NchantdTodayComms')
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdTodayComms, self).__init__(self.parent, self.config)

	def initModel(self):
		""""""
		super().initModel()
		return self

	def initView(self):
		""""""
		super().initView()
		return self

	def initWidget(self):
		""""""
		self.initModel()
		self.initView()
		return self

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
