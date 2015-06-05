# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

#import pprint
import configparser

class HardwareInfo:
	'''
	Holds hardware info
	'''

	# Singleton variable
	hwInfo = None

	def __init__(self, hwDict, nodeDict):
		# save dicts
		self.hwDict = hwDict
		self.nodeDict = nodeDict
		
		# hardware
		cores = int(hwDict['cores'])
		sockets = int(hwDict['sockets'])
		mem = int(hwDict['mem'])
		
		# derived harware specs
		coresPerSocket = int(cores / sockets)
		coresInCluster = int(nodeDict['nodes']) * cores
		
		# all specs
		self.specs = {'cores' : cores, 
					'sockets' : sockets, 
					'coresPerSocket' : coresPerSocket,
					'coresInCluster' : coresInCluster, 
					'mem' : mem,
					'nodes' : int(nodeDict['nodes'])}

		# nodes
		#pprint.pprint(nodeDict)
		self.nodeCount = int(nodeDict['nodes'])
		if (nodeDict['inferids'] == 'True'):
			self.nodePrefix = nodeDict['prefix']
			self.nodeZeros = int(nodeDict['zeros'])
			self.nodeFirst = int(nodeDict['first'])

			# lazy load of node list
			self.allNodes = None

	def getHwAndNodeDicts(self):
		return (self.specs, self.nodeDict)

	def getHwSpecs(self):
		'''
		Returns hardware specs as a dict.
		'''
		return dict(self.specs)

def getHardwareInfo(filename='../input/hardware.params'):
	'''
	Reads hardware info from param file
	(default: input/hardware.params)
	'''
	# Singleton
	if HardwareInfo.hwInfo is None:
		config = configparser.RawConfigParser()
		config.read(filename)
		hwDict = dict(config.items('Hardware'))
		nodeDict = dict(config.items('Nodes'))
		HardwareInfo.hwInfo = HardwareInfo(hwDict, nodeDict)

	return HardwareInfo.hwInfo