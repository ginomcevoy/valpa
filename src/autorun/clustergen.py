'''
Created on Sep 29, 2014

@author: giacomo
'''
from bean.cluster import Topology, Mapping, ClusterPlacement, Cluster,\
    SetsTechnologyDefaults, Technology
from bean.specs import SimpleClusterPlacementSpecification
from autorun.constraint import ClusterGenerationSpecification,\
    SimpleClusterGenerationSpecification
from bean.simple import SimpleRules

#  super(ParentClass, self).__init__(superParams)
# isinstance(simpleExpConstraintInstance, ExperimentConstraint)

class ClusterRequestGenerator():
    '''
    Generates a list of virtual cluster requests using a clusterPlacementGenerator as strategy,
    and default values for VMM Settings (technology + tuning). 
    '''
    
    def __init__(self, hwSpecs, clusterPlacementGenerator, defaultTechnology, defaultTuning = None):
        self.hwSpecs = hwSpecs
        self.clusterPlacementGenerator = clusterPlacementGenerator
        self.technologyTuple = [defaultTechnology, ]
        self.tuningTuple = [defaultTuning, ]
        
    def withTechnologies(self, technologyTuple):
        '''
        Optional method to specify VMM technologies
        '''
        self.technologyTuple = technologyTuple
        return self
    
    def withTuningOptions(self, tuningTuple):
        '''
        Optional method to specify VMM tunings
        '''
        self.tuningTuple = tuningTuple
        return self
        
    def generateWithSpecification(self, generationSpec):
        '''
        Generates a list of cluster requests based on a generation specification. 
        @param generationSpec: ClusterGenerationSpecification 
        '''
        assert isinstance(generationSpec, ClusterGenerationSpecification)
        
        # delegate cluster placements
        clusterPlacements = self.clusterPlacementGenerator.generateWithSpecification(generationSpec)
        
        # create cluster requests
        clusterRequests = []
        for clusterPlacement in clusterPlacements:
            
            # virtual or physical cluster?
            physicalMachinesOnly = not clusterPlacement.isForVirtualCluster()
            
            # use provided VMM Settings
            for technology in self.technologyTuple:
                for tuning in self.tuningTuple:
                    cluster = Cluster(clusterPlacement, technology, tuning, physicalMachinesOnly)
                    clusterRequests.append(cluster)
                        
        return clusterRequests
                    
class ClusterPlacementGenerator():
    '''
    Generates a list of virtual cluster placements based on a generation specification.
    Each virtual cluster placement generated should satisfy a cluster specification.
    '''

    def __init__(self, hwSpecs, placementSpecification):
        self.hwSpecs = hwSpecs
        self.placementSpecification = placementSpecification
        
    def generateWithSpecification(self, generationSpec):
        '''
        Generates a list of cluster placements based on a specification
        @param generationSpec: ClusterGenerationSpecification 
        '''
        clusterPlacements = self.__doGeneration__(generationSpec)
        
        # each request should satisfy the cluster specification
        for clusterPlacement in clusterPlacements:
            assert clusterPlacement.isConsistentWithSpec(self.hwSpecs, self.placementSpecification)
            
        return clusterPlacements
        
    def __doGeneration__(self, generationSpec):
        '''
        Inherited classes should implement this method
        @return: list of ClusterPlacement objects.
        '''
        pass
    
class SimpleClusterGenerator(ClusterRequestGenerator):
    '''
    Generates a list of virtual cluster requests using the simple cluster
    characterization (DIST tuple). Calculates default technology from 
    Vespa configuration.
    '''
    def __init__(self, vespaPrefs, hwSpecs):
        # use the simple characterization for cluster placements
        placementSpecs = SimpleClusterPlacementSpecification(hwSpecs)
        placementGen =  SimpleClusterPlacementGenerator(hwSpecs, placementSpecs)
        
        # calculate default technology
        technologySetter = SetsTechnologyDefaults(vespaPrefs)
        defaultTechnology = technologySetter.setDefaultsOn(Technology())
        
        ClusterRequestGenerator.__init__(self, hwSpecs, placementGen, defaultTechnology)
    
class SimpleClusterPlacementGenerator(ClusterPlacementGenerator):
    '''
    Generates a list of virtual cluster placements using the simple cluster
    characterization (DIST tuple)
    '''
    
    def __init__(self, hwSpecs, clusterSpecification):
        ClusterPlacementGenerator.__init__(self, hwSpecs, clusterSpecification)
        self.simpleRules = SimpleRules(hwSpecs)
    
    def __doGeneration__(self, generationSpec):
        '''
        @param generationSpec: Should be of type
        SimpleClusterPlacementSpecification 
        '''
        assert isinstance(generationSpec, SimpleClusterGenerationSpecification)
        
        clusterPlacements = []
        
        # it will have an internalSpace with the {nc: set((cpv, idf), ...)} structure
        clusterSpace = generationSpec.internalSpace
        pstratSet = generationSpec.pstrats
        
        for nc in clusterSpace.keys():
            ncSet = sorted(list(clusterSpace[nc]))
            
            for entry in ncSet:
                # entry is a (cpv, idf) tuple
                # for each entry, create a topology
                # for each pstrat, create a mapping that fits said topology 
                cpv = entry[0]
                idf = entry[1]
                topology = Topology(nc, cpv) 
                for pinningOpt in pstratSet:
                    # a pinningOpt may not satisfy the spec
                    # for instance, using BAL_SET on single-core VMs
                    validPstrats = self.simpleRules.allPstratGiven(nc, cpv, idf)
                    if pinningOpt in validPstrats:
                        mapping = Mapping(idf, pinningOpt)
                        clusterPlacement = ClusterPlacement(topology, mapping)
                        clusterPlacements.append(clusterPlacement)
        
        return clusterPlacements