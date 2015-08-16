'''
Created on Nov 2, 2014

@author: giacomo
'''

import imp
import os
import difflib
import unittest

from core import config_vespa
from core import config_hw
from core.cluster import Topology, Mapping, Technology, ClusterRequest,\
    ClusterPlacement
from core.physical import PhysicalNode, PhysicalCluster
from core.enum import PinningOpt, DiskOpt, NetworkOpt, MPIBindOpt
from core.experiment import AppTuning, Application
from core.virtual import BuildsAllVMDetails, VMDetails, VMTemplate,\
    VirtualClusterTemplates, AllVMDetails
import shutil

class VespaTestHelper(unittest.TestCase):
    """ Utility class used for testing, helps validating file content. """
    
    def assertMultiLineEqual(self, first, second, msg=None):
        '''
        Assert that two multi-line strings are equal.
        If they aren't, show a nice diff.
        '''
        isStringFirst = isinstance(first, str) or isinstance(first, unicode)
        isStringSecond = isinstance(second, str) or isinstance(second, unicode)
        self.assertTrue(isStringFirst,
                'First argument is not a string')
        self.assertTrue(isStringSecond,
                'Second argument is not a string')

        if first != second:
            message = ''.join(difflib.ndiff(first.splitlines(True),
                                                second.splitlines(True)))
            if msg:
                message += " : " + msg
            self.fail("Multi-line strings are unequal:\n" + message)

    def assertTextEqualsContent(self, text, expectedFilename):
        self.assertMultiLineEqual(text, open(expectedFilename, 'r').read())
        
    def assertFileContentEqual(self, testFilename, expectedFilename):
        self.assertMultiLineEqual(open(testFilename, 'r').read(), open(expectedFilename, 'r').read())

class VespaAbstractTest(VespaTestHelper):
    '''
    Basic template for most unit tests in Vespa, fixes default configuration using 
    resources/vespa.params and resources/hardware.params.
    '''

    def setUp(self):
        # Hardware
        self.hwInfo = config_hw.getHardwareInfo(specsFile='resources/hardware.params', inventoryFilename='resources/vespa.nodes')
        self.hwSpecs = self.hwInfo.getHwSpecs()
        self.nodeNames = self.hwInfo.getNodeNames()
        
        # Vespa params
        vespaConfig = config_vespa.readVespaConfig('resources/vespa.params')
        (self.createParams, self.submitParams, self.networkParams,
            self.consolidateParams, self.miscParams) = vespaConfig.getAllParams()
    
        
class VespaWithNodesAbstractTest(VespaAbstractTest):
    '''
    Template for unit tests in Vespa that assume a fixed physical cluster.
    The physical cluster has 12 nodes.
    '''
    
    def setUp(self):
        # load fixed Vespa settings
        VespaAbstractTest.setUp(self)
        
        # assume cluster architecture: 12 physical nodes
        node1 = PhysicalNode('node082', 0, 82, '082')
        node2 = PhysicalNode('node083', 1, 83, '083')
        node3 = PhysicalNode('node084', 2, 84, '084')
        node4 = PhysicalNode('node085', 3, 85, '085')
        node5 = PhysicalNode('node086', 4, 86, '086')
        node6 = PhysicalNode('node087', 5, 87, '087')
        node7 = PhysicalNode('node088', 6, 88, '088')
        node8 = PhysicalNode('node089', 7, 89, '089')
        node9 = PhysicalNode('node090', 8, 90, '090')
        node10 = PhysicalNode('node091', 9, 91, '091')
        node11 = PhysicalNode('node092', 10, 92, '092')
        node12 = PhysicalNode('node093', 11, 93, '093')
        nodeDict = {'node082' : node1, 'node083' : node2, 
                    'node084' : node3, 'node085' : node4,
                    'node086' : node5, 'node087' : node6,
                    'node088' : node7, 'node089' : node8,
                    'node090' : node9, 'node091' : node10,
                    'node092' : node11, 'node093' : node12
                    }
        self.physicalCluster = PhysicalCluster(nodeDict)
        
        buildsVMDetails = BuildsAllVMDetails(self.createParams, self.hwSpecs, self.physicalCluster)
        self.allVMDetails = buildsVMDetails.build()
        
