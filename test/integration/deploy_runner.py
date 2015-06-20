'''
Created on Oct 16, 2013

@author: giacomo
'''
import unittest
from deploy.runner import ClusterExecutor
from define.cluster import ClusterDefiner, ClusterXMLGenerator
from test.test_abstract import ValpaDeploymentAbstractTest
from deploy.pinning import BuildsPinningWriter
from network.address import NetworkAddresses
from define.vm import BuildsVMDefinitionGenerator
from start import bootstrap
from deploy.mapping import MappingResolver

class ExperimentSetRunnerPartialIntegrationTest(unittest.TestCase):
    '''
    Full integration test for ExperimentSetRunner, using forReal=False
    (only checks for cluster definition in each experiment) 
    '''
    
    def setUp(self):
        # VALPA configuration files
        self.valpaFilename = 'resources/valpa.params'
        self.hardwareFilename = 'resources/hardware.params'
        self.masterXML = 'resources/master.xml'
        
        # expected
        self.expectedOutput1 = {'kvm-pbs082-01' : '/tmp/valpa/xmls/exp1/kvm-pbs082-01.xml',
                               'kvm-pbs082-02' : '/tmp/valpa/xmls/exp1/kvm-pbs082-02.xml',
                               'kvm-pbs083-01' : '/tmp/valpa/xmls/exp1/kvm-pbs083-01.xml',
                               'kvm-pbs083-02' : '/tmp/valpa/xmls/exp1/kvm-pbs083-02.xml'}
        self.expectedXMLs1 = (open('resources/integration/kvm-pbs082-01-expected.xml').read(),
                             open('resources/integration/kvm-pbs082-02-expected.xml').read(),
                             open('resources/integration/kvm-pbs083-01-expected.xml').read(),
                             open('resources/integration/kvm-pbs083-02-expected.xml').read())
        
        self.expectedOutput2 = {'kvm-pbs082-01' : '/tmp/valpa/xmls/exp2/kvm-pbs082-01.xml'}
        self.expectedXML2 = open('resources/integration/kvm-pbs082-01-second.xml').read()
    
    def testRunAll(self):
        # Bootstrap VALPA
        bootstrap.doBootstrap(False) # forReal is false
        bootstrapper = bootstrap.getInstance()
     
        expSetRunner = bootstrapper.getExperimentSetRunner()
        experimentXML = 'resources/integration/two-exps.xml'
        
        # when
        expSetRunner.readAndExecute(experimentXML)
        
class ClusterDefinerIntegrationTest(ValpaDeploymentAbstractTest):
    '''
    Full integration test for ClusterDefiner.
    '''

    def setUp(self):
        super(ClusterDefinerIntegrationTest, self).setUp()
        
        # valpa XML, as generated by ValpaConfig.produceValpaXML
        self.valpaXML = open('resources/valpa-expected.xml', 'r').read()
        self.experimentName = 'testExp'
        
        # instantiate
        mappingResolver = MappingResolver(self.hwSpecs, self.valpaPrefs, self.physicalCluster, self.allVMDetails)
        clusterXMLGen = ClusterXMLGenerator(self.valpaXML, self.valpaPrefs)
        
        pinningBuilder = BuildsPinningWriter(self.hwSpecs, self.valpaPrefs)
        networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalCluster, self.hwSpecs)
        buildsVmRequestGenerator = BuildsVMDefinitionGenerator(self.valpaPrefs, pinningBuilder.build(), networkAddresses)
        vmDefinitionGenerator = buildsVmRequestGenerator.build()
        
        self.clusterDefiner = ClusterDefiner(mappingResolver, clusterXMLGen, vmDefinitionGenerator)
        
        # expected
        self.expectedOutput = {'kvm-pbs082-01' : '/tmp/valpa/xmls/testExp/kvm-pbs082-01.xml',
                               'kvm-pbs082-02' : '/tmp/valpa/xmls/testExp/kvm-pbs082-02.xml',
                               'kvm-pbs083-01' : '/tmp/valpa/xmls/testExp/kvm-pbs083-01.xml',
                               'kvm-pbs083-02' : '/tmp/valpa/xmls/testExp/kvm-pbs083-02.xml'}
        
        self.expectedXMLs = (open('resources/integration/kvm-pbs082-01-expected.xml').read(),
                             open('resources/integration/kvm-pbs082-02-expected.xml').read(),
                             open('resources/integration/kvm-pbs083-01-expected.xml').read(),
                             open('resources/integration/kvm-pbs083-02-expected.xml').read())
        
    def testGeneration(self):
        # call under test
        (deployedNodes, deployedSockets, deployedVMs) = self.clusterDefiner.defineCluster(self.clusterRequest, self.experimentName, False)  # @UnusedVariable
        
        # verify
        self.maxDiff = None
        self.assertEqual(open(deployedVMs.getDefinitionOf('kvm-pbs082-01'), 'r').read(), self.expectedXMLs[0])
        self.assertEqual(open(deployedVMs.getDefinitionOf('kvm-pbs082-02'), 'r').read(), self.expectedXMLs[1])
        self.assertEqual(open(deployedVMs.getDefinitionOf('kvm-pbs083-01'), 'r').read(), self.expectedXMLs[2])
        self.assertEqual(open(deployedVMs.getDefinitionOf('kvm-pbs083-02'), 'r').read(), self.expectedXMLs[3])
        
class ClusterExecutorTest(ValpaDeploymentAbstractTest):
    
    def setUp(self):
        super(ClusterExecutorTest, self).setUp()
        self.executor = ClusterExecutor(False, self.valpaPrefs, self.runOpts)
    
    def testPrepareAndExecute(self):
        (execConfig, executionFile) = self.executor.prepareAndExecute(self.clusterRequest, self.deploymentInfo, self.appRequest)
        
        self.maxDiff = None
        self.assertEquals(open(execConfig, 'r').read(), open('resources/execConfig-expected.output' , 'r').read())
        self.assertEquals(open(executionFile, 'r').read(), open('resources/pbs-exec-expected.pbs', 'r').read())

    
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
