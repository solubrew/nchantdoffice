#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																			||
---  #																			||
<(META)>:  #																	||
	docid:    #								||
	name: #													||
	description: >  #															||
	expirary: <[expiration]>  #													||
	version: <[version]>  #														||
	authority: document|this  #													||
	security: sec|lvl2  #														||
	<(WT)>: -32  #																||
''' #																			||
# -*- coding: utf-8 -*-#														||
#=================================Core Modules==================================||
from os.path import abspath, dirname, exists, join
#===============================================================================||
import crow
#===============================================================================||
from condor import condor#										||
from nchantrs import nchantrs
from nchantrs.dialogs.dialogs import Sigil
from nchantrs.dialogs import prefs
from models import NFAppModel
import widgets
#===============================================================================||
here = join(dirname(__file__),'')#												||set path at pheonix level
log = True
#===============================================================================||

pxcfg = join(abspath(here), '_data_', 'dialogs.yaml')

class NFApplicationPreferences(prefs.Preferences):
	''' '''

	def __init__(self):
		super(ApplicationPreferences, self).__init__(self)
		mainLayout = QVBoxLayout()
		mainLayout.addWidget(sitelauncher)

	def getApiKey(self):
		'''Add a launcher widget to the top of the preferences tab'''
		self.sitelauncher = Button('Get API Key for Free')


class NFAccountEntry():
	''' '''

	def __init__(self):
		''' '''
		self.config = condor.instruct(pxcfg).override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('NFAccountEntry\n', self.config.dikt.keys())
		super(NFAccountEntry, self).__init__(name, parent)#					||


class NFExpenseEntry():
	''' '''

	def __init__(self):
		''' '''
		self.config = condor.instruct(pxcfg).override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('NFExpenseEntry\n', self.config.dikt.keys())
		super(NFExpenseEntry, self).__init__(name, parent)#					||


class NFInstitutionEntry():
	''' '''

	def __init__(self):
		''' '''
		super(NFInstitutionEntry, self).__init__(name, parent)#					||


class NFRevenueEntry():
	''' '''

	def __init__(self):
		''' '''
		self.config = condor.instruct(pxcfg).override(cfg)
		if parent:
			self.config.override(parent.config)
		if log: print('NFRevenueEntry\n', self.config.dikt.keys())
		super(NFRevenueEntry, self).__init__(name, parent)#					||