class VespaDeploymentAbstractTest(VespaWithNodesAbstractTest):
    """ Template for unit tests in Vespa used for testing virtual cluster deployments.
    
    Inherits the physical cluster from VespaWithNodesAbstractTest, and assumes
    a virtual cluster request.
    
    """
    
    def setUp(self):
        # load fixed Vespa settings and physical nodes
        VespaWithNodesAbstractTest.setUp(self)
    
        # Cluster with 2 PMs, 2 VMs each, cpv=4, all sockets
        topo = Topology(16, 4)
        mappings = Mapping(8, PinningOpt.BAL_ONE)
        technology = Technology(NetworkOpt.vhost, DiskOpt.scsi, infinibandFlag=False)
        self.clusterRequest = ClusterRequest(ClusterPlacement(topo, mappings), technology)
        
        nodeNames = ('node082', 'node083') 
        deployedNodes = self.physicalCluster.getSubset(nodeNames)

        # build virtual cluster deployment manually        
        vm1 = VMDetails('kvm-pbs082-01', 0, '01', deployedNodes.getNode('node082'))
        vm2 = VMDetails('kvm-pbs082-02', 1, '02', deployedNodes.getNode('node082'))
        vm3 = VMDetails('kvm-pbs083-01', 0, '01', deployedNodes.getNode('node083'))
        vm4 = VMDetails('kvm-pbs083-02', 1, '02', deployedNodes.getNode('node083'))
        
        vmDict = {'kvm-pbs082-01' : vm1, 'kvm-pbs082-02' : vm2, 
                  'kvm-pbs083-01' : vm3, 'kvm-pbs083-02' : vm4}
        byNode = {deployedNodes.getNode('node082') : ('kvm-pbs082-01', 'kvm-pbs082-02'), 
                  deployedNodes.getNode('node083') : ('kvm-pbs083-01', 'kvm-pbs083-02')}
        
        allVMDetails = AllVMDetails(vmDict, byNode)
        
        vmTemplate1 = VMTemplate(vm1, 2)
        vmTemplate2 = VMTemplate(vm2, 2)
        vmTemplate3 = VMTemplate(vm3, 2)
        vmTemplate4 = VMTemplate(vm4, 2)
        
        templateDict = {'kvm-pbs082-01' : vmTemplate1, 'kvm-pbs082-02' : vmTemplate2, 
                  'kvm-pbs083-01' : vmTemplate3, 'kvm-pbs083-02' : vmTemplate4}
        
        deployedVMs = VirtualClusterTemplates(templateDict, byNode, allVMDetails)
        
        deployedSockets = (0, 1)
        self.deploymentInfo = (deployedNodes, deployedSockets, deployedVMs)
        
        # Application under test
        appTuning = AppTuning(MPIBindOpt.socket)
        self.appRequest = Application('parpac', 11, 'firstarg secondarg', appTuning)
        
        # assume constructed XML
        self.clusterXML = open('resources/cluster-expected-vhost-scsi.xml', 'r').read()
        
