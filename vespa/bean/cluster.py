from bean.enum import CpuTopoOpt, NetworkOpt, DiskOpt, PinningOpt
from bean.specs import SimpleClusterPlacementSpecification,\
	SimpleTopologySpecification, SimpleMappingSpecification

class Cluster:

	def __init__(self, clusterPlacement, technology=None, tuning=None, physicalMachinesOnly=False):
		
		if physicalMachinesOnly:
			# physical cluster has no mappings, use idf=-1 to refer to PC
			clusterPlacement.mapping = Mapping(-1, PinningOpt.NONE)
			technology = getEmptyTechnology()
		else:
			self.tuning = tuning
			if technology is None:
				technology = getDefaultTechnology()
		
		self.clusterPlacement = clusterPlacement
		self.topology = clusterPlacement.topology
		self.mapping = clusterPlacement.mapping
		self.physicalMachinesOnly = physicalMachinesOnly
		self.technology = technology
	
	def isConsistentWith(self, hwSpecs):
		'''
		Returns True iff cluster is correctly defined
		Validates the following:
		1) valid clusterPlacement (see ClusterPlacement class)
		2) technology with valid options
		'''
		validClusterPlacement = self.clusterPlacement.isConsistentWith(hwSpecs)
		
		if self.physicalMachinesOnly:
			# physical cluster has no technology definition
			validTechnology = True
		else:
			validTechnology = self.technology.isValid()
		
		return validClusterPlacement and validTechnology

	def __str__(self):
		result = str(self.topology) + "-" + str(self.mapping)
		if not self.technology.isDefault():
			result = result + "-" + str(self.technology) 
		if self.tuning is not None:
			result = result + "-"  + str(self.tuning)
		return result

class ClusterPlacement:
	
	def __init__(self, topology, mapping):
		self.topology = topology
		self.mapping = mapping
			
	def isConsistentWith(self, hwSpecs):
		'''
		Validates consistency of cluster placement against available 
		physical cluster topology. For virtual clusters, uses simple specification.
		For physical clusters, verifies machine count.
		'''
		if self.isForVirtualCluster():
			# use simple specification
			simplePlacementSpec = SimpleClusterPlacementSpecification(hwSpecs)
			return self.isConsistentWithSpec(hwSpecs, simplePlacementSpec)
		else:
			# just count physical machines
			return self.canBeDeployedWithin(hwSpecs['nodes'])
	
	def isConsistentWithSpec(self, hwSpecs, clusterSpecification):
		return clusterSpecification.isSatisfiedBy(self.topology, self.mapping)
	
	def canBeDeployedWithin(self, physicalMachineCount):
		'''
		Returns True iff the virtual cluster can be deployed in the number of
		physical nodes specified. To evaluate this, the number of virtual cores
		and the spreading are considered. 
		@raise ValueError: If physicalMachineCount is not positive integer
		'''
		if type(physicalMachineCount) != type(1) or physicalMachineCount < 1:
			raise ValueError("cannot use physicalMachineCount: ", physicalMachineCount)

		# special case of single PM
		if self.mapping.idf == 0:
			return True
		
		if self.mapping.idf > 0:
			requiredPhysicalMachines = self.topology.nc / self.mapping.idf
		else:
			# physical cluster (idf = -1)
			requiredPhysicalMachines = self.topology.nc / self.topology.cpv
		
		return requiredPhysicalMachines <= physicalMachineCount
	
	def isForVirtualCluster(self):
		'''
		Returns True if the placement is for a virtual cluster, False if it is
		a physical cluster (sub-cluster)
		'''
		return self.mapping.idf != -1

class Topology:

	def __init__(self, nc, cpv):
		self.nc = nc
		self.cpv = cpv
	
	def isConsistentWith(self, hwSpecs):
		'''
		Validates consistency of virtual cluster topology with
		physical cluster topology, uses simple specification
		'''
		topologySpec = SimpleTopologySpecification(hwSpecs)
		return topologySpec.isSatisfiedBy(self)
	
	def canBeMappedWith(self, mapping, hwSpecs):
		clusterPlacementSpec = SimpleClusterPlacementSpecification(hwSpecs)
		return clusterPlacementSpec.isSatisfiedBy(self, mapping)
		
	def __str__(self):
		return "nc" + str(self.nc) + "-cpv" + str(self.cpv)

class Mapping:

	def __init__(self, idf, pinningOpt, deployNodes=None, deploySockets=None):
		self.idf = idf
		self.pinningOpt = pinningOpt
		self.deployNodes = deployNodes # default value: first deployNodes
		self.deploySockets = deploySockets # default value: all sockets
	
	def isConsistentWith(self, hwSpecs):
		'''
		Validates consistency of virtual cluster mapping with
		physical cluster, uses simple specification
		'''
		mappingSpec = SimpleMappingSpecification(hwSpecs)
		return mappingSpec.isSatisfiedBy(self)
	
	def canAccommodate(self, topology, hwSpecs):
		clusterPlacementSpec = SimpleClusterPlacementSpecification(hwSpecs)
		return clusterPlacementSpec.isSatisfiedBy(topology, self)

	def __str__(self):
		return "idf" + str(self.idf) + "-ps" + str(self.pinningOpt)

class Technology:

	def __init__(self, networkOpt, diskOpt):
		self.networkOpt = networkOpt
		self.diskOpt = diskOpt
		
	def isValid(self):
		validNetwork = NetworkOpt.__contains__(self.networkOpt)
		validDisk = DiskOpt.__contains__(self.diskOpt)
		return validNetwork and validDisk
	
	def isDefault(self):
		defaultTech = getDefaultTechnology()
		return self.networkOpt == defaultTech.networkOpt and self.diskOpt == defaultTech.diskOpt

	def __str__(self):
		return "disk" + str(self.diskOpt) + "-net" + str(self.networkOpt)

def getDefaultTechnology():
	'''
	To be used when cluster does not specify technology values.
	TODO: Make this configurable
	TODO: if Vespa is using sriov, use sriov by default
	'''
	return Technology(NetworkOpt.vhost, DiskOpt.virtio)

def getEmptyTechnology():
	'''
	To be used for deployments on physical cluster (technology is
	inapplicable).
	'''
	return Technology(networkOpt=None, diskOpt=None)

class Tuning:
	
	def __init__(self):
		self.cpuTopoOpt = CpuTopoOpt.DEFAULT
		self.hugepages = False
		self.guestNuma = False
		self.numaTune = False
		self.ballooning = False

	def __str__(self):
		return "cpuTopoOpt = " + str(self.cpuTopoOpt) + ", hugepages = " + str(self.hugepages)
	