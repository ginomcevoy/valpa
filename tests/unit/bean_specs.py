'''
Created on Jul 11, 2015

@author: giacomo
'''

import unittest

from unit.test_abstract import VespaAbstractTest
from bean.specs import SimpleTopologySpecification, SimpleMappingSpecification,\
    SimpleClusterPlacementSpecification
from bean.cluster import Topology, Mapping
from bean.enum import PinningOpt


class SimpleTopologySpecificationTest(VespaAbstractTest):
    """Unit unit for bean.specs.SimpleTopologySpecification. """
    
    def setUp(self):
        super(SimpleTopologySpecificationTest, self).setUp()
        self.topologySpec = SimpleTopologySpecification(self.hwSpecs)
        
    def testIsSatisfiedBy1(self):
        topologyRequest = Topology(24, 6)
        self.assertTrue(self.topologySpec.isSatisfiedBy(topologyRequest))
        
    def testIsSatisfiedBy2(self):
        topologyRequest = Topology(25, 6)
        self.assertFalse(self.topologySpec.isSatisfiedBy(topologyRequest))
        
    def testIsSatisfiedBy3(self):
        topologyRequest = Topology(48, 24)
        self.assertFalse(self.topologySpec.isSatisfiedBy(topologyRequest))
        
class SimpleMappingSpecificationTest(VespaAbstractTest):
    """Unit unit for bean.specs.SimpleMappingSpecification. """
    
    def setUp(self):
        super(SimpleMappingSpecificationTest, self).setUp()
        self.mappingSpec = SimpleMappingSpecification(self.hwSpecs)
        
    def testIsSatisfiedBy1(self):
        mappingRequest = Mapping(6, PinningOpt.BAL_SET)
        self.assertTrue(self.mappingSpec.isSatisfiedBy(mappingRequest))
        
    def testIsSatisfiedBy2(self):
        mappingRequest = Mapping(6, "BAL_SET")
        self.assertTrue(self.mappingSpec.isSatisfiedBy(mappingRequest))
        
    def testIsSatisfiedBy3(self):
        mappingRequest = Mapping(6, "BAL_SAT")
        self.assertFalse(self.mappingSpec.isSatisfiedBy(mappingRequest))
        
    def testIsSatisfiedBy4(self):
        mappingRequest = Mapping(13, PinningOpt.BAL_SET)
        self.assertFalse(self.mappingSpec.isSatisfiedBy(mappingRequest))

class SimpleClusterSpecificationTest(VespaAbstractTest):
    """Unit unit for bean.specs.SimpleClusterSpecification. """
    
    def setUp(self):
        super(SimpleClusterSpecificationTest, self).setUp()
        self.clusterSpec = SimpleClusterPlacementSpecification(self.hwSpecs)
        
    def testIsSatisfiedBy1(self):
        topologyRequest = Topology(18, 3)
        mappingRequest = Mapping(6, PinningOpt.BAL_SET)
        self.assertTrue(self.clusterSpec.isSatisfiedBy(topologyRequest, mappingRequest))
        
    def testIsSatisfiedBy2(self):
        topologyRequest = Topology(18, 1)
        mappingRequest = Mapping(6, PinningOpt.BAL_SET) # BAL_SET not valid (equals BAL_ONE)
        self.assertFalse(self.clusterSpec.isSatisfiedBy(topologyRequest, mappingRequest))
        
    def testIsSatisfiedBy3(self):
        topologyRequest = Topology(24, 12)
        mappingRequest = Mapping(6, PinningOpt.BAL_SET) # idf not valid with topology
        self.assertFalse(self.clusterSpec.isSatisfiedBy(topologyRequest, mappingRequest))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()