'''
Created on Oct 15, 2013

@author: giacomo
'''
import unittest
from unit.test_abstract import VespaDeploymentAbstractTest
from create.pinning import BuildsPinningWriter
from network.address import NetworkAddresses
from create.vm import BuildsVMDefinitionGenerator

class VmRequestGeneratorIntegrationTest(VespaDeploymentAbstractTest):

    def setUp(self):
        super(VmRequestGeneratorIntegrationTest, self).setUp()
        (self.deployedNodes, self.deployedSockets, self.deployedVMs) = self.deploymentInfo
        
        # instantiate
        pinningWriterBuilder = BuildsPinningWriter(self.hwSpecs, self.vespaPrefs)
        pinningWriter = pinningWriterBuilder.build()
        networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalCluster, self.hwSpecs)
        buildsVMGenerator = BuildsVMDefinitionGenerator(self.vespaPrefs, pinningWriter, networkAddresses)
        self.vmDefinitionGenerator = buildsVMGenerator.build()
        
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
        
        # call under test
        self.vmDefinitionGenerator.setDeploymentContext(self.deploymentInfo, False)
        xmlNames = self.vmDefinitionGenerator.createDefinitions(self.clusterXML, self.clusterRequest, 'testExp')
        
        # verify
        self.assertEqual(xmlNames, self.expectedOutput)
        self.assertFileContentEqual(xmlNames['kvm-pbs082-01'], self.expectedXMLs[0])
        self.assertFileContentEqual(xmlNames['kvm-pbs082-02'], self.expectedXMLs[1])
        self.assertFileContentEqual(xmlNames['kvm-pbs083-01'], self.expectedXMLs[2])
        self.assertFileContentEqual(xmlNames['kvm-pbs083-02'], self.expectedXMLs[3])
        
    def testGenerationInfiniband(self):
        # for infiniband only
        clusterXMLInfiniband = open('resources/cluster-expected-infiniband.xml').read()
        self.clusterRequest.technology.infinibandFlag = True
        
        # call under test
        self.vmDefinitionGenerator.setDeploymentContext(self.deploymentInfo, False)
        xmlNames = self.vmDefinitionGenerator.createDefinitions(clusterXMLInfiniband, self.clusterRequest, 'testExp')
        
        # verify a single VM
        expectedXMLInfiniband = 'resources/integration/kvm-pbs082-01-infiniband.xml'
        self.assertFileContentEqual(xmlNames['kvm-pbs082-01'], expectedXMLInfiniband)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
