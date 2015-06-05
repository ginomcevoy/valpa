'''
Created on Oct 15, 2013

@author: giacomo
'''
import unittest
from test.test_abstract import ValpaDeploymentAbstractTest
from deploy.pinning import BuildsPinningWriter
from network.address import NetworkAddresses
from define.vm import BuildsVMDefinitionGenerator

class VmRequestGeneratorIntegrationTest(ValpaDeploymentAbstractTest):

    def setUp(self):
        super(VmRequestGeneratorIntegrationTest, self).setUp()
        (self.deployedNodes, self.deployedSockets, self.deployedVMs) = self.deploymentInfo
        
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
        # instantiate
        pinningWriterBuilder = BuildsPinningWriter(self.hwSpecs, self.valpaPrefs)
        pinningWriter = pinningWriterBuilder.build()
        networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalCluster, self.hwSpecs)
        buildsVMGenerator = BuildsVMDefinitionGenerator(self.valpaPrefs, pinningWriter, networkAddresses)
        vmDefinitionGenerator = buildsVMGenerator.build()
        
        # call under test
        vmDefinitionGenerator.setDeploymentContext(self.deploymentInfo, False)
        xmlNames = vmDefinitionGenerator.createDefinitions(self.clusterXML, self.clusterRequest, 'testExp')
        
        # verify
        self.assertEqual(xmlNames, self.expectedOutput)
        self.maxDiff = None
        self.assertEqual(open(xmlNames['kvm-pbs082-01'], 'r').read(), self.expectedXMLs[0])
        self.assertEqual(open(xmlNames['kvm-pbs082-02'], 'r').read(), self.expectedXMLs[1])
        self.assertEqual(open(xmlNames['kvm-pbs083-01'], 'r').read(), self.expectedXMLs[2])
        self.assertEqual(open(xmlNames['kvm-pbs083-02'], 'r').read(), self.expectedXMLs[3])

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
