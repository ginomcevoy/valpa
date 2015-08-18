# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

import ConfigParser

class HardwareInfo:
	'''
	Holds hardware info
	'''

	# Singleton variable
	hwInfo = None

	def __init__(self, hwDict, nodeNames):
		# save dicts
		self.hwDict = hwDict
		self.nodeNames = nodeNames
		self.nodeCount = len(nodeNames)
		
		# hardware
		cores = int(hwDict['cores'])
		sockets = int(hwDict['sockets'])
		mem = int(hwDict['mem'])
		
		# derived harware specs
		coresPerSocket = int(cores / sockets)
		coresInCluster = self.nodeCount * cores
		
		# all specs
		self.specs = {'cores' : cores, 
					'sockets' : sockets, 
					'coresPerSocket' : coresPerSocket,
					'coresInCluster' : coresInCluster, 
					'mem' : mem,
					'ib_bus' : hwDict['ib_bus'],
					'ib_slot_start' : hwDict['ib_slot_start'],
				 	'ib_device_start' : hwDict['ib_device_start'],
					'ib_vfs' : hwDict['ib_vfs'],
					'nodes' : self.nodeCount}

	def getHwSpecs(self):
		'''
		Returns hardware specs as a dict.
		'''
		return dict(self.specs)
	
	def getNodeNames(self):
		return self.nodeNames
	
def readInventoryFile(inventoryFilename):
	'''
	Reads Vespa main inventory file and returns a list of hostnames of
	the physical nodes.
	'''
	nodeNames = []
	for line in open(inventoryFilename, 'r'):
		li = line.strip()
		
		# ignore lines with comments
		if not li.startswith("#"):
			nodeName = line.rstrip()
			nodeNames.append(nodeName)
	return tuple(nodeNames)

def getHardwareInfo(specsFile='../config/hardware.params', inventoryFilename='../config/vespa.nodes'):
	'''
	Reads hardware info from specsFile (default: config/hardware.params)
	and node identities from inventoryFile (default: config/vespa.nodes)
	'''
	# Singleton
	if HardwareInfo.hwInfo is None:
		
		# read specs
		config = ConfigParser.RawConfigParser()
		config.read(specsFile)
		hwDict = dict(config.items('Hardware'))
		
		# read inventory
		nodeNames = readInventoryFile(inventoryFilename)
		
		# initialize singleton
		HardwareInfo.hwInfo = HardwareInfo(hwDict, nodeNames)

	return HardwareInfo.hwInfo
