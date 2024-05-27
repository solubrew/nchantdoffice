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
import datetime as dt
# ===============================================================================||
from ogma.logma import Logma

# ===============================================================================||
here = join(dirname(__file__), '')  # ||
log = True
logma = Logma(__name__)

# ===============================================================================||
pxcfg = join(here, '_data_', 'models.yaml')

class Resource():
	""""""
	def __init__(self, name, fungibility):
		""""""
		self.name = name
		self.schedule = {}
		self.fungibility = fungibility

	def build_schedule(self, inc=15):
		"""
		self.schedule can contain
	
		a status of ONTRACK, OVERLOADED, UNTRACKED
		the state can be PAST, CURRENT, FUTURE
	
		:param inc:
		:return:
	
		"""
		for t in range(0, 24 * 60, inc):
			t = dt.timedelta(minutes=t)
			logma.info(str(t)[:str(t).rfind(':')])
			self.schedule[str(t)[:str(t).rfind(':')]] = {'events': [], 'tasks': [],
			                                             'status': 'ONTRACK', 'state': 'FUTURE'}
		return self
	

class Resource_Human(Resource):
	""""""
	def __init__(self, name, fungibility=0.7):
		""""""
		Resource.__init__(self, name, fungibility)

	def default_routine(self, window='daily'):
		""""""
		if window == 'daily':
			sleep_start_tm = ''
			sleep_end_tm = ''
			sleep_tms = {'main': 480}
			
			eat_tms = {'breakfast': 30, 'lunch': 30, 'dinner': 30}
		elif window == 'weekly':
			#standard weekly work 40 hours
			#2 day weekend
			pass
		elif window == 'monthly':
			#standard pill payments
			pass
		elif window == 'yearly':
			#
			pass
		elif window == 'life':
			#
			pass
		return self

class Resource_Machine(Resource):
	""""""
	def __init__(self, name, fungibility=0.9):
		""""""
		Resource.__init__(self, name, fungibility)

class Resource_Consumable(Resource):
	""""""
	def __init__(self, name):
		""""""
		Resource.__init__(self, name, 0.99)

