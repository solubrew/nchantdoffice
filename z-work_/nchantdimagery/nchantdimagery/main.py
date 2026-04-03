#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@nchantdTree - Main@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''  #																			||
---  #																			||
<(META)>:  #																	||
	docid: '608908e5-ec15-402a-9096-7e3533ccce94'  #							||
	name: Nchantd Imagery#														||
	description: >  #															||
	expirary: <[expiration]>  #													||
	version: <[version]>  #														||
	authority: document|this  #													||
	security: sec|lvl2  #														||
	<(WT)>: -32  #																||
''' #																			||
# -*- coding: utf-8 -*-#														||
#=================================Core Modules==================================||
import sys#																		||
from os.path import abspath, dirname, exists, join, expanduser#					||
#===============================================================================||
import crow#																	||
#===============================================================================||
from condor import condor#														||
from nchantrs.nchantrs import NchantdCloak#										||
#===============================================================================||
there = abspath(join(''))#														||set path at pheonix level
here = join(dirname(__file__),'')#												||
log = True#																		||
#===============================================================================||
pxcfg = join(abspath(there), '_data_', 'nchantdimagery.yaml')#					||

class NchantdImagery(NchantdCloak):#											||
	'''A desktop application for managing image files through efficent chunking
		and thumbnail views to move between a selected directory and
		the directory tree.  Additional tabs integrating some various
		image tools
			- Stable Diffusion
			- Background Removal
			-
		'''#																	||

	def __init__(self, args):#													||
		self.config = condor.instruct(pxcfg).load().addArgs(args)#				||
		super(NchantdImagery, self).__init__('NchantdImagery')#					||
		self.initApp()

if __name__ == '__main__':#														||
	NchantdImagery(sys.argv)#													||
#===========================Code Source Examples================================||
'''
'''
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
