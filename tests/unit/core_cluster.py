'''
Created on Oct 13, 2013

@author: giacomo
'''
import unittest

from core.cluster import ClusterRequest, Topology, Mapping, \
    Tuning, ClusterPlacement, SetsTechnologyDefaults, Technology
from core.enum import PinningOpt, DiskOpt, NetworkOpt
from unit.test_abstract import VespaAbstractTest, VespaDeploymentAbstractTest

class ConsistencyTest(VespaAbstractTest):
        
    def setUp(self):
        VespaAbstractTest.setUp(self)
        self.technology = Technology(NetworkOpt.vhost, DiskOpt.virtio, False)
        
    def testConsistent1(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(24, 2)
        mapping = Mapping(4, PinningOpt.BAL_SET)
        cluster = ClusterRequest(ClusterPlacement(topology, mapping), self.technology, Tuning(), False)
        self.failUnless(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistent2(self):
        '''
        Test for consistency between physical and virtual cluster
        '''
        topology = Topology(144, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        cluster = ClusterRequest(ClusterPlacement(topology, mapping), self.technology, Tuning(), False)
        self.failUnless(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistentNot1(self):
        '''
        Test for consistency between physical and virtual cluster
        Virtual cluster too large
        '''
        topology = Topology(156, 2)
        mapping = Mapping(12, PinningOpt.BAL_SET)
        cluster = ClusterRequest(ClusterPlacement(topology, mapping), self.technology, Tuning(), False)
        self.failIf(cluster.isConsistentWith(self.hwSpecs))
        
    def testConsistentNot2(self):
        '''
        Test for consistency between physical and virtual cluster
        Use idf = 0 but virtual cluster does not fit in a single PM
        '''
        topology = Topology(24, 2)
        mapping = Mapping(0, PinningOpt.BAL_SET)
        cluster = ClusterRequest(ClusterPlacement(topology, mapping), self.technology, Tuning(), False)
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
        
class TestClusterDefaults(VespaDeploymentAbstractTest):
    """Unit test for ClusterDefaults class. """
    
    def setUp(self):
        super(TestClusterDefaults, self).setUp()
        self.technologySetter = SetsTechnologyDefaults(self.createParams)

    def testSetDefaultsOnNoInfiniband(self):
        # given that VespaDeploymentAbstractTest has 
        # NetworkOpt.vhost, DiskOpt.scsi set, infinibandFlag is unset
        technology = self.clusterRequest.technology
        
        # when
        technology = self.technologySetter.setDefaultsOn(technology)
        
        # then
        self.assertEqual(technology.networkOpt, NetworkOpt.vhost)
        self.assertEqual(technology.diskOpt, DiskOpt.scsi)
        self.assertEqual(technology.infinibandFlag, False)
        
    def testSetDefaultsOnInfinibandTrue(self):
        # given that VespaDeploymentAbstractTest has 
        # NetworkOpt.vhost, DiskOpt.scsi set, infinibandFlag is set manually
        technology = self.clusterRequest.technology
        technology.infinibandFlag = True
        
        # when
        technology = self.technologySetter.setDefaultsOn(technology)
        
        # then
        self.assertEqual(technology.networkOpt, NetworkOpt.vhost)
        self.assertEqual(technology.diskOpt, DiskOpt.scsi)
        self.assertEqual(technology.infinibandFlag, True)

    def testSetDefaultsOnAllUnset(self):
        # given an empty Technology request 
        technology = Technology()
        
        # when
        technology = self.technologySetter.setDefaultsOn(technology)
        
        # then
        self.assertEqual(technology.networkOpt, NetworkOpt.vhost)
        self.assertEqual(technology.diskOpt, DiskOpt.virtio)
        self.assertEqual(technology.infinibandFlag, False)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testDeployedNodesSubset']
    unittest.main()
