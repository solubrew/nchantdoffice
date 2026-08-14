# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
"""
NchantdAXN Main Entry Point

Run the NchantdAXN application with optional arguments.
"""
# -*- coding: utf-8 -*-
# ================================Core Modules===================================||
import sys
from os.path import dirname

# Add project to path
here = dirname(dirname(abspath(__file__)))
sys.path.insert(0, here)

# ===============================================================================||
from nchantdaxn.main import NchantdAXN

abspath = None  # noqa: F821  # placeholder until refactor

# ===============================================================================||

if __name__ == '__main__':
	# Run the application
	app = NchantdAXN(sys.argv)
	app.setup()
	app.run()
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
