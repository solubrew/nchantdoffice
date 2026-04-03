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
class dataRTR(object):#													||
	'Distribute Data between the inMemory DB and persistent Stores'
	def __init__(self, nameserver, cfg=None):#							||
		'Data Router'#							||
		self.config = config.instruct(pxcfg).override(cfg)#				||
		self.nameserver = nameserver#									||
		self.queue = queue.Queue()#										||
		self.go = True#													||
		self.listen()
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
	def genSQLCMD(self):
		''
		cmd = sonql.doc()
		return self
	def mapTables(self):
		''
		#get dbs from nameserver
		return self

class fracExSQL(object):
	'Fractionally Executed Structure Query Language'
	version = '0.0.0.0.0.0'
	def __init(self, cmd, tblMap):
		''
		self.cmd = cmd
		self.tblMap = tblMap
	def refreshTableMap(self):
		''
		return self
	def cmdFractionalizer(self):
		'split cmd so that different sections can be pulled from different tables'
		'this is mainly intended to allow the use of the inmem database for active data'
		'and to take the same actions on stored data as well as moving the data between'
		'these states'
	def write(self):
		''
		return self
	def read(self):
		''
		return self
	def _write2inMemShare(self):
		''
		return True
	def _write2AppDB(self):
		''
		return True
	def _write2FileDB(self):
		''
		return True
	def _readinMemShare(self):
		''
		return self
	def _readAppDB(self):
		''
		return self
	def _readFileDB(self):
		''
		return self
class chunk(object):
	def __init__(self, chunk):
		self.chunk = chunk
		self.sectnUUID = chunk['sectnUUID']
		self.sectnSize = chunk['sectnSize']
		self.text = chunk['Text']
		self.dtid = chunk['DTID']
		self.tipe = chunk['Type']
		self.state = chunk['State']
	def expand(self):
		''
		self.decoded = encoder(self.text, self.sectnSize).decode()
		return self
	def compact(self):
		''
		self.encoded = encoder(self.text, self.sectnSize).encode()
		return self
	def calcSize(self):
		''
		return self
class encoder(object):
	def __init__(self, text, size):
		''
		self.text = text
		self.size = size
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

		return self
