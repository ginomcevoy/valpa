'''
Created on Oct 14, 2013

Unit tests for deploy.vmgen module

@author: giacomo
'''
import unittest
from test.test_abstract import ValpaDeploymentAbstractTest
from network.address import NetworkAddresses
from define.vm import VMDefinitionDetails, VMDefinitionBasicGenerator,\
    VMXMLSaver

class VMRequestGenerationDetailsTest(ValpaDeploymentAbstractTest):
    
    def setUp(self):
        super(VMRequestGenerationDetailsTest, self).setUp()
        networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalCluster, self.hwSpecs)
        self.generationDetails = VMDefinitionDetails(self.valpaPrefs, networkAddresses) 
        self.generationDetails.setDeploymentContext(self.deploymentInfo)

    def testGetUUID(self):
        uuidgen = self.generationDetails.getUUID('kvm-pbs082-01')
        #print(uuidgen)
        self.failUnlessEqual(len(uuidgen), len('446bf85f-b4ba-459b-8e04-60394fc00d5c'))
        
    def testGetMAC(self):
        mac = self.generationDetails.getMAC('kvm-pbs082-01')
        self.failUnlessEqual(mac, '00:16:36:ff:82:01')
        
        mac = self.generationDetails.getMAC('kvm-pbs083-02')
        self.failUnlessEqual(mac, '00:16:36:ff:83:02')

    def testGetVmPath(self):
        path = self.generationDetails.getVmPath('kvm-pbs082-01')
        self.failUnlessEqual(path, 'node082/kvm-pbs082-01')
        
        path = self.generationDetails.getVmPath('kvm-pbs083-02')
        self.failUnlessEqual(path, 'node083/kvm-pbs083-02')
        
class BasicVMGenTest(ValpaDeploymentAbstractTest):
    
    def setUp(self):
        super(BasicVMGenTest, self).setUp()
        (deployedNodes, deployedSockets, deployedVMs) = self.deploymentInfo  # @UnusedVariable
        networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalCluster, self.hwSpecs)
        generationDetails = VMDefinitionDetails(self.valpaPrefs, networkAddresses)
        self.basicGen = VMDefinitionBasicGenerator(self.valpaPrefs, generationDetails)
        self.basicGen.setDeploymentContext(self.deploymentInfo, False)

    def testProduceXMLs(self):
        self.maxDiff = None
        
        xmls = self.basicGen.createDefinitions(self.clusterXML)
        self.failUnlessEqual(type(xmls), type({}))
        
        xml08201 = open('resources/vms/kvm-pbs082-01-basic.xml').read() 
        self.failUnlessEqual(xmls['kvm-pbs082-01'], xml08201)
        
        xml08302 = open('resources/vms/kvm-pbs083-02-basic.xml').read() 
        self.failUnlessEqual(xmls['kvm-pbs083-02'], xml08302)
        
class VmXMLSaverTest(ValpaDeploymentAbstractTest):
    '''
    Unit tests for VmXMLSaver
    '''
    
    def setUp(self):
        super(VmXMLSaverTest, self).setUp()
        self.xmlDict = {'kvm-pbs082-01' : open('resources/vms/kvm-pbs082-01-balone.xml', 'r').read(),
                          'kvm-pbs082-02' : open('resources/vms/kvm-pbs082-02-balone.xml', 'r').read()}
        
        self.expectedOutput = {'kvm-pbs082-01' : '/tmp/valpa/xmls/testExp/kvm-pbs082-01.xml',
                               'kvm-pbs082-02' : '/tmp/valpa/xmls/testExp/kvm-pbs082-02.xml'}
        
        (deployedNodes, deployedSockets, deployedVMs) = self.deploymentInfo  # @UnusedVariable
        self.xmlSaver = VMXMLSaver(self.valpaPrefs)
        
    def testSaveXMLs(self):
        xmlNameDict = self.xmlSaver.saveXMLs(self.xmlDict, 'testExp')
        
        self.assertEqual(xmlNameDict, self.expectedOutput)
        self.assertEqual(self.xmlDict['kvm-pbs082-01'], open(self.expectedOutput['kvm-pbs082-01'], 'r').read())
        self.assertEqual(self.xmlDict['kvm-pbs082-02'], open(self.expectedOutput['kvm-pbs082-02'], 'r').read())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()