# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# Reads valpa.params to obtain VALPA preferences

import configparser
from quik import FileLoader
#import pprint

class ValpaConfig:
	'''
	Reads valpa.params to produce dictionaries with options (valpaPrefs, valpaXMLOpts).
	'''

	# Singleton for ValpaConfig
	valpaConfig = None

	def __init__(self, valpaFile):
		config = configparser.RawConfigParser()
		config.read(valpaFile)
		self.valpaPrefs = dict(config.items('Preferences'))
		self.valpaXMLOpts = dict(config.items('MasterXML'))
		self.runOpts = dict(config.items('Run'))
		self.networkingOpts = dict(config.items('Networking'))
		
	def getValpaPrefs(self):
		return self.valpaPrefs

	def getValpaXMLOpts(self):
		return self.valpaXMLOpts
	
	def getRunOpts(self):
		return self.runOpts
	
	def getNetworkingOpts(self):
		return self.networkingOpts
	
	def getAll(self):
		return (self.valpaPrefs, self.valpaXMLOpts, self.runOpts, self.networkingOpts)

def readValpaConfig(valpaFilename):
	'''
	Reads VALPA params file and instantiates ValpaConfig object
	'''
	if ValpaConfig.valpaConfig is None:
		ValpaConfig.valpaConfig = ValpaConfig(valpaFilename)
	return ValpaConfig.valpaConfig

def produceValpaXML(valpaXMLOpts, networkingOpts, masterXML):
	'''
	Produces VALPA XML for cluster XML generation, based on a master XML and preferences.
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
			'valpa_disk_type' : valpaXMLOpts['xml_disk_drivertype'],
			'valpa_path' : valpaXMLOpts['xml_disk_path'],
			'valpa_disk_file' : valpaXMLOpts['xml_disk_file'],
			'valpa_disk_dev' : valpaXMLOpts['xml_disk_dev'],
		}
	
	# apply quik
	loader = FileLoader('.')
	template = loader.load_template(masterXML)
	valpaXML = template.render(args, loader=loader)
	
	# Read master xml
	#xmlText = open(masterXML, 'r').read()
	
	# Make substitutions in text object
	#xmlText = xmlText.replace('_NET_VALUE', valpaXMLOpts['xml_network_value'])
	#xmlText = xmlText.replace('_DISK_DRIVER_TYPE', valpaXMLOpts['xml_disk_drivertype'])
	#xmlText = xmlText.replace('_VALPAPATH', valpaXMLOpts['xml_disk_path'])
	#xmlText = xmlText.replace('_DISKFILE', valpaXMLOpts['xml_disk_file'])
	#xmlText = xmlText.replace('_DISK_DEV', valpaXMLOpts['xml_disk_dev'])
	
	valpaXML = valpaXML.replace('_VALPA_POUND_', '#')
	
	return valpaXML

def allowedNetworkTypes():
	'''
	List of virtual networks allowed by VALPA.
	'''
	return ('sriov', 'external-bridge', 'libvirt-bridge')