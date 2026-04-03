# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""  #																			||
---  #																			||
<(META)>:  #																	||
	docid: '' #								||
	name: Xochi Game Engine Run Commands Python Document  #							||
	description: >  #															||

	expirary: '<[expiration]>'  #												||
	version: '0.0.0.0.0.0'  #													||
	path: ''  #										||
	authority: 'document|this'  #												||
	security: 'sec|lvl2'  #														||
	<(WT)>: -32  #																||
"""  # ||
# -*- coding: utf-8 -*-#														||
# ==================================Core Modules=================================||
from os.path import abspath, dirname, expanduser, join  # ||
from sys import argv

# ===============================================================================||
import pygame

# ===============================================================================||
import crow
crow.crowLoad('DELTA')

from condor import condor
from fxsquirl import collector
from ogma.logma import Logma

# ===============================================================================||
from xochi.xochi import Xochi
from xochi.leveleditor import XochiLevelEditor

# ================Common Globals=================================================||
here = join(dirname(__file__), '')  # ||
version = '0.0.0.0.0.0'  # ||
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(abspath(here), '_data_', 'run.yaml')
cfg = condor.instruct(pxcfg).load()

def run(seq):
	""" """
	if seq[1] == 'tic-tac-toe':
		game = Xochi().run(seq[1])
	elif seq[1] == 'crossword':
		game = Xochi().run(seq[1])
	elif seq[1] == 'wordle':
		game = Xochi().run(seq[1])
	elif seq[1] == 'hangman':
		game = Xochi().run(seq[1])
	elif seq[1] == 'snake':
		game = Xochi().run(seq[1])
	elif seq[1] == 'mario':
		game = Xochi().run(seq[1])
	elif seq[1] == 'level_editor':
		setup = True
		game = XochiLevelEditor(cfg, setup).run(seq[1])


if __name__ == '__main__':
	""" """
	run(argv)