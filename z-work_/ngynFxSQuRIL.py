#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
''' #																	||
--- #																	||
<(META)>: #																||
	DOCid: <^[uuid]^> #													||
	name:  ngynFxSQuRIL#
	description: > #													||
		Fractionally Executed SQL Queued Recursive Interaction Layer

		only one shared cache inmem db
		others must be private
		spin a process for each in memdb for each fileinmemdb needed
		use the single shared cache for the main app db have the name server
		communicate directly here

		inmemdb
		bigtable
		cmd = "CREATE TABLE bgtbl col0-col49"#use machine learning here

		appdb...one per device running application
		multiple interaction pathways
		filedbs...unknown number
		max attach is like 25dbs
		how to determine when a fileDB should get its own bigtable
		increased security
		how to implement permissions effectively??
		reduced overhead for lots of small workbooks using a combined bigtable
		process:
			load document
			get all sectn ids from file db and load into inmem big table
			map document table columns to bigtable columns
			read document
			check bigtable documents
			if no runs are connected to the current document...how to tell
			check m_run table
			check _run table
			once completed
			if not there:
				load document limit 0 to displaysize-y*(1+i%)
			if is there get first and lest seq
				compare against displaysize-y
					if not then grab additional
						check if first is 0 then get from bottom
					if not split gap and get from top first
						then from bottom
			also verify that full seq is available
			if not get
			next verify that all sectns are the most recent
			if there is not then
	expirary: <[expiration]> #											||
	version: <[version]> #												||
	path: <[LEXIvrs]>pheonix/elements/store/orgnql/sonql.py #			||
	outline: <[outline]> #												||
	authority: document|this #											||
	security: sec|lvl2 #												||
	<(WT)>: -32 #														||
''' #																	||
# -*- coding: utf-8 -*-
#=======================================================================||
import os, datetime as dt, pandas as pd, re#							||
import queue#															||
#=======================================================================||
import pyodbc as sql, sqlite3 as sql3#									||
from osbrain import run_nameserver, run_agent#							||
#=======================================================================||
from pheonix.elements.calcgen import text as calct#						||
from pheonix.elements.comm import comm#									||
from pheonix.elements.comm import log#									||
from pheonix.elements.config import config#								||
from pheonix.elements.exam import exam#									||
from pheonix.elements.rule import rule#									||
from pheonix.elements.thing import thing#								||
#=======================================================================||
here = os.path.join(os.path.dirname(__file__),'')#						||
there = os.path.abspath(os.path.join('../../..'))#						||set path at pheonix level
version = '0.0.0.0.0.0'#												||
#=======================================================================||
class fracExSQL(object):
	'Fractionally Executed Structure Query Language'
	version = '0.0.0.0.0.0'
	def __init(self, docUUID=None, data=None, cmd=None, tblMap=None, cfg=None, db=None):
		''
		pxcfg = here+'/ngynFxSQuRIL.yaml'
		self.config = config.instruct(pxcfg).override(cfg)
		if docUUID == None:
			docUUID = next(thing.what().uuid())
		self.docUUID = docUUID
		self.cmd = cmd
		if tblMap == None:
			self.refreshTableMap()
		else:
			self.tblMap = tblMap
		self.tblMap = tblMap
		if db == None:
			db = session.app('pyffice').install().db
		self.db = db
	def cmdFractionalizer(self, cmd, targets):
		'split cmd so that different sections can be pulled from different tables'
		'this is mainly intended to allow the use of the inmem database for active data'
		'and to take the same actions on stored data as well as moving the data between'
		'these states'

	def read(self, tipe='active'):
		''
		if tipe == 'active':#	||read data from inmem table for current interactions
			mapp = self.docMap[self.docUUID]
			self._conAPP(mapp['FILE'])
			self.doc = self.filedb.read(self.docUUID)
			#if read hits extents of active data and more is available then trigger a load read
		elif tipe == 'load':#	||read data from the ondisk table

		elif tipe == 'close':#	||read data from the ondisk table for version update comparisons
		return self
	def refreshTableMap(self):
		'Table map provides live mapping'
		self.tblMap =
		return self
	def write(self, tipe='crash'):
		''
		if tipe == 'active':#	||write data to new interaction data to the inmem table
		elif tipe == 'clean':#
		elif tipe == 'close':#	||write data from the inmem table tot the ondisk table for persistance
		elif tipe == 'crash':#	||emergency dump write of all in memory data
		elif tipe == 'load':#	||write data to the inmem table from the ondisk table
		return self
	def _conAPP(self):
		''
		try:
			self.appdb = sonql.doc(self.db)
		except Exception as e:
			self.appdb = None
			m = 'Connection to Pyffice App Failed'
			comm.log(self.db, e, m).toApp('fail')
		return self
	def _conFILE(self, filedb):
		''
		try:
			self.filedb = sonql.doc(filedb)
		except Exception as e:
			self.filedb = None
			m = 'Connection to Pyffice File Failed'
			comm.log(filedb, e, m).toUser('alert')
		return self
class chunk(encode.fxSQuRILchunker):
	def __init__(self):
		''
		pass
class memDB(db):
	def __init__(self, cfg=None):
		pxcfg = here+'/z-data_/FxSQuRIL.yaml'
		self.config = config.instruct(pxcfg).select('inmemdb').override(cfg)
		self.name = self.config.dikt['Name']
		self.path = 'file:'+self.name+':memory:?cache=shared'
	def _conx(self):
		''
		self.conn = sql3.connect(self.name, uri=True)
	def init(self):
		bigTable(contentcols=None)
		#need to check if bigtable exists and if so increment
		#create unioning view from incremented table
		#union current bigtable for immediate needs
		#replace original bigtable with new one
		idcols = self.config['tables']['bigtable']['size']['columns']['ids']
		ncols = self.config['tables']['bigtable']['size']['columns']['content']['min']
		cntcols = []
		for col in range(ncols):
			cntcols.append('col'+str(col))
		admincols = ['tables']['bigtable']['size']['columns']['admins']
		cols = idcols+cntcols+admincols
		FxTable()
		'load functions from any active languages'
		'Python, Excel, LEXI,....add as you go'
		initMsgTable()
		initOpenDocsTable()
		'Used to translate state between inmembigtable and appdb/filedb'
		initIsolatedTable()
		'An Isolated Table is used for a intensive datasets needing their own structure'
		initRunTable()
		cacheTable()
		'write everything in memory db to a on disk cache table'
		'set startup flag to parse anything left on next start'
		'then parsing cache table and storing updates correctly'
		'this is intended to save data quickly to reduce data loss from unexpected closing'
	def deconstruct(self):
		'take all data from the in memDB and store permanetly to the file and app db'
		return self
class appDB(db):
	def __init__(self):
		''
	def manageDocDBs(self):
		''
		return self
	def initPerfTable(self):
		''
		return self
class fileDB(db):
	def __init__(self):
		''
		return self
#==========================Source Materials=============================||
'''
https://www.eversql.com/faster-pagination-in-mysql-why-order-by-with-limit-and-offset-is-slow/
https://www.sqlite.org/backup.html
https://www.sqlite.org/inmemorydb.html
https://www.sqlite.org/malloc.html
'''
#============================:::DNA:::==================================||
'''
<(DNA)>:
	201804101534:
		coupling:
			version: <[active:.version]>
			test:
			description: >
				Couple tmplts and data with rule systems implicitally
				and explicitally
			work:
	201804101534:
		here:
			version: <[active:.version]>
			test:
			description: >
				Define Rule Routing for Utilization of Multiple Rule Systems
			work:
'''
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
