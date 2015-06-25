# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# Reads vespa.params to obtain VESPA preferences

import ConfigParser
from quik import FileLoader
#import pprint

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
		
	def getVespaPrefs(self):
		return self.vespaPrefs

	def getVespaXMLOpts(self):
		return self.vespaXMLOpts
	
	def getRunOpts(self):
		return self.runOpts
	
	def getNetworkingOpts(self):
		return self.networkingOpts
	
	def getAll(self):
		return (self.vespaPrefs, self.vespaXMLOpts, self.runOpts, self.networkingOpts)

def readVespaConfig(vespaFilename):
	'''
	Reads VESPA params file and instantiates VespaConfig object
	'''
	if VespaConfig.vespaConfig is None:
		VespaConfig.vespaConfig = VespaConfig(vespaFilename)
	return VespaConfig.vespaConfig

def produceVespaXML(vespaXMLOpts, networkingOpts, masterXML):
	'''
	Produces VESPA XML for cluster XML generation, based on a master XML and preferences.
	Returns the text of the xml.
	'''

	# choose network name from selected type 
	# types: ('sriov', 'use-bridge', 'create-bridge')
	networkType = networkingOpts['network_source']
	if not networkType in allowedNetworkTypes():
		print('Allowed values = ' + str(allowedNetworkTypes()))
		raise ValueError('Network type not allowed: ', networkType)
	
	if networkType == 'external-bridge':
		networkName = networkingOpts['net_name_bridge_use']
	elif networkType == 'libvirt-bridge':
		networkName = networkingOpts['net_name_bridge_create']
	else: #networkType == 'sriov'
		networkName = networkingOpts['net_name_sriov']
	
	# Prepare arguments for substitution with quik
	args = {'network_name' : networkName,
			'vespa_disk_type' : vespaXMLOpts['xml_disk_drivertype'],
			'vespa_path' : vespaXMLOpts['xml_disk_path'],
			'vespa_disk_file' : vespaXMLOpts['xml_disk_file'],
			'vespa_disk_dev' : vespaXMLOpts['xml_disk_dev'],
		}
	
	# apply quik
	loader = FileLoader('.')
	template = loader.load_template(masterXML)
	vespaXML = template.render(args, loader=loader)
	
	# Read master xml
	#xmlText = open(masterXML, 'r').read()
	
	# Make substitutions in text object
	#xmlText = xmlText.replace('_NET_VALUE', vespaXMLOpts['xml_network_value'])
	#xmlText = xmlText.replace('_DISK_DRIVER_TYPE', vespaXMLOpts['xml_disk_drivertype'])
	#xmlText = xmlText.replace('_VESPAPATH', vespaXMLOpts['xml_disk_path'])
	#xmlText = xmlText.replace('_DISKFILE', vespaXMLOpts['xml_disk_file'])
	#xmlText = xmlText.replace('_DISK_DEV', vespaXMLOpts['xml_disk_dev'])
	
	vespaXML = vespaXML.replace('_VESPA_POUND_', '#')
	
	return vespaXML

def allowedNetworkTypes():
	'''
	List of virtual networks allowed by Vespa.
	'''
	return ('sriov', 'external-bridge', 'libvirt-bridge')