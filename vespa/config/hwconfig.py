# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

#import pprint
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

def getHardwareInfo(specsFile='../input/hardware.params', inventoryFilename='../input/vespa.nodes'):
	'''
	Reads hardware info from specsFile (default: input/hardware.params)
	and node identities from inventoryFile (default: input/vespa.nodes)
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