'''
Created on Oct 16, 2013

@author: giacomo
'''
import unittest

from create.runner import ClusterExecutor
from unit.test_abstract import VespaDeploymentAbstractTest
from .vespa_bootstrap import VespaWithBootstrapAbstractTest

class ExperimentSetRunnerIntegrationTest(VespaWithBootstrapAbstractTest):
    """Full integration test for ExperimentSetRunner, without deploying
    any real VMs.
    
    """
    
    def setUp(self):
        super(ExperimentSetRunnerIntegrationTest, self).setUp()
    
    def testRunAll(self):
        
        expSetRunner = self.bootstrap.getExperimentSetRunner()
        experimentXML = 'resources/integration/two-exps.xml'
        
        # when
        expSetRunner.readAndExecute(experimentXML)
        
class ClusterDefinerIntegrationTest(VespaWithBootstrapAbstractTest, VespaDeploymentAbstractTest):
    """
    Full integration test for ClusterDefiner.
    """

    def setUp(self):
        VespaDeploymentAbstractTest.setUp(self)
        VespaWithBootstrapAbstractTest.setUp(self)
        
        # vespa XML, as generated by VespaConfig.produceVespaXML
        self.vespaXML = open('resources/vespa-expected.xml', 'r').read()
        self.experimentName = 'testExp'
        
        # get ClusterDefiner instance through the bootstrapper
        clusterFactory = self.bootstrap.getClusterFactory()
        self.clusterDefiner = clusterFactory.createClusterDefiner()
        
        # expected
        self.expectedOutput = {'kvm-pbs082-01' : '/tmp/vespa/xmls/testExp/kvm-pbs082-01.xml',
                               'kvm-pbs082-02' : '/tmp/vespa/xmls/testExp/kvm-pbs082-02.xml',
                               'kvm-pbs083-01' : '/tmp/vespa/xmls/testExp/kvm-pbs083-01.xml',
                               'kvm-pbs083-02' : '/tmp/vespa/xmls/testExp/kvm-pbs083-02.xml'}
        
        self.expectedXMLs = ('resources/integration/kvm-pbs082-01-expected.xml',
                             'resources/integration/kvm-pbs082-02-expected.xml',
                             'resources/integration/kvm-pbs083-01-expected.xml',
                             'resources/integration/kvm-pbs083-02-expected.xml')
        
    def testGeneration(self):
        # call under unit
        (deployedNodes, deployedSockets, deployedVMs) = self.clusterDefiner.defineCluster(self.clusterRequest, self.experimentName, False)  # @UnusedVariable
        
        # verify
        for i, vm in enumerate(deployedVMs):
            self.assertFileContentEqual(vm.getDefinition(), self.expectedXMLs[i])
        
class ClusterExecutorTest(VespaWithBootstrapAbstractTest, VespaDeploymentAbstractTest):
    
    def setUp(self):
        VespaDeploymentAbstractTest.setUp(self)
        VespaWithBootstrapAbstractTest.setUp(self)
        configFactory = self.bootstrap.getConfiguratorFactory()
        self.executor = ClusterExecutor(configFactory, False, self.vespaPrefs, self.runOpts)
    
    def testPrepareAndExecute(self):
        (execConfig, executionFile) = self.executor.prepareAndExecute(self.clusterRequest, self.deploymentInfo, self.appRequest)
        
        self.assertFileContentEqual(execConfig, 'resources/execConfig-expected.output')
        self.assertFileContentEqual(executionFile, 'resources/torque/pbs-exec-expected.pbs')
    
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
