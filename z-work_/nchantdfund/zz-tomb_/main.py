#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																	||
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
''' #																	||
# -*- coding: utf-8 -*-#														||
#===============================Core Modules====================================||
import sys
from os.path import abspath, dirname, join
#===============================================================================||
import crow

from condor import condor
from nchantrs.libraries import pyqt
from nchantrs.nchantrs import NchantdCloak
from nchantrs.models import applicationmodels, treemodels
#=======================================================================||
here = join(dirname(__file__),'')#										||
there = abspath(join('../../..'))#										||set path at pheonix level
version = '0.0.0.0.0.0'#												||
log = True
#=======================================================================||
pxcfg = f'{here}_data_/nchantdfund.yaml'
class NchantdFund(NchantdCloak):
	''' '''
	def __init__(self, args, parent=None):
		''' '''
		ucfg = f'{there}/_data_/user.yaml'
		self.config = condor.instruct(pxcfg).override(ucfg).addArgs(args)
		if parent:
			self.config.override(parent.config)
		super(NchantdFund, self).__init__('NchantdFund', self)
		self.model.initModel()
		self.initApp()
	def setup(self):
		''''''
		self.applicationSetup()
		return self
	def applicationSetup(self):
		''' '''
		self.newApp = True
		self.instanceSetup()
		self.newApp = False
		return self
	def instanceSetup(self):
		''' '''
		self.newInstance = True
		self.model.updateData()
		self.newInstance = False
		return self
	def updateDataModels(self):
		''' '''
		return self
if __name__ == '__main__':
	NchantdFund(sys.argv)
