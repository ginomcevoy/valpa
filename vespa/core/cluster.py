"""This module contains the main entity classes that describe virtual clusters.

The ClusterRequest class contains all the necessary information to describe a
virtual cluster (Virtual Cluster Characterization). It is composed of the 
ClusterPlacement, Technology and Tuning instances.

A ClusterPlacement describes unambiguously how the virtual cores of the VMs 
are mapped to the physical cores. It is composed by the Topology and Mapping. 

The Topology describes the definition of the VMs, in amount and size. The 
Mapping describes how these VMs are mapped to physical machines. Both are
expressed using the simplified characterization (nc, cpv, idf, pstrat).

"""

from .enum import CpuTopoOpt, NetworkOpt, DiskOpt, PinningOpt
from core.simple_specs import SimpleClusterPlacementSpecification,\
    SimpleTopologySpecification, SimpleMappingSpecification

class ClusterRequest:
    """Represents an instance of a complete Virtual Cluster Characterization
    
    The ClusterRequest class contains all the necessary information to describe
    a virtual cluster (Virtual Cluster Characterization). It is composed of 
    ClusterPlacement, Technology and Tuning instances.
    
    Parameters
    ----------
    clusterPlacement : `ClusterPlacement`
    technology : `Technology`, optional
    tuning : `Tuning`, optional
    physicalMachinsOnly : bool (default is False)
            if False then deploy a virtual cluster, else use physical nodes 
    
    """


    def __init__(self, clusterPlacement, technology=None, tuning=None, physicalMachinesOnly=False):
        
        if physicalMachinesOnly:
            # physical cluster has no mappings, use idf=-1 to refer to PC
            clusterPlacement.mapping = Mapping(-1, PinningOpt.NONE)
        else:
            self.tuning = tuning
            if technology is None:
                technology = Technology()
        
        self.clusterPlacement = clusterPlacement
        self.topology = clusterPlacement.topology
        self.mapping = clusterPlacement.mapping
        self.physicalMachinesOnly = physicalMachinesOnly
        self.technology = technology
    
    def isConsistentWith(self, hwSpecs):
        """Return True iff cluster is correctly defined.
        
        Validates the following:
        1) valid clusterPlacement (see ClusterPlacement class)
        2) technology with valid options
        
        Parameters
        ----------
        hwSpecs: dict
        Hardware specifications created by HardwareInfo.
    
        """
        validClusterPlacement = self.clusterPlacement.isConsistentWith(hwSpecs)
        
        if self.physicalMachinesOnly:
            # physical cluster has no technology definition
            validTechnology = True
        else:
            validTechnology = self.technology.isValid()
        
        return validClusterPlacement and validTechnology

    def __str__(self):
        result = str(self.topology) + "-" + str(self.mapping)
        if not self.technology.isEmpty():
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

    def __init__(self, idf, pinningOpt, firstNodeIndex=None, deployNodes=None, deploySockets=None):
        self.idf = idf
        self.pinningOpt = pinningOpt
        self.deployNodes = deployNodes # default value: first deployNodes
        self.deploySockets = deploySockets # default value: all sockets
        
        # mapping will start at first node if unspecified
        if firstNodeIndex is None:
            firstNodeIndex = 0
        self.firstNodeIndex = firstNodeIndex
    
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

    def __init__(self, networkOpt=None, diskOpt=None, infinibandFlag=None):
        self.networkOpt = networkOpt
        self.diskOpt = diskOpt
        self.infinibandFlag = infinibandFlag
        
    def isValid(self):
        validNetwork = NetworkOpt.__contains__(self.networkOpt)
        validDisk = DiskOpt.__contains__(self.diskOpt)
        validInfiniband = type(self.infinibandFlag) == type(True) 
        return validNetwork and validDisk and validInfiniband
    
    def isEmpty(self):
        return self.networkOpt is None and self.diskOpt is None and self.infinibandFlag is None
    
    def __str__(self):
        if self.isEmpty():
            return ''
        infinibandText = 'openIB' if self.infinibandFlag else 'eth'
        return str(self.diskOpt) + "-" + str(self.networkOpt) + "-" + infinibandText  

class Tuning:
    
    def __init__(self):
        self.cpuTopoOpt = CpuTopoOpt.DEFAULT
        self.hugepages = False
        self.guestNuma = False
        self.numaTune = False
        self.ballooning = False

    def __str__(self):
        return "cpuTopoOpt = " + str(self.cpuTopoOpt) + ", hugepages = " + str(self.hugepages)
    
    
class SetsTechnologyDefaults:
    """Sets any unset technolgoy variable with Vespa defaults.
    
    The default values for virtual cluster Technology are read
    from Vespa configuration, and are set for any unset parameters. If the
    experiment has specified a parameter for the cluster, it is not 
    overridden with the default values.
    """
    
    def __init__(self, vespaPrefs):
        self.vespaPrefs = vespaPrefs
        
    def setDefaultsOn(self, technology):
        
        # check for any parameters that are not overridden in experiment
        # if parameter is not set, use parameter from preferences
        if technology.networkOpt is None:
            defaultNetworkOpt = self.vespaPrefs['default_tech_network']
            technology.networkOpt = eval('NetworkOpt.' + defaultNetworkOpt)
        if technology.diskOpt is None:
            defaultDiskOpt = self.vespaPrefs['default_tech_disk']
            technology.diskOpt = eval('DiskOpt.' + defaultDiskOpt)
        if technology.infinibandFlag is None:
            defaultInfinibandFlag = self.vespaPrefs['default_infiniband'] == 'True'
            technology.infinibandFlag = defaultInfinibandFlag
            
        return technology
    
