# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# Reads vespa.params to obtain Vespa preferences

import ConfigParser

class VespaConfig:
	"""
	Reads vespa.params to produce dictionaries with parameters
	
	Each parameter group reflects a key functionality:
	createParams - used for instantiating virtual clusters
	submitParams - used for deploying applications
	networkParams - used for networking
	
	The parameters that the user can/should modify are grouped in the
	section [Preferences] of the file, these parameters are then put in 
	these main groups. The miscParams holds miscellaneous parameters.

	"""

	# Singleton for VespaConfig
	vespaConfig = None

	def __init__(self, vespaFile):
		# Read all sections of configuration file
		config = ConfigParser.RawConfigParser()
		config.read(vespaFile)
		
		userPrefs = dict(config.items('Preferences'))
		self.networkParams = dict(config.items('Networking'))
		self.createParams = dict(config.items('Create'))
		self.submitParams = dict(config.items('Submit'))
		self.consolidateParams = dict(config.items('Consolidate'))
		self.miscParams = dict(config.items('Misc'))
		
		
		# put user preferences into their respective group
		self.createParams['vm_disk']  = userPrefs['vm_disk']
		self.createParams['repo_root']  = userPrefs['repo_root']
		self.createParams['default_tech_network']  = userPrefs['default_tech_network']
		self.createParams['default_tech_disk']  = userPrefs['default_tech_disk']
		self.createParams['default_infiniband']  = userPrefs['default_infiniband']
		self.createParams['vm_mem_base']  = userPrefs['vm_mem_base']
		self.createParams['vm_mem_core']  = userPrefs['vm_mem_core']
		
		self.submitParams['vespa_home']  = userPrefs['vespa_home']
		self.submitParams['exp_dir']  = userPrefs['exp_dir']
		self.submitParams['monitor_run']  = userPrefs['monitor_run']
		self.submitParams['monitor_app']  = userPrefs['monitor_app']
		self.submitParams['monitor_do_nodes']  = userPrefs['monitor_do_nodes']
		
		self.networkParams['network_source']  = userPrefs['network_source']
		self.networkParams['net_name_bridge_use']  = userPrefs['net_name_bridge_use']
		self.networkParams['net_bridge']  = userPrefs['net_bridge']
		self.networkParams['net_dev']  = userPrefs['net_dev']
		
		self.consolidateParams['consolidated_dir']  = userPrefs['consolidated_dir']
		
		self.miscParams['defined_dir'] = userPrefs['defined_dir']
		self.miscParams['general_verbose']  = userPrefs['general_verbose']
		
	def getAllParams(self):
		return (self.createParams, self.submitParams, self.networkParams,
			self.consolidateParams, self.miscParams)
		
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
