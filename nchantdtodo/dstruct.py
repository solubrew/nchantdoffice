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
# -*- coding: utf-8 -*
# ======================================Standard Library Modules======================================================||
from os.path import abspath, dirname, join

# ======================================3rd Party Library Modules=====================================================||

# ======================================Solutions Brewer Library Modules==============================================||
from condor import condor
from ogma.logma import Logma

# ====================================================================================================================||
here = join(dirname(__file__), '')  # ||
logma = Logma(__name__)

# ====================================================================================================================||
pxcfg = join(here, '_data_', '.yaml')
def setupNodes():
	""""""

def setupTabs():
	""""""


	tabs_df = qpandas.DataFrame(tabs, columns=self.tabcolumns)
	data = next(self.src.docs['db'].read({'table': ['tabs']})).dikt
	db_tabs_df = qpandas.DataFrame(data['tabs']['records'], columns=data['tabs']['columns'])
	tabs_df['uuid'] = tabs_df['name'].apply(lambda x: uuid.UUID(str(uuid.uuid4())).hex)
	if log: logma.info(f"Columns {tabs_df.columns}")
	if log: logma.info(f"Tabs DF\n{tabs_df}")
	if log: logma.info(f"Tabs DF\n{db_tabs_df}")
	# TODO: this needs to be name and parent
	tabs_df = tabs_df[~tabs_df['name'].isin(db_tabs_df['name'].values.tolist())]
	
	# TODO: This should be a function of a base model in nchantrs and check against already stored tabs
	if not tabs_df.empty:
		self.src.docs['db'].write({'tabs': tabs_df})
	
def genTreeNodes(self):
	
	data = next(self.src.docs['db'].read({'table': ['trnodes', 'tabs']})).dikt
	trnodes_df = qpandas.DataFrame(data['trnodes']['records'], columns=data['trnodes']['columns'])
	if log: logma.info(f"DATA {data}")
	icon = ''
	nodes = [
		['1', icon, 'Action', 'appnode', 0, 0, 'NTDActionTabSet'] + self.nodebase + [
			uuid.UUID(str(uuid.uuid4())).hex],
		['2', icon, 'Concern', 'appnode', 0, 1, 'NTDConcernTabSet'] + self.nodebase + [
			uuid.UUID(str(uuid.uuid4())).hex],
		['3', icon, 'Timeline', 'appnode', 0, 2, 'NTDHistoryTabSet'] + self.nodebase + [
			uuid.UUID(str(uuid.uuid4())).hex]
	]
	if log: logma.info(f'SRC {self.src}')
	logma.info(f"Columns {self.nodecolumns}")
	df = qpandas.DataFrame(nodes, columns=self.nodecolumns)
	if log: logma.info(f"TRNODES_DF {trnodes_df}")
	df = df[~df['nid'].isin(trnodes_df['nid'].values.tolist())]
	df['uuid'] = df['nid'].apply(lambda x: uuid.UUID(str(uuid.uuid4())).hex)  # TODO: upgrade to 7 or 8
	df.reset_index(inplace=True, drop=True)
	if log: logma.info(f"DF {df}")
	if not df.empty:
		self.src.docs['db'].write({'trnodes': df})
	# TODO: need to create a node for today and then transfer information to the timeline node for that date
	nid = NchantdTreeGenerator(self, trnodes_df).genYearMonthTreeData(self.src, 0, 3, 4)
	self.setToday(nid)
	return self


# ====================================================================================================================||

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@||