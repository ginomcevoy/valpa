'''
Created on Oct 13, 2013

@author: giacomo
'''
import unittest

from bean.cluster import Cluster, Topology, Mapping, Technology, \
    Tuning, ClusterPlacement
from bean.enum import PinningOpt
from config import hwconfig

class ConsistencyTest(unittest.TestCase):
        
    def setUp(self):
        # hardware info for consistency
        hwInfo = hwconfig.getHardwareInfo("resources/hardware.params")
        self.hwSpecs = hwInfo.getHwSpecs()
        
    def testConsistent1(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(24, 2)
        mapping = Mapping(4, PinningOpt.BAL_SET)
        cluster = Cluster(ClusterPlacement(topology, mapping), Technology(), Tuning(), False)
        self.failUnless(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistent2(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(144, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        cluster = Cluster(ClusterPlacement(topology, mapping), Technology(), Tuning(), False)
        self.failUnless(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistentNot1(self):
        '''
        Test for consistency between physical and virtual cluster
        Virtual cluster too large
        '''
        topology = Topology(156, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        cluster = Cluster(ClusterPlacement(topology, mapping), Technology(), Tuning(), False)
        self.failIf(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistentNot2(self):
        '''
        Test for consistency between physical and virtual cluster
        Use idf = 0 but virtual cluster does not fit in a single PM
        '''
        topology = Topology(24, 2)
        mapping = Mapping(0, PinningOpt.BAL_SET)
        cluster = Cluster(ClusterPlacement(topology, mapping), Technology(), Tuning(), False)
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