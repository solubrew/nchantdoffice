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
from crow import crowLoad
crowLoad('NchantdTodo', 'DELTA')
# ===============================================================================||

from condor import condor  # ||
from nchantrs.dialogs.dialogs import NchantdCape
from nchantdtodo.resource import Resource_Human
from ogma.logma import Logma

# ===============================================================================||
there = abspath(join(''))
here = join(dirname(__file__), '')
log = True
logma = Logma(__name__)


# ===============================================================================||
pxcfg = join(here, '_data_', 'runTab.yaml')

class NchantdTab(NchantdCape):
	"""A Dialog for entrying Account Addresses with detail information into a
		table"""
	def __init__(self, args):
		"""Create new database eventually have checks in place so as not to
			delete user db also have a way of backing up any nonblockchain data
			so it can be selectively reimported to a new database if needed"""
		ucfg = f'{there}/_data_/user.yaml'
		self.config = condor.instruct(pxcfg).override(ucfg).addArgs(args)
		if log: logma.info(f'CONFIG {self.config.dikt.keys()}')
		super(NchantdTab, self).__init__('NchantdTab', self.config)
		self.initApp()

def runApplication(seq):
	"""Run individual tabs with mock data for development purposes"""
	NchantdTab(seq)

if __name__ == '__main__':
	start = dt.datetime.now()
	print('Start', start)
	runApplication(argv)
	end = dt.datetime.now()
	print('End', end)
