'''
Created on Nov 2, 2014

@author: giacomo
'''
import unittest
from config import hwconfig, valpaconfig
from bean.cluster import Topology, Mapping, Technology, Cluster,\
    ClusterPlacement
from bean.node import PhysicalNode, NodeCluster
from bean.enum import PinningOpt, DiskOpt, NetworkOpt
from bean.experiment import AppTuning, Application
from bean.vm import BuildsAllVMDetails, VMDetails, VMTemplate,\
    VirtualClusterTemplates


class ValpaAbstractTest(unittest.TestCase):
    '''
    Basic template for most unit tests in VALPA, fixes default configuration using 
    resources/valpa.params and resources/hardware.params.
    '''

    def setUp(self):
        # Hardware
        self.hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')
        self.hwSpecs = self.hwInfo.getHwSpecs()
        
        # Valpa params
        valpaConfig = valpaconfig.readValpaConfig('resources/valpa.params')
        (self.valpaPrefs, self.valpaXMLOpts, self.runOpts, self.networkingOpts) = valpaConfig.getAll()
        
class ValpaWithNodesAbstractTest(ValpaAbstractTest):
    '''
    Template for unit tests in VALPA that assume a fixed physical cluster.
    '''
    
    def setUp(self):
        # load fixed VALPA settings
        super(ValpaWithNodesAbstractTest, self).setUp()
        
        # assume cluster architecture: 3 physical nodes
        node1 = PhysicalNode('node082', 0, 82, '082')
        node2 = PhysicalNode('node083', 1, 83, '083')
        node3 = PhysicalNode('node084', 2, 84, '084')
        node4 = PhysicalNode('node085', 3, 85, '085')
        node5 = PhysicalNode('node086', 4, 86, '086')
        node6 = PhysicalNode('node087', 5, 87, '087')
        nodeDict = {'node082' : node1, 
                    'node083' : node2, 
                    'node084' : node3,
                    'node085' : node4,
                    'node086' : node5,
                    'node087' : node6}
        nodeTuple = ('node082', 'node083', 'node084', 'node085', 'node086', 'node087')
        self.physicalCluster = NodeCluster(nodeDict, nodeTuple)
        
        buildsVMDetails = BuildsAllVMDetails(self.valpaPrefs, self.hwSpecs, self.physicalCluster)
        self.allVMDetails = buildsVMDetails.build()
        
class ValpaDeploymentAbstractTest(ValpaWithNodesAbstractTest):
    '''
    Template for unit tests in VALPA used for testing virtual cluster deployments.
    Inherits the physical cluster from ValpaWithNodesAbstractTest, and assumes
    a virtual cluster request.
    '''
    
    def setUp(self):
        # load fixed VALPA settings and physical nodes
        super(ValpaDeploymentAbstractTest, self).setUp()
    
        # Cluster with 2 PMs, 2 VMs each, cpv=4, all sockets
        topo = Topology(16, 4)
        mappings = Mapping(8, PinningOpt.BAL_ONE)
        technology = Technology(NetworkOpt.vhost, DiskOpt.scsi)
        self.clusterRequest = Cluster(ClusterPlacement(topo, mappings), technology)
        
        nodeNames = ('node082', 'node083') 
        deployedNodes = self.physicalCluster.getSubset(nodeNames)

        # build virtual cluster deployment manually        
        vm1 = VMDetails('kvm-pbs082-01', 0, '01', 'node082')
        vm2 = VMDetails('kvm-pbs082-02', 1, '02', 'node082')
        vm3 = VMDetails('kvm-pbs083-01', 0, '01', 'node083')
        vm4 = VMDetails('kvm-pbs083-02', 1, '02', 'node083')
        
        vmTemplate1 = VMTemplate(vm1, 2)
        vmTemplate2 = VMTemplate(vm2, 2)
        vmTemplate3 = VMTemplate(vm3, 2)
        vmTemplate4 = VMTemplate(vm4, 2)
        
        vmDict = {'kvm-pbs082-01' : vmTemplate1, 'kvm-pbs082-02' : vmTemplate2, 
                  'kvm-pbs083-01' : vmTemplate3, 'kvm-pbs083-02' : vmTemplate4}
        byNode = {'node082' : ('kvm-pbs082-01', 'kvm-pbs082-02'), 'node083' : ('kvm-pbs083-01', 'kvm-pbs083-02')}
        deployedVMs = VirtualClusterTemplates(vmDict, byNode)
        
        deployedSockets = (0, 1)
        self.deploymentInfo = (deployedNodes, deployedSockets, deployedVMs)
        
        # Application under test
        appTuning = AppTuning(True)
        self.appRequest = Application('parpac', 11, 'firstarg secondarg', appTuning)
        
        # assume constructed XML
        self.clusterXML = open('resources/cluster-expected-vhost-scsi.xml', 'r').read()
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()