class memDB(db):
	def __init__(self, cfg=None):
		pxcfg = here+'/z-data_/FxSQuRIL.yaml'
		self.config = config.instruct(pxcfg).select('inmemdb').override(cfg)
		self.name = self.config.dikt['Name']
		self.path = 'file:'+self.name+':memory:?cache=shared'
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
	def initMsgTable(self):
		''

		return self
	def initOpenDocsTable(self):
		'Used to translate state between inmembigtable and appdb/filedb'

		return self
	def initIsolatedTable(self):
		'An Isolated Table is used for a intensive datasets needing their own structure'
		return self
	def initRunTable(self):
		''
		return self
	def cacheTable(self):
		'write everything in memory db to a on disk cache table'
		'set startup flag to parse anything left on next start'
		'then parsing cache table and storing updates correctly'
		'this is intended to save data quickly to reduce data loss from unexpected closing'
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
class db(object):
	'Control I/O for relational database formats'#						||=>Describe class
	version = '0.0.0.0.0.0'#											||=>Set version
	def __init__(self, doc, kind=None, params=None, cfg=None):#			||=>
		self.doc = doc#													||set doc var
		pxcfg = here+'z-data_/ngynFxSQuRIL.yaml'#							||assign default config
		self.config = config.instruct(pxcfg).override(cfg)#				||load config
		self._findDBType()#												||
		db = {'server': '', 'database': self.doc}#						||
		self._conx(db)#													||
	def _conx(self, db=None):#											||
		'Connect to Database'#											||
		try:#														||
			dpath = calct.stuff(db).path()
			if not dpath.valid:
				os.makedirs(dpath.it)
			self.conn = sql3.connect(dbase)#						||assign db connection
		except Exception as e:#										||
			m = ['Database connection to',db,'failed due to',e]#	||
			log.WORKLOG(e,m,db)#									||
			comm.see(m)#											||
		return self#														||
	def read(self, fill=None, cfg={}, cmd={}):#						||
		'Return iterator object to pull data in chunks via offset'
		if 'adders' not in cfg.keys():
			cfg['adders'] = []
		if 'page' not in cfg.keys():
			cfg['page'] = 100
		if 'fill' not in cfg.keys():
			cfg['fill'] = {}
		if cmd in list(self.config[self.dbtype]['cmds'].keys()):
			cmd = self.config[self.dbtype]['cmds'][cmd]
		cfg['cmds'] = cmd
		cfg['fill']['<[limit]>'] = cfg['page']
		cfg['fill']['<[offset]>'] = 0
		if fill != None:
			for k in fill.keys():
				cfg['fill'][k] = fill[k]
		cfg['adders'].append(self.config['SQLT']['adders']['limitoffset'])
		self.build = {}
		if 'tables' in cfg.keys():
			for table in cfg['tables']:
				if table not in self.build.keys():
					self.build[table] = {}
		self.builder('SELECT', cfg['cmds'], cfg)
		while self.build != {}:
			self.execute('read', cfg)
			cfg['fill']['<[offset]>'] += cfg['page']
			print(cfg['fill']['<[offset]>'])
			self.dikt = self.build
			self.go = True
			yield self
		self.go = False
		yield self
	def write(self, data, ext='.sqlite', cfg=None):#							||
		self.build = data#											||{table: records}
		self.builder('CRE')#									||
		self.execute('cre')#										||
		self.builder('INS')#									||
		self.execute('write')#										||
	def fraqBuilder(self, how='SELECT', gcmd={}, cfg=None):#				||
		'Build Fractional Query to be executed across databases'#		||
		self.cmdr = {}#													||set sql cmd container
		self._admin()#													||get admin columns
		if gcmd == {}:#													||check for given cmd
			if self.build == {}:#										||
				self.getInfo()#											||get database info
			if self.build.keys() == {}:#								||
				self.getTables(self.build.keys())#						||
			for table in self.build.keys():#							||
				if 'columns' not in self.build[table]:#					||
					self.getTableColumns(table)#						||
				cols = self.build[table]['columns']
				cols = self.validateColumns(cols)#						||
				self.cmdr[table] = {'columns': cols}#					||
				if how == 'SELECT':#									||
					cmd = self.bldSELECT(cols, table, cfg)#					||
				elif how == 'CRE':#										||
					cmd = self.bldCRE(cols, table, cfg)#						||
				elif how == 'INS':#										||
					cmd = self.bldINS(cols, table, cfg)#						||
				elif how == 'DROP':#									||
					cmd = self.bldDROP(cols, table, cfg)
				elif how == 'REV':#										||
					cmd = self.bldREV(cols, table, cfg)
				else:
					e = 'STORE.ORGNQL.SONQL.doc.builder'
					m = 'No Command Built'
					d = {'table': table,'columns': cols,'config': cfg}#	||
					log.WORKLOG(e,m,d,c)
				self.cmdr[table]['cmd'] = cmd
		else:#															||
			sec = '--LOG.ALERT.SQLINJECTION'
			self.bldGIVEN(gcmd.replace(';',sec), cfg)#					||
		return self
