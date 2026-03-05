# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""  #																			||
---  #																			|
<(META)>:  #																|
	docid:   #															|
	name:	NchantdAXN Application										|
	description: >  #														|
		GUI application for managing AXN tasks and ProjectAXN projects.	|
		Built on the Nchantrs framework.									|
	expirary: <[expiration]>  #											|
	version: <[version]>  #												|
	path: nchantdaxn.main  #												|
	authority: document|this  #											|
	security: sec|lvl2  #													|
	<(WT)>: -32  #														|
"""  # ||
# -*- coding: utf-8 -*-#														||
# ===============================Core Modules====================================||
import sys
from os.path import abspath, dirname, join

# ===============================================================================||
import crow
crow.crowLoad('NchantdAXN', 'ARTHR-WS')

from condor import condor
from nchantrs.nchantrs import NchantdCloak
from ogma.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, '_data_', 'nchantdaxn.yaml')


class NchantdAXN(NchantdCloak):
	"""
	Main application class for NchantdAXN.
	Manages AXN tasks and ProjectAXN projects with GUI.
	"""
	
	def __init__(self, args, parent=None):
		"""
		Initialize the NchantdAXN application.
		
		:param args: Command line arguments.
		:param parent: Parent object (optional).
		"""
		self.config = condor.instruct(pxcfg).load().addArgs(args)
		if parent:
			self.config.override(parent.config)
		
		# Set AXN paths from config
		axn_path = self.config.dikt.get('axn_path', '/home/solubrew/.arthr/workspace/axn')
		self.config.dikt['axn_path'] = axn_path
		self.config.dikt['shared_path'] = axn_path
		
		super(NchantdAXN, self).__init__('NchantdAXN', self.config)
		
		# Initialize the model
		self.model.initStores()
		self.initApp()

	def setup(self):
		"""Perform application setup."""
		self.applicationSetup()
		return self

	def applicationSetup(self):
		"""Setup the application instance."""
		self.newApp = True
		self.instanceSetup()
		self.newApp = False
		return self

	def instanceSetup(self):
		"""Setup a new application instance."""
		self.newInstance = True
		# TODO: Load last session or create new
		self.newInstance = False
		return self

	def updateDataModels(self):
		"""Update data models from AXN stores."""
		pass


# Entry point
if __name__ == '__main__':
	NchantdAXN(sys.argv)
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
