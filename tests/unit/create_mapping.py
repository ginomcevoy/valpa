'''
Created on Oct 13, 2013

@author: giacomo
'''
import unittest
from create.mapping import MappingResolver
from core.cluster import Topology, ClusterRequest, Mapping, \
    ClusterPlacement
from unit.test_abstract import VespaWithNodesAbstractTest
from core.virtual import VirtualClusterTemplates

class MappingTest(VespaWithNodesAbstractTest):

    def setUp(self):
        # load fixed Vespa settings and physical nodes
        VespaWithNodesAbstractTest.setUp(self)
        self.mappingResolver = MappingResolver(self.hwSpecs, self.physicalCluster, self.allVMDetails)

    def testSpecified(self):
        '''
        Tests MappingResolver for when cluster provides detailed info on
        deployed node and socket ids.
        '''
        # 3 hosts, 2 vms per host, 4 cores each'''
        topology = Topology(24, 4)
        self.testDeployNodes = ('node083', 'node084', 'node087')
        self.testDeploySockets = (1, 2)
        mapping = Mapping(8, None, None, self.testDeployNodes, self.testDeploySockets)
        self.cluster = ClusterRequest(ClusterPlacement(topology, mapping))

        self.mappingResolver.processMappings(self.cluster)

        # deployNodes
        deployNodes = self.mappingResolver.getDeployedNodes()
        self.failIf(deployNodes is None, 'cannot read deployNodes')
        self.failUnlessEqual(deployNodes.nodeNames, self.testDeployNodes)

        # deploySockets
        deploySockets = self.mappingResolver.getDeployedSockets()
        self.failIf(deploySockets is None, 'cannot read deploySockets')
        self.failUnlessEqual(deploySockets, self.testDeploySockets)
    
    def testInferred(self):
        '''
        Tests MappingResolver for when cluster provides detailed info on
        deployed node and socket ids.
        '''
        # 3 hosts, 2 vms per host, 4 cores each
        topology = Topology(24, 4)
        mapping = Mapping(8, None)
        self.cluster = ClusterRequest(ClusterPlacement(topology, mapping))
        
        self.mappingResolver.processMappings(self.cluster)

        # deployNodes
        deployNodes = self.mappingResolver.getDeployedNodes()
        self.failUnlessEqual(deployNodes.nodeNames, ('node082', 'node083', 'node084'))

        # deploySockets
        deploySockets = self.mappingResolver.getDeployedSockets()
        self.failUnlessEqual(deploySockets, (0, 1))
        
    def testInferredOnePM(self):
        '''
        Tests MappingResolver for when cluster provides detailed info on
        deployed node and socket ids.
        '''
        # 1 hosts, 2 vms, 4 cores each
        topology = Topology(8, 4)
        mapping = Mapping(0, None)
        self.cluster = ClusterRequest(ClusterPlacement(topology, mapping))

        self.mappingResolver.processMappings(self.cluster)

        # deployNodes
        deployNodes = self.mappingResolver.getDeployedNodes()
        self.failUnlessEqual(deployNodes.nodeNames, ('node082',))

    def testSingleVM(self):
        '''
        Tests MappingResolver for when cluster provides detailed info on
        deployed node and socket ids.
        '''
        # 1 host, 1 vms, 4 cores
        topology = Topology(4, 4)
        mapping = Mapping(0, None)
        self.cluster = ClusterRequest(ClusterPlacement(topology, mapping))

        self.mappingResolver.processMappings(self.cluster)

        # deployedVMs
        deployedVMs = self.mappingResolver.getDeployedVMs()
        self.failUnless(isinstance(deployedVMs, VirtualClusterTemplates))
        
        node082 = self.physicalCluster.getNode('node082')
        vmName = deployedVMs.getVMNamesForNode(node082)[0]
        self.failUnlessEqual(vmName, 'kvm-pbs082-01')
        
        vmTemplate = deployedVMs.vmTemplateDict[vmName]
        self.failUnlessEqual(vmTemplate.vmDetails.index, 0)
        self.failUnlessEqual(vmTemplate.vmDetails.suffix, '01')
        self.failUnlessEqual(vmTemplate.vmDetails.hostingNode, node082)
        
    def testMultipleVMsMultipleHosts(self):
        
        # 3 hosts, 2 vms per host, 4 cores each
        topology = Topology(24, 4)
        mapping = Mapping(8, None)
        self.cluster = ClusterRequest(ClusterPlacement(topology, mapping))
        
        self.mappingResolver.processMappings(self.cluster)
        
        # deployedVMs
        deployedVMs = self.mappingResolver.getDeployedVMs()
        self.failUnless(isinstance(deployedVMs, VirtualClusterTemplates))

        node083 = self.physicalCluster.getNode('node083')    
        vmsSecondHost = deployedVMs.getVMNamesForNode(node083)
        self.failUnlessEqual(vmsSecondHost, ('kvm-pbs083-01', 'kvm-pbs083-02'))
        
    def testFirstNodeIndex(self):
        # 3 PMs, 2 vms per PM, 4 cores each
        # firstNodeIndex = 3 so it leaves 3 PMs free
        topology = Topology(24, 4)
        mapping = Mapping(8, None, 3)
        self.cluster = ClusterRequest(ClusterPlacement(topology, mapping))
        
        self.mappingResolver.processMappings(self.cluster)
        
        physicalNodes = self.mappingResolver.getDeployedNodes()
        self.assertEquals(physicalNodes.nodeNames, ('node085', 'node086', 'node087'))
        
        virtualCluster = self.mappingResolver.getDeployedVMs()
        node086 = self.physicalCluster.getNode('node086')
        vmNames = virtualCluster.getVMNamesForNode(node086)
        self.assertEquals(vmNames, ('kvm-pbs086-01', 'kvm-pbs086-02'))

        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