class fxSQuRILchunker(object):
	def __init__(self, gchunk=None, schunk=None, cfg=None):
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
class doc:#																||=>Define class
	'Control I/O for relational database formats'#						||=>Describe class
	version = '0.0.0.0.0.0'#											||=>Set version
	def __init__(self, doc, kind=None, params=None, cfg=None):#			||=>
		self.doc = doc#													||set doc var
		if cfg == None:#												||chk config is None
			cfg = here+'z-data_/orgnql.yaml'#							||assign default config
		self.config = config.instruct(cfg).select('sonql').dikt#		||load config
		if kind == None:#												||
			kind = exam.thing(self.doc).kind#							||
		self.kind = kind#												||
		comm.see(['SONQL Kind'])
		self._findDBType()#												||
		#this is an sqlite connection string that has been hard coded
		db = {'server': '', 'database': self.doc}#						||
		self._conx(db)#													||
	def _conx(self, db=None):#											||
		'Connect to Database'#											||
		if db != None:#													||
			server = db['server']#										||
			dbase = db['database']#										||
		if self.dbtype == 'SQLT':#										||
			try:#														||
				dpath = calct.stuff(dbase).path()
				if not dpath.valid:
					os.makedirs(dpath.it)
				self.conn = sql3.connect(dbase)#						||assign db connection
			except Exception as e:#										||
				m = ['Database connection to',dbase,'failed due to',e]#	||
				log.WORKLOG(e,m,db)#									||
				comm.see(m)#											||
		elif self.dbtype == 'MSSQL':
			server = 'ReportDevSQL'
			conn = 'DRIVER={SQL SERVER};SERVER='+server+';Trusted_Connection-yes;'
			self.conn = sql.connect(conn)
		elif self.dbtype == 'MySQL':
			server, port = '192.168.1.210', '3306'
			conn = ''
			self.conn = mysql.connect(conn)
		return self#														||
	def append(self):
		#check that table exists
		#if not create
		#if yes check columns
		#modify as nesecary for additional data addition
		#add columns to table if new data is too long
		#add columns to new data if new data is too short
		return self
	def builder(self, how='SELECT', gcmd={}, cfg=None):#				||
		'Build Query'#													||
		self.cmdr = {}#													||set sql cmd container
		self._admin()#													||get admin columns
		if gcmd == {}:#													||check for given cmd
			if self.build == {}:#										||
				self.getInfo()#											||get database info
			if self.build.keys() == {}:#								||
				self.getTables(self.build.keys())#						||
			comm.see(['Builder Needs Broken Out'])
			for table in self.build.keys():#							||
				if 'columns' not in self.build[table]:#					||
					self.getTableColumns(table)#						||
				cols = self.build[table]['columns']
				cols = self.validateColumns(cols)#						||
				#santable = calct.stuff(table).dbtablename().thing#		||
				self.cmdr[table] = {'columns': cols}#					||
				if how == 'SELECT':#									||
					cmd = self.bldSELECT(cols, table, cfg)#					||
				elif how == 'CRE':#										||
					cmd = self.bldCRE(cols, table, cfg)#						||
				elif how == 'INS':#										||
					cmd = self.bldINS(cols, table, cfg)#						||
				elif how == 'DROP':#									||
					cmd = self.bldDROP(cols, table, cfg)
				elif how == 'REV':#										||
					cmd = self.bldREV(cols, table, cfg)
				else:
					e = 'STORE.ORGNQL.SONQL.doc.builder'
					m = 'No Command Built'
					d = {'table': table,'columns': cols,'config': cfg}#	||
					log.WORKLOG(e,m,d,c)
				self.cmdr[table]['cmd'] = cmd
		else:#															||
			sec = '--LOG.ALERT.SQLINJECTION'
			self.bldGIVEN(gcmd.replace(';',sec), cfg)#					||
		return self
	def bldCRE(self, cols, table, cfg={}):
		'Build Table Creation SQL Statement'
		cmd = "CREATE TABLE IF NOT EXISTS "+table+" ("#					||
		cmd += '['+table+'Id] INTEGER '#								||
		cmd += 'PRIMARY KEY AUTOINCREMENT '#							||
		for col in cols:#												||
#			cmd += ', ['+calct.stuff(col).dbtablename().thing+']'#		||
			cmd += ', ['+col+']'
