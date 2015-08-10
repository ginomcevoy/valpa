'''
Created on Sep 29, 2014

@author: giacomo
'''
from .simple_rules import SimpleRules

class ClusterPlacementSpecification():
    '''
    Establishes if the virtual cluster placement (topo+mapping) is feasible
    under some constraints.
    '''
    
    def __init__(self, hwSpecs):
        self.hwSpecs = hwSpecs
        
    def isSatisfiedBy(self, topologyRequest, mappingRequest):
        '''
        Returns True iff a virtual cluster request (topology+mapping) satisfies
        this specification. 
        '''
        pass
    
class SimpleTopologySpecification():
    '''
    Establishes if the virtual topology is feasible under the constraints
    of the Simple characterization (DIST), using the SimpleRules as a basis
    for validating a virtual cluster.
    '''
    def __init__(self, hwSpecs):
        self.hwSpecs = hwSpecs
        self.simpleRules = SimpleRules(hwSpecs)
        
    def isSatisfiedBy(self, topologyRequest):
        '''
        Returns True iff a topology request satisifies
        this specification. Assumes the DIST representation.
        '''        
        nc = topologyRequest.nc
        cpv = topologyRequest.cpv
        
        cpvs = self.simpleRules.allCpvGivenNc(nc)
        return cpv in cpvs
    
class SimpleMappingSpecification():
    '''
    Establishes if the virtual mapping is feasible under the constraints
    of the Simple characterization (DIST), using the SimpleRules as a basis
    for validating a virtual cluster.
    '''
    def __init__(self, hwSpecs):
        self.hwSpecs = hwSpecs
        self.simpleRules = SimpleRules(hwSpecs)
        
    def isSatisfiedBy(self, mappingRequest):
        '''
        Returns True iff a mapping request satisifies
        this specification. Assumes the DIST representation.
        '''
        idf = mappingRequest.idf
        pstrat = mappingRequest.pinningOpt
        firstNodeIndex = mappingRequest.firstNodeIndex
        
        valid1 = self.simpleRules.isIdfPermitted(idf)
        valid2 = self.simpleRules.isPstratPermitted(pstrat) 
        valid3 = self.simpleRules.isFirstNodeIndexPermitted(firstNodeIndex)
        return valid1 and valid2 and valid3
           
class SimpleClusterPlacementSpecification(ClusterPlacementSpecification):
    '''
    Establishes if the virtual cluster placement (topo+mapping) is feasible
    under the constraints of the Simple characterization (DIST), using the 
    SimpleRules as a basis for validating a virtual cluster.
    '''
    
    def __init__(self, hwSpecs):
        #super(ClusterPlacementSpecification, self).__init__(hwSpecs)
        ClusterPlacementSpecification.__init__(self, hwSpecs)
        self.hwSpecs = hwSpecs
        self.simpleRules = SimpleRules(hwSpecs)
        self.topologySpec = SimpleTopologySpecification(hwSpecs)
        self.mappingSpec = SimpleMappingSpecification(hwSpecs)
        
    def isSatisfiedBy(self, topologyRequest, mappingRequest):
        '''
        Returns True iff a virtual cluster request (topology+mapping) satisifies
        this specification. Assumes the DIST representation.
        '''
        
        # check if the parts each satisfy their specifications
        validTopology = self.topologySpec.isSatisfiedBy(topologyRequest)
        validMapping = self.mappingSpec.isSatisfiedBy(mappingRequest)
        
        if (not validTopology) or (not validMapping):
            return False  
        
        # check if the combined parts can produce a feasible virtual cluster
        nc = topologyRequest.nc
        cpv = topologyRequest.cpv
        idf = mappingRequest.idf
        pstrat = mappingRequest.pinningOpt
        firstNodeIndex = mappingRequest.firstNodeIndex
        
        validIdfs = self.simpleRules.allIdfGiven(nc, cpv)
        idfOk = idf in validIdfs
        
        validPstrats = self.simpleRules.allPstratGiven(nc, cpv, idf)
        pstratOk = pstrat in validPstrats
        
        # The virtual cluster must fit in the physical cluster, this can fail
        # if firstNodeIndex is too large.  
        remainingNodes = self.hwSpecs['nodes'] - firstNodeIndex 
        requiredNodes = self.simpleRules.mappedPhysicalNodes(nc, idf)
        indexOk = remainingNodes >= requiredNodes
        
        return idfOk and pstratOk and indexOk     
