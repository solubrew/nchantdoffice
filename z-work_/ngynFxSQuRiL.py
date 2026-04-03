#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||
'''
---
<(META)>:
	DOCid: <^(UUID)^>
	name:
	description: >
		Fractionally Executed SQL Queued Recursive Interaction Layer

		only one shared cache inmem db others must be private
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
	expirary: <[expiration]>
	version: <[version]>
	path: <[LEXIvrs]>
	outline: <[outline]>
	authority: document|this
	security: sec|lvl2
	<(WT)>: -32
'''
# -*- coding: utf-8 -*-
#===============================================================================||
import os, datetime as dt, pandas as pd, re#									||
from multiprocessing import Process#											||
import queue#																	||
#===============================================================================||
import pyodbc as sql, sqlite3 as sql3#											||
from osbrain import run_nameserver, run_agent#									||
#===============================================================================||
from pheonix.elements.calcgen import text as calct#								||
from pheonix.elements.comm import comm#											||
from pheonix.elements.comm import log#											||
from pheonix.elements.config import config#										||
from pheonix.elements.exam import exam#											||
from pheonix.elements.rule import rule#											||
from pheonix.elements.thing import thing#										||
#===============================================================================||
here = os.path.join(os.path.dirname(__file__),'')#								||
there = os.path.abspath(os.path.join('../../..'))#								||set path at pheonix level
version = '0.0.0.0.0.0'#														||
#===============================================================================||
class fxsquril(object):
	'''Fractionally Executed Structure Query Language
		Distribute Data between the inMemory DB and persistent Stores'''
	version = '0.0.0.0.0.0'
	def __init__(self, nameserver, docUUID=None, data=None, cmd=None, tblMap=None, cfg=None, db=None)):#									||
		'''Data Router'''#															||
		pxcfg = here+'/ngynFxSQuRIL.yaml'
		self.config = config.instruct(pxcfg).override(cfg)
	def init(self):
		''' '''
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
		self.config = config.instruct(pxcfg).override(cfg)#						||
		self.nameserver = nameserver#											||
		self.queue = queue.Queue()#												||
		self.go = True#															||
		self.listen()
		self.path = 'file:'+self.name+':memory:?cache=shared'
	def cacheTable(self):
		'''write everything in memory db to a on disk cache table
		set startup flag to parse anything left on next start
		then parsing cache table and storing updates correctly
		this is intended to save data quickly to reduce data loss from unexpected closing'''
		return self



	def new(self):
		''' '''
		create('FileOnDiskDB')
	def open(self):
		''' '''
		create('FileInMemDB')
	def setup(self):
		'''Create database for application'''
		if self.session.dbapp == None:
			create('AppOnDiskDB')
		create('AppInMemDB')
	def start(self):
		''' '''
		create('SharedInMemDB')
	def _conx(self):
		''
		self.conn = sql3.connect(self.name, uri=True)
	def initBigTable(self, contentcols=None):
		''
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
	def initFxTable(self):
		'load functions from any active languages'
		'Python, Excel, LEXI,....add as you go'
		return self
	def initOpenDocsTable(self):
		'Used to translate state between inmembigtable and appdb/filedb'
		return self
	def initIsolatedTable(self):
		'An Isolated Table is used for a intensive datasets needing their own structure'
		return self

	def listen(self):
		''
		wati = 0
		while self.go == True:
			poll()
			if response == None and wait < 5000:
				wait += 0.1
			else:
				wait = 0
			time.sleep(wait)
	def getQueue(self):
		''
		return self.queue
	def writeQueue(self):
		''
		self.queue.write()
	def processQue(self):
		#need to be very careful about the use of parallel processing here
		#if possible take advantage for speed but becareful and error to safe side
		self.pool = mp.Pool()
		while task in self.queue:
			self.runAction(task)
	def runAction(self, task):
		obj = getattr(self, task['how'])
		self.status[task['id']] = obj(task)
		return self
	def cmdFractionalizer(self, cmd, targets):
		'''split cmd so that different sections can be pulled from different tables
		this is mainly intended to allow the use of the inmem database for active data
		and to take the same actions on stored data as well as moving the data between
		these states'''
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
	def write(self, tipe='crash'):
		''
		if tipe == 'active':#	||write data to new interaction data to the inmem table
			pass
		elif tipe == 'clean':#
			pass
		elif tipe == 'close':#	||write data from the inmem table tot the ondisk table for persistance
			pass
		elif tipe == 'crash':#	||emergency dump write of all in memory data
			pass
		elif tipe == 'load':#	||write data to the inmem table from the ondisk table
			pass
		return self
	def _conAPP(self, gchunk=None, schunk=None, cfg=None):
		''
		try:
			self.appdb = sonql.doc(self.db)
		except Exception as e:
			self.appdb = None
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
		pxcfg = here+'/cfg/ngynFxSQuRIL.yaml'
		self.config = config.instruct(pxcfg).select('sectn').override(cfg)
		self.seqCodes = self.getCodes('seq')
		self.sizeCodes = self.getCodes('size')
	def carveSource(self):
		self.sectnUUID = self.schunk['sectnUUID']
		self.sectnSize = self.schunk['sectnSize']
		self.text = self.schunk['Text']
		self.dtid = self.schunk['DTID']
		self.tipe = self.schunk['Type']
		self.state = self.schunk['State']
	def getCodes(self, part):
		codes = []
		for sectn in self.config.dikt[part]['codes']:
			codes.append(sectn['symbol'])
		return codes
	def grab(self):
		''
		self.text = text
		self.size = size
		return self
	def split(self):
		''
		return self
	def decodeSeq(self):
		cols, rows= size.split([',','.','|'])
		nrow = [sectnUUID, seq]
		for col in cols:
			for row in rows:
				for line in text.split('\n'):
					tbl.append(line)
		return self
	def encodeSeq(self, cnt, seq):
		''
		return self
	def decodeText(self):
		''
		return self
	def encodeText(self, uuid=None):
		''
		if uuid == None:
			sectnUUID = thing.what().uuid
		return self
def create(db, cfg):
	''' '''
	tables = cfg[db]['tables']
	for table in tables:
		newtable(table, tables[table])
	return
def newtable(table, data):
	''' '''
	cmd = data['cmd']
	execute(cmd)
#===============================Source Materials================================||
'''
https://www.eversql.com/faster-pagination-in-mysql-why-order-by-with-limit-and-offset-is-slow/
https://www.sqlite.org/backup.html
https://www.sqlite.org/inmemorydb.html
https://www.sqlite.org/malloc.html
'''
#==================================:::DNA:::====================================||
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
