# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# Reads valpa.params to obtain VALPA preferences

import ConfigParser

class ValpaConfig:
	'''
	Reads valpa.params to produce dictionaries with options (valpaPrefs, valpaXMLOpts).
	'''

	# Singleton for ValpaConfig
	valpaConfig = None

	def __init__(self, valpaFile):
		config = ConfigParser.RawConfigParser()
		config.read(valpaFile)
		self.valpaPrefs = dict(config.items('Preferences'))
		self.valpaXMLOpts = dict(config.items('MasterXML'))
		self.runOpts = dict(config.items('Run'))
		self.networkingOpts = dict(config.items('Networking'))
		self.repoOpts = dict(config.items('Repository'))
		
	def getValpaPrefs(self):
		return self.valpaPrefs

	def getValpaXMLOpts(self):
		return self.valpaXMLOpts
	
	def getRunOpts(self):
		return self.runOpts
	
	def getNetworkingOpts(self):
		return self.networkingOpts
	
	def getRepoOpts(self):
		return self.repoOpts
	
	def getAll(self):
		return (self.valpaPrefs, self.valpaXMLOpts, self.runOpts, self.networkingOpts, self.repoOpts)

def readValpaConfig(valpaFilename):
	'''
	Reads VALPA params file and instantiates ValpaConfig object
	'''
	if ValpaConfig.valpaConfig is None:
		ValpaConfig.valpaConfig = ValpaConfig(valpaFilename)
	return ValpaConfig.valpaConfig

def allowedNetworkTypes():
	'''
	List of virtual networks allowed by VALPA.
	TODO: Read this from VALPA configuration parameters
	'''
	return ('sriov', 'external-bridge', 'libvirt-bridge')