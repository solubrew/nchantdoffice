








class NTDConcernTabSet(tabsets.NchantdTabSet):
	""""""
	def __init__(self):
		""""""

class NTDHistoryTabSet(tabsets.NchantdTabSet):
	""""""
	def __init__(self):
		""""""


class NTDTimeLineTabSet(tabsets.NchantdTabSet):
	""""""
	def __init__(self):
		""""""




class NTDAddObjectsTabSet(tabsets.NchantdTabSet):
	""" """
	def __init__(self, parent=None, cfg={}):
		""" """
		self.parent = parent
		self.config = condor.instruct(pxcfg).select('NMBTabSet')
		self.config.override(cfg)
		if parent:
			self.config.override(parent.config)
		super(NTDAddObjectsTabSet, self).__init__(parent, self.config)














