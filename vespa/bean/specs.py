'''
Created on Sep 29, 2014

@author: giacomo
'''
from bean.simple import SimpleRules

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
        
        validIdf = self.simpleRules.isIdfPermitted(idf)
        validPstrat = self.simpleRules.isPstratPermitted(pstrat) 
        return validIdf and validPstrat
           
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
        
        # now check if the combined parts can produce a feasible virtual cluster
        nc = topologyRequest.nc
        cpv = topologyRequest.cpv
        idf = mappingRequest.idf
        pstrat = mappingRequest.pinningOpt
        
        validIdfs = self.simpleRules.allIdfGiven(nc, cpv)
        validPstrats = self.simpleRules.allPstratGiven(nc, cpv, idf)
        
        idfOk = idf in validIdfs
        pstratOk = pstrat in validPstrats
        return idfOk and pstratOk     
