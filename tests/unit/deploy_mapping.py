'''
Created on Oct 13, 2013

@author: giacomo
'''
import unittest
from create.mapping import MappingResolver
from core.cluster import Topology, Cluster, Mapping, \
    ClusterPlacement
from unit.test_abstract import VespaWithNodesAbstractTest
from core.vm import VirtualClusterTemplates

class MappingTest(VespaWithNodesAbstractTest):

    def setUp(self):
        # load fixed Vespa settings and physical nodes
        super(MappingTest, self).setUp()
        self.mappingResolver = MappingResolver(self.hwSpecs, self.vespaPrefs, self.physicalCluster, self.allVMDetails)

    def testSpecified(self):
        '''
        Tests MappingResolver for when cluster provides detailed info on
        deployed node and socket ids.
        '''
        # 3 hosts, 2 vms per host, 4 cores each'''
        topology = Topology(24, 4)
        self.testDeployNodes = ('node083', 'node084', 'node087')
        self.testDeploySockets = (1, 2)
        mapping = Mapping(8, None, self.testDeployNodes, self.testDeploySockets)
        self.cluster = Cluster(ClusterPlacement(topology, mapping))

        self.mappingResolver.processMappings(self.cluster)

        # deployNodes
        deployNodes = self.mappingResolver.getDeployedNodes()
        self.failIf(deployNodes is None, 'cannot read deployNodes')
        self.failUnlessEqual(deployNodes.getNames(), self.testDeployNodes)

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
        self.cluster = Cluster(ClusterPlacement(topology, mapping))
        
        self.mappingResolver.processMappings(self.cluster)

        # deployNodes
        deployNodes = self.mappingResolver.getDeployedNodes()
        self.failUnlessEqual(deployNodes.getNames(), ('node082', 'node083', 'node084'))

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
        self.cluster = Cluster(ClusterPlacement(topology, mapping))

        self.mappingResolver.processMappings(self.cluster)

        # deployNodes
        deployNodes = self.mappingResolver.getDeployedNodes()
        self.failUnlessEqual(deployNodes.getNames(), ('node082',))

    def testSingleVM(self):
        '''
        Tests MappingResolver for when cluster provides detailed info on
        deployed node and socket ids.
        '''
        # 1 host, 1 vms, 4 cores
        topology = Topology(4, 4)
        mapping = Mapping(0, None)
        self.cluster = Cluster(ClusterPlacement(topology, mapping))

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
        self.cluster = Cluster(ClusterPlacement(topology, mapping))
        
        self.mappingResolver.processMappings(self.cluster)
        
        # deployedVMs
        deployedVMs = self.mappingResolver.getDeployedVMs()
        self.failUnless(isinstance(deployedVMs, VirtualClusterTemplates))

        node083 = self.physicalCluster.getNode('node083')    
        vmsSecondHost = deployedVMs.getVMNamesForNode(node083)
        self.failUnlessEqual(vmsSecondHost, ('kvm-pbs083-01', 'kvm-pbs083-02'))
        
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
