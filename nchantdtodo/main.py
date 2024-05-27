# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""  #																	||
---  #																	||
<(META)>:  #															||
	docid:   #															||
	name:	#														||
	description: >  #													||
	expirary: <[expiration]>  #											||
	version: <[version]>  #												||
	path: <[LEXIvrs]>  #												||
	outline: <[outline]>  #												||
	authority: document|this  #											||
	security: sec|lvl2  #												||
	<(WT)>: -32  #														||
"""  # ||
# -*- coding: utf-8 -*-#														||
# ===============================Core Modules====================================||
import sys
from os.path import abspath, dirname, join
# ===============================================================================||
import crow
crow.crowLoad('NchantdTODO', 'DELTA')

from condor import condor
from nchantrs.nchantrs import NchantdCloak
from ogma.logma import Logma

# =======================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# =======================================================================||
pxcfg = join(here, '_data_', 'nchantdtodos.yaml')

class NchantdTODOs(NchantdCloak):
	""" """
	def __init__(self, args, parent=None):
		""" """
		#ucfg = f'{there}/_data_/user.yaml'
		self.config = condor.instruct(pxcfg).load().addArgs(args)
		if parent:
			self.config.override(parent.config)
		super(NchantdTODOs, self).__init__('NchantdTODOs', self.config)
		self.model.initModel()
		self.initApp()

	def setup(self):
		""""""
		self.applicationSetup()
		return self
	
	def applicationSetup(self):
		""" """
		self.newApp = True
		self.instanceSetup()
		self.newApp = False
		return self
	
	def instanceSetup(self):
		""" """
		self.newInstance = True
		self.newInstance = False
		return self

	def updateDataModels(self):
		""""""


if __name__ == '__main__':
	NchantdTODOs(sys.argv)
