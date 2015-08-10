# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# Reads vespa.params to obtain Vespa preferences

import ConfigParser

class VespaConfig:
	'''
	Reads vespa.params to produce dictionaries with options (vespaPrefs, vespaXMLOpts).
	'''

	# Singleton for VespaConfig
	vespaConfig = None

	def __init__(self, vespaFile):
		config = ConfigParser.RawConfigParser()
		config.read(vespaFile)
		self.vespaPrefs = dict(config.items('Preferences'))
		self.vespaXMLOpts = dict(config.items('MasterXML'))
		self.runOpts = dict(config.items('Run'))
		self.networkingOpts = dict(config.items('Networking'))
		self.repoOpts = dict(config.items('Repository'))
		self.consolidatePrefs = dict(config.items('Consolidate'))
		
	def getVespaPrefs(self):
		return self.vespaPrefs

	def getVespaXMLOpts(self):
		return self.vespaXMLOpts
	
	def getRunOpts(self):
		return self.runOpts
	
	def getNetworkingOpts(self):
		return self.networkingOpts

	def getRepoOpts(self):
		return self.repoOpts
	
	def getConsolidatePrefs(self):
		return self.consolidatePrefs
	
	def getAll(self):
		return (self.vespaPrefs, self.vespaXMLOpts, self.runOpts, self.networkingOpts, self.repoOpts)

def readVespaConfig(vespaFilename):
	'''
	Reads VESPA params file and instantiates VespaConfig object
	'''
	if VespaConfig.vespaConfig is None:
		VespaConfig.vespaConfig = VespaConfig(vespaFilename)
	return VespaConfig.vespaConfig

def allowedNetworkTypes():
	'''
	List of virtual networks allowed by Vespa.
	'''
	return ('sriov', 'external-bridge', 'libvirt-bridge')
