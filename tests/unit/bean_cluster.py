'''
Created on Oct 13, 2013

@author: giacomo
'''
import unittest

from core.cluster import Cluster, Topology, Mapping, \
    Tuning, ClusterPlacement
from core.enum import PinningOpt
from core import cluster
from unit.test_abstract import VespaAbstractTest

class ConsistencyTest(VespaAbstractTest):
        
    def setUp(self):
        super(ConsistencyTest, self).setUp()
        self.technology = cluster.getDefaultTechnology() 
        
    def testConsistent1(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(24, 2)
        mapping = Mapping(4, PinningOpt.BAL_SET)
        cluster = Cluster(ClusterPlacement(topology, mapping), self.technology, Tuning(), False)
        self.failUnless(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistent2(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(144, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        cluster = Cluster(ClusterPlacement(topology, mapping), self.technology, Tuning(), False)
        self.failUnless(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistentNot1(self):
        '''
        Test for consistency between physical and virtual cluster
        Virtual cluster too large
        '''
        topology = Topology(156, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        cluster = Cluster(ClusterPlacement(topology, mapping), self.technology, Tuning(), False)
        self.failIf(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistentNot2(self):
        '''
        Test for consistency between physical and virtual cluster
        Use idf = 0 but virtual cluster does not fit in a single PM
        '''
        topology = Topology(24, 2)
        mapping = Mapping(0, PinningOpt.BAL_SET)
        cluster = Cluster(ClusterPlacement(topology, mapping), self.technology, Tuning(), False)
        self.failIf(cluster.isConsistentWith(self.hwSpecs))
        
    def testCanBeDeployedWithin1(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(144, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        clusterPlacement = ClusterPlacement(topology, mapping)
        self.failUnless(clusterPlacement.canBeDeployedWithin(12))
        
    def testCanBeDeployedWithin2(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(144, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        clusterPlacement = ClusterPlacement(topology, mapping)
        self.failIf(clusterPlacement.canBeDeployedWithin(11))
        
    def testCanBeDeployedWithin3(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(144, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        clusterPlacement = ClusterPlacement(topology, mapping)
        self.failUnless(clusterPlacement.canBeDeployedWithin(13))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDeployedNodesSubset']
    unittest.main()