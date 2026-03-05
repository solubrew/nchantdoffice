# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
---
<(META)>:
	docid: <^(UUID)^>
	name:
	description: >
	expirary: <[expiration]>
	version: <[version]>
	path: <[LEXIvrs]>
	outline: <[outline]>
	authority: document|this
	security: sec|lvl2
	<(WT)>: -32
"""
# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
from os.path import abspath, dirname, exists, join
from sys import argv
import datetime as dt

# ===============================================================================||
# from crow import  # Commented out crowLoad
crowLoad('NchantdTodo', 'DELTA')
# ===============================================================================||

from nchantdtodo.main import NchantdTODOs
from ogma.logma import Logma

# ===============================================================================||
there = abspath(join(''))
here = join(dirname(__file__), '')
log = True
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, '_data_', 'runTab.yaml')

def runApplication(seq):
	"""Run individual tabs with mock data for development purposes"""
	NchantdTODOs(argv)

if __name__ == '__main__':
	start = dt.datetime.now()
	print('Start', start)
	runApplication(argv)
	end = dt.datetime.now()
	print('End', end)
