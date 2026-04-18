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
from kahndor import kahndor
from kahndor.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, '_data_', '.yaml')


class :
	""""""
	def __init__(self, cfg=None):
		""""""
		self.config = kahndor.instruct(pxcfg).select('').override(cfg)
		dark_grey = (26, 31, 40)
		green = (47, 230, 23)
		red = (232, 18, 18)
		orange = (226, 116, 17)
		yellow = (237, 234, 4)
		purple = (166, 0, 247)
		cyan = (21, 204, 209)
		blue = (13, 64, 216)
		white = (255, 255, 255)
		dark_blue = (44, 44, 127)
		light_blue = (59, 85, 162)

		@classmethod
		def get_cell_colors(cls):
			return [cls.dark_grey, cls.green, cls.red, cls.orange

# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