#			if 'id' in calct.stuff(col).dbtablename().thing.lower():
			if 'id' in col.lower():
				cmd += ' INTEGER \n'#								||
			else:#													||
				cmd += ' TEXT\n'#									||
		cmd += self.admincmd#										||
		return cmd
	def bldDROP(self):
		'Build Table Drop SQL Statement'
		return self
	def bldGIVEN(self, gcmd, cfg):
		''
		table = 'given'
		self.cmdr[table] = {}
		cols = self.getCmdColumns(gcmd)
		if table not in self.build.keys():
			self.build[table] = {}
		self.build[table]['columns'] = cols
#		if 'adders' in cfg.keys():
#			if cfg['adders'] != []:
#				for add in cfg['adders']:
#					gcmd += ' '+add
		self.cmdr[table]['cmd'] = gcmd
		return self
	def bldINS(self, cols, table, cfg={}):
		'Build Data Insertion SQL Statement'
		cmdvals = ''#													||
		cmd = 'INSERT INTO '+table+' ('#								||
		for col in cols+list(self.admin.keys()):
#			cmd += '['+calct.stuff(col).dbtablename().thing+'], '
			cmd += '['+col+'], '
			cmdvals += '?, '
		cmd = cmd[:-2]
		cmd += ') VALUES ('
		cmd += cmdvals[:-2]+')'
		return cmd
	def bldSELECT(self, cols, table, cfg={}):
		'Build Data Selection SQL Statement'
		cmd = 'SELECT '#												||
		for col in cols:#												||
#			cmd += '['+calct.stuff(col).dbtablename().thing+'], '#		||
			cmd += '['+col+'], '
		cmd = cmd[:-2]+' FROM '+table#									||
		if cfg != None:#												||
			if cfg['adders'] != []:#									||
				for add in cfg['adders']:#								||
########################################################################||
					if 'LIMIT' not in cmd:#major hack
########################################################################||
						cmd += ' '+add#										||
