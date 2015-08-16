# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# Mapping Resolver component
from core.virtual import VirtualClusterFactory

class MappingResolver:
	'''
	Uses HardwareInfo from physical cluster and Topology/PhysicalMappings from
	virtual cluster to generate node ids, VM ids and sockets that will 
	be used to deploy virtual cluster.
	'''

	def __init__(self, hwSpecs, allNodes, allVMDetails):
		self.hwSpecs = hwSpecs
		self.allNodes = allNodes
		self.allVMDetails = allVMDetails

	def processMappings(self, clusterRequest):
		'''
		Call this with a virtual cluster definition
		'''
		self.mapping = clusterRequest.mapping
		self.topology = clusterRequest.topology
		
		# try to read from definition
		deployNodeNames = self.mapping.deployNodes
		
		if (deployNodeNames is None):
			# infer deployNodes
			deployNodeCount = self.__obtainDeployNodeCount__()
			firstNodeIndex = self.mapping.firstNodeIndex
			deployNodeNames = self.allNodes.nodeNames[firstNodeIndex:(deployNodeCount+firstNodeIndex)]
			deployNodeNames = tuple(deployNodeNames)
		
		self.deployedNodes = self.allNodes.getSubset(deployNodeNames)
		
	def getDeployedNodes(self):
		'''
		Returns physical nodes as PhysicalCluster object, either read from 
		virtual cluster definition or inferred from specs and prefs. 
		TODO: add support for initial node
		'''
		return self.deployedNodes
		
	def getDeployedSockets(self):
		'''
		Returns physical sockets, either read from virtual cluster definition
		or inferred from specs and prefs
		'''
		# TODO: use VMDetails + VirtualClusterFactory
		
		# try to read from definition
		deploySockets = None
		if self.mapping is not None:
			deploySockets = self.mapping.deploySockets

		if (deploySockets is None):
			# infer deploySockets
			deploySockets = []
			socketIndex = 0
			while socketIndex < self.hwSpecs['sockets']:
				deploySockets.append(socketIndex)
				socketIndex += 1

			deploySockets = tuple(deploySockets)

		return deploySockets
	
	def getDeployedVMs(self):
		'''
		Returns VMs for cluster as VirtualClusterTemplates object, using 
		VespaPreferences and virtual cluster request. The number of VMs
		and the number of VMs per host are obtained from cluster definition.
		'''
		vmCount = int(self.topology.nc / self.topology.cpv)
		if self.mapping.idf == 0:
			vmsPerHost = vmCount
		else:
			vmsPerHost = int(self.mapping.idf / self.topology.cpv)
		
		clusterVMs = []
		
		# get VM names that should correspond to cluster request
		for node in self.deployedNodes:
			allVMsForNode = self.allVMDetails.getVMNamesForNode(node)
			# current policy: select the first vms up to vmsPerHost
			vmsForNode = allVMsForNode[0:vmsPerHost]
			clusterVMs.extend(vmsForNode)
			
		# use the factory to build the VM templates
		vmTemplateFactory = VirtualClusterFactory(self.allVMDetails)
		deployedVMs = vmTemplateFactory.create(clusterVMs, self.topology.cpv)
		return deployedVMs
		
	def __obtainDeployNodeCount__(self):
		if self.mapping.idf == 0:
			deployNodeCount = 1
		else:
			deployNodeCount = self.topology.nc / self.mapping.idf 
			deployNodeCount = int(deployNodeCount)
		return deployNodeCount
