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
import unittest
import pytest
# -*- coding: utf-8 -*-
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join
from sys import argv
import datetime as dt

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
# import crow  # Commented out - not needed for local system
# crow.crowLoad removed

from condor import condor
from ogma.logma import Logma
from test_nchantdoffice.nchantdoffice.nchantdofficeTEST import Test_NchantdOfficeCloak

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
logma = Logma(__name__)
log = True

# ====================================================================================================================||
pxcfg = join(here, '_data_', '.yaml')

def run(args):
	""""""
	if args[1] == 'all':
		test = Test_NchantdOfficeCloak.setup_class()
		test.test_all()
		test.teardown_class()

if __name__ == '__main__':
	start = dt.datetime.now()
	logma.info(f'Start {start}')
	run(argv)
	end = dt.datetime.now()
	logma.info(f'Start {start}')
	logma.info(f'End {end}')
	logma.info(f'End Duration {end - start}')


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