#					cfg['adders'].remove(add)
		return cmd
	def bldREV(self, cols, table, cfg={}):
		''
		self.bldSELECT()
		self.bldCRE()
		self.bldINS()
		self.execute()#create a copy of the existing table drop the existing table
		self.bldDROP()
		#need to do modifications...add columns, etc...how to determine when this is not a wanted behavior?
		self.bldCRE()
		self.bldINS()
		self.execute()#create a new table populate the new table
		return self
	def checkTable(self, tab):
		sub = {'<[table]>': table}
		cmd = self.config[self.dbtype]['cmds']['exists_table']
		cmd = rule.mechanism(cmd, sub).run().it
		if self.run(cmd).data != []:
			return True
		return False
	def checkColumns(self, cols, how='read'):
		'This would be to checkk for existence'
		return cols
	def execute(self, how='read', cfg={'fill':{}}):# cycle through cmds built to get data from various tables
		''
		for table in self.cmdr.keys():
			cmd = self.cmdr[table]['cmd']
			if how == 'read':
				self.run(cmd, cfg['fill'], how, table)# retreive data to object
			elif how == 'cre':
				self.run(cmd, None, how)
			elif how == 'write':
				self._admin()
				data, ndata = self.build[table]['records'], []
				if isinstance(data, pd.DataFrame):
					newcols = {}
					for i in range(data.shape[0]):
						for k, v in self.admin.items():
							if k in newcols.keys():
								newcols[k].append(v)
							else:
								newcols[k] = []
								newcols[k].append(v)
					ncols = self.checkColumns(list(data.columns))#this may need to call validate instead
					for k in newcols.keys():
						if k not in data.keys():
							data[k] = newcols[k]
						else:
							data[k+'0'] = newcols[k]
					ncols += newcols.keys()
					data = data.values.tolist()
				else:
					for dat in data:
						dat.extend(list(self.admin.values()))
						ndata.append(dat)
					data = ndata
				self.run(cmd, data, how)
		return self
	def getInfo(self):
		'Retreive Information about the database'
		cmd = self.config[self.dbtype]['cmds']['all_table']
		self.run(cmd, None, 'read', 'sqlite_master')
		self.dbtables = []
		for t in self.build['sqlite_master']['records']:
			self.dbtables.append(t[0])
		self.build = {}
		self.getTables(self.dbtables)
		return self
	def getTables(self, tables):
		if len(tables) > 10:
			tables = tables[:10]
		for table in tables:#limit the auto grab to 10 tables
			self.getTableColumns(table)
		return self
	def getTableColumns(self, table):#										||
		cmd = self.config[self.dbtype]['cmds']['get_columns']#				||pull sql statement from config file
		cmd = rule.mechanism(cmd, {'<[table]>': table}).run()[0]#					||fill template
		self.run(cmd, None, 'read', table)#									||run sql cmd
		self.build[table]['columns'] = []#									||
		for col in self.build[table]['records']:#							||
			self.build[table]['columns'].append(col[1])#					||
		return self#														||
	def getCmdColumns(self, cmd):#											||
		'Return the columns from a given cmd skrp'#							||
		cols, lvl = [], 1#													||
		if 'SELECT' in cmd:#												||
			bcmd = calct.stuff(cmd).trimTo('SELECT'#						||
												).trimPast('FROM').it#		||
		elif 'INSERT INTO' in cmd:#											||
			bcmd = calct.stuff(cmd).trimTo('INSERT INTO '+table+'('#		||
										).trimPast(') VALUES (').it#		||
		elif 'CREATE TABLE' in cmd:#										||
			bcmd = calct.stuff(cmd).trimTo(#								||
							'CREATE TABLE IF NOT EXISTS '+santable+' ('#	||
												).trimPast('FROM').it#		||
		else:
			comm.see(['Cmd type not found in getCmdColumns',cmd])
			lvl = 2#														||
		if lvl == 1:#														||
			for col in bcmd.split(','):#									||
				if ' as ' in col.lower():#									||
					ncol = calct.stuff(col).trimTo(' as ')#				||spaces inc'd for pattern uniqueness
				else:#														||
					ncol = calct.stuff(col).trimTo('.')#					||
				while ncol.it in cols:#										||
					ncol.rename()#											||
				ncol.it = ncol.it.strip('\n').strip(' ')#				||
				cols.append(ncol.it)#									||
		elif lvl == 2:#														||
			for col in bcmd.split(','):#									||
				if ' as ' in col.lower():#									||
					ncol = calct.stuff(col).trimTo(' as ')#				||spaces inc'd for pattern uniqueness
				else:
					ncol = calct.stuff(col).trimTo('.')
				while ncol.it in cols:
					ncol.rename()
				ncol.it = ncol.it.strip('\n').strip(' ')
				cols.append(ncol.thing)
		return cols
	def getDataColumns(self, data):
		if data != []:
			cols = data[0]
		else:
			cols = []
		return cols
	def read(self, fill=None, cfg={}, cmd={}):#						||
		'Return iterator object to pull data in chunks via offset'
		#modify generator to use seek method instead of offset method...
		#the offset method requires less knowledge about the data use this for open exploration
		if 'adders' not in cfg.keys():
			cfg['adders'] = []
		if 'page' not in cfg.keys():
			cfg['page'] = 100
		if 'fill' not in cfg.keys():
			cfg['fill'] = {}
		if cmd in list(self.config[self.dbtype]['cmds'].keys()):
			cmd = self.config[self.dbtype]['cmds'][cmd]
#		if 'cmds' not in cfg.keys():
#			cfg['cmds'] = cmd
		cfg['cmds'] = cmd
		cfg['fill']['<[limit]>'] = cfg['page']
		cfg['fill']['<[offset]>'] = 0
		if fill != None:
			for k in fill.keys():
				cfg['fill'][k] = fill[k]
		cfg['adders'].append(self.config['SQLT']['adders']['limitoffset'])
		self.build = {}
		if 'tables' in cfg.keys():
			for table in cfg['tables']:
				if table not in self.build.keys():
					self.build[table] = {}
