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

# -*- coding: utf-8 -*-
from __future__ import annotations
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
import datetime as dt
from typing import Self

# ======================================3rd Party Library Modules=====================================================||
import feedparser

# ======================================Solutions Brewer Library Modules==============================================||
from kahndor import kahndor
from nchantrs.libraries import pyqt
from nchantrs.widgets.groups import NchantdVScrollGroupBox
from nchantrs.widgets.widgets import NchantdWidget
from nchantrs.widgets.annotations import NchantdLabel
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), "")  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, "_data_", ".yaml")


class NchantdCommunitiesSummary(NchantdWidget):
	""""""

	def __init__(self, parent=None, cfg=None) -> None:
		""" """
		logma.info(f"NchantdCommunitiesSummary init: parent={type(parent).__name__}")
		self.parent = parent
		self.config = kahndor.Instruct(pxcfg).select("NchantdCommunitiesSummaryTab")
		if self.parent:
			self.config.override(parent.config)
		self.config.override(cfg)
		super(NchantdCommunitiesSummary, self).__init__(self.parent, self.config)

	def initModel(self) -> Self:
		""""""
		return self

	def initView(self) -> Self:
		""""""
		super().initView()
		group_box = NchantdVScrollGroupBox()
		group_box.setTitle("Communities")
		self.layout.addLayout(group_box.layout)
		return self

	def initWidget(self) -> Self:
		""""""
		self.initModel()
		self.initView()
		return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||