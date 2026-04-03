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