class VespaInfinibandAbstractTest(VespaWithNodesAbstractTest):
    """ Template for unit tests in Vespa used for testing virtual cluster deployments.
    
    Similar to VespaDeploymentAbstractTest, but the deployment is of eight VMs
    in a single PM and Infiniband is enabled.
    """
    
    def setUp(self):
        # load fixed Vespa settings and physical nodes
        VespaWithNodesAbstractTest.setUp(self)
    
        # Cluster of eight single-core VMs with 1 PM
        topo = Topology(8, 1)
        mappings = Mapping(0, PinningOpt.NONE)
        technology = Technology(NetworkOpt.vhost, DiskOpt.scsi, infinibandFlag=True)
        self.clusterRequest = ClusterRequest(ClusterPlacement(topo, mappings), technology)
        
        nodeNames = ('node082',) 
        deployedNodes = self.physicalCluster.getSubset(nodeNames)

        # build virtual cluster deployment manually        
        vm1 = VMDetails('kvm-pbs082-01', 0, '01', deployedNodes.getNode('node082'))
        vm2 = VMDetails('kvm-pbs082-02', 1, '02', deployedNodes.getNode('node082'))
        vm3 = VMDetails('kvm-pbs082-03', 2, '03', deployedNodes.getNode('node082'))
        vm4 = VMDetails('kvm-pbs082-04', 3, '04', deployedNodes.getNode('node082'))
        vm5 = VMDetails('kvm-pbs082-05', 4, '05', deployedNodes.getNode('node082'))
        vm6 = VMDetails('kvm-pbs082-06', 5, '06', deployedNodes.getNode('node082'))
        vm7 = VMDetails('kvm-pbs082-07', 6, '07', deployedNodes.getNode('node082'))
        vm8 = VMDetails('kvm-pbs082-08', 7, '08', deployedNodes.getNode('node082'))
        
        vmDict = {'kvm-pbs082-01' : vm1, 'kvm-pbs082-02' : vm2, 
                  'kvm-pbs082-03' : vm3, 'kvm-pbs082-04' : vm4,
                  'kvm-pbs082-05' : vm5, 'kvm-pbs082-06' : vm6,
                  'kvm-pbs082-07' : vm7, 'kvm-pbs082-08' : vm8}
        byNode = {deployedNodes.getNode('node082') : ('kvm-pbs082-01', 'kvm-pbs082-02',
                                                      'kvm-pbs082-03', 'kvm-pbs082-04',
                                                      'kvm-pbs082-05', 'kvm-pbs082-06',
                                                      'kvm-pbs082-07', 'kvm-pbs082-08')}
        allVMDetails = AllVMDetails(vmDict, byNode)
        
        vmTemplate1 = VMTemplate(vm1, 1)
        vmTemplate2 = VMTemplate(vm2, 1)
        vmTemplate3 = VMTemplate(vm3, 1)
        vmTemplate4 = VMTemplate(vm4, 1)
        vmTemplate5 = VMTemplate(vm5, 1)
        vmTemplate6 = VMTemplate(vm6, 1)
        vmTemplate7 = VMTemplate(vm7, 1)
        vmTemplate8 = VMTemplate(vm8, 1)
        
        templateDict = {'kvm-pbs082-01' : vmTemplate1, 'kvm-pbs082-02' : vmTemplate2, 
                        'kvm-pbs082-03' : vmTemplate3, 'kvm-pbs082-04' : vmTemplate4,
                        'kvm-pbs082-05' : vmTemplate5, 'kvm-pbs082-06' : vmTemplate6,
                        'kvm-pbs082-07' : vmTemplate7, 'kvm-pbs082-08' : vmTemplate8}
        
        deployedVMs = VirtualClusterTemplates(templateDict, byNode, allVMDetails)
        
        deployedSockets = (0, 1)
        self.deploymentInfo = (deployedNodes, deployedSockets, deployedVMs)
        
        # Application under test
        appTuning = AppTuning(MPIBindOpt.socket)
        self.appRequest = Application('parpac', 11, 'firstarg secondarg', appTuning)
        
        # assume constructed XML
        self.clusterXML = open('resources/cluster-expected-infiniband.xml', 'r').read()
    
class ParpacAbstractTest(unittest.TestCase):
    """ Sets up unit and integration tests using the Parpac plugin. """
    
    def setUp(self):
        moduleName = 'read_output'
        fp, pathname, description = imp.find_module(moduleName, ['../apps/parpac',])
        self.read_output = imp.load_module(moduleName, fp, pathname, description)
        
class ConsolidateAbstractTest(VespaTestHelper):
    """ Sets up integration tests for the consolidate functionality.
    
    The resources/consolidate/arriving directory is copied to the /tmp/vespa/tests directory.
    This allows for idem-potent consolidation tests that do not already include 
    intermediary outputs in the input directories.
    
    """ 
    
    def setUp(self):
        VespaTestHelper.setUp(self)
        self.sourceDir = 'resources/consolidate/arriving'
        self.consolidateDir = '/tmp/vespa/tests/consolidate'
        if os.path.exists(self.consolidateDir): # always get a fresh copy
            shutil.rmtree(self.consolidateDir)
        shutil.copytree(self.sourceDir, self.consolidateDir)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