#		comm.see(['Why is this not working'])
		self.builder('SELECT', cfg['cmds'], cfg)
		while self.build != {}:
			self.execute('read', cfg)
			cfg['fill']['<[offset]>'] += cfg['page']
			print(cfg['fill']['<[offset]>'])
			self.dikt = self.build
			self.go = True
			yield self
		self.go = False
		yield self
	def run(self, cmd, data=None, how='read', table=None):#				||
		try:
			with self.conn:
				curs = self.conn.cursor()#										||
				if how == 'read':
					if data != None:
						cmd = rule.mechanism(cmd, data).run()[0]
						comm.see(['Initiate Build'])
					if table not in self.build.keys():
						self.build[table] = {}
					try:
						e, m = 'SONQL', 'Monitor the built cmds'
						d, c = data, cmd
						log.CMDLOG(e,m,d,c)
						out = [list(row) for row in curs.execute(cmd)]
						self.build[table]['records'] = out#						||
						if out == [[]]:
							self.build = {}
						curs.close()#											||
					except Exception as e:
						self.build = {}
						m = ['records not read due to \n', str(e),#				||
														'using this cmd',cmd]#	||
						comm.see(m)
						log.FAILLOG(e,m,self.build,cmd)
				elif how == 'write':
					try:#														||
						curs.executemany(cmd, data)#							||
						self.conn.commit()#										||
						curs.close()#											||
					except Exception as e:#										||
						comm.see(['records not commited due to \n', str(e)])
						m = 'SQL Write Failed'
						#build this out through a backup data collection system
						#parse out data for reuse before/while storing log
						#use messaging system when available for both actions
						log.FAILLOG(e,m,data,cmd)
						comm.see(['Failed Cmd and Data Stored to WORKLOG'])#	||
				elif how == 'cre':
					try:
						curs.execute(cmd)#										||
						self.conn.commit()#										||
						curs.close()#											||
					except Exception as e:#										||
						m = ['Create not commited due to \n', str(e),
															'using this cmd',#	||
													cmd,'with this data',data]#	||
						comm.see(m)#								||
						log.FAILLOG(e,m,None,cmd)
		except Exception as e:
			m = ['Database Connection failed for ',self.conn,'do to ',e]
			comm.see(m)
		return self
	def validateColumns(self, cols, how='read'):
		'This is incrementing for duplicate columns'
		'need to incldue matching the input data to the database data'
		tcols = []
		if how == 'write':
			acols = [x for x in self.admin.keys()]
			if acols == cols[:len(acols)]:
				cols += acols
			cols += acols
		for col in cols:
			inc = 0
			while col.lower() in tcols:
				col = col+str(inc)
				inc += 1
			tcols.append(col)
		return tcols
	def write(self, data, ext='.sqlite', cfg=None):#							||
		self.build = data#											||{table: records}
		#write system is going to need to be extensive to allow for proper updates
		#always provide a dict that includes the table name as the top key and the
		#columns and records as subkeys
		self.builder('CRE')#									||
		self.execute('cre')#										||
		self.builder('INS')#									||
		self.execute('write')#										||
	def _admin(self):
		self.admin = {'CreBy': 0, 'CreOn': thing.when().dtid,
							'ModBy': 0, 'ModOn': thing.when().dtid,
							'DLT': 0, 'ACTV': 1}
		self.admincmd = self.config['SQLT']['adders']['admin']
		return self
	def _bldIndexes(self):
		'Add Index creation statements to the table creation also allow'
		'for future peformance upgrades by retoractively creating indexes'
		return self
	def _findDBType(self):
		if '.sqlite' or 'sqlite3' in self.doc:
			self.dbtype = 'SQLT'
		return self
#==========================Source Materials=============================||
'''
https://www.eversql.com/faster-pagination-in-mysql-why-order-by-with-limit-and-offset-is-slow/
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
