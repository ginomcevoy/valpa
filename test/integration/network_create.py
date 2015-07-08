'''
Created on Oct 31, 2014

Unit tests for network.create module

@author: giacomo
'''
import unittest
from network.create import CreatesBasicNetworkXML, EnhancesXMLForCreatingBridge,\
    NetworkArgumentsForSRIOV, NetworkArgumentsForUsingBridge,\
    NetworkArgumentsForCreatingBridge
from integration.root_bootstrap import VespaWithBootstrapAbstractTest

class CreatesBasicNetworkXMLTest(VespaWithBootstrapAbstractTest):
    '''
    Integration tests for CreatesBasicNetworkXMLFromTemplate.
    '''
    def setUp(self):
        super(CreatesBasicNetworkXMLTest, self).setUp()
        networkingOpts = self.bootstrap.getNetworkingOpts()
        networkAddresses = self.bootstrap.getNetworkAddresses()
        
        self.argumentsSRIOV = NetworkArgumentsForSRIOV(networkingOpts)
        self.argumentsUseBridge = NetworkArgumentsForUsingBridge(networkingOpts)
        self.argumentsCreateBridge = NetworkArgumentsForCreatingBridge(networkingOpts, networkAddresses)
        
        self.networkCreator = CreatesBasicNetworkXML()

    def testCreateFromTemplateSRIOV(self):
        # given
        self.networkCreator.setArgumentSolver(self.argumentsSRIOV)
        expectedFilename = 'resources/network/sriov-expected.xml'
        
        # when
        result = self.networkCreator.createXML()
        
        # then
        self.assertTextEqualsContent(result, expectedFilename)
        
    def testCreateFromTemplateUseBridge(self):
        # given
        self.networkCreator.setArgumentSolver(self.argumentsUseBridge)
        expectedFilename = 'resources/network/external-bridge-expected.xml'
        
        # when
        result = self.networkCreator.createXML()
        
        # then
        self.assertTextEqualsContent(result, expectedFilename)
        
    def testCreateFromTemplateCreateBridge0(self):
        # given
        self.networkCreator.setArgumentSolver(self.argumentsCreateBridge)
        nodeIndex = 0
        expectedFilename = 'resources/network/libvirt-bridge-0-expected.xml'
        
        # when
        result = self.networkCreator.createXML(nodeIndex)
        
        # then
        self.assertTextEqualsContent(result, expectedFilename)
        
    def testCreateFromTemplateCreateBridge1(self):
        # given
        self.networkCreator.setArgumentSolver(self.argumentsCreateBridge)
        nodeIndex = 1
        expectedFilename = 'resources/network/libvirt-bridge-1-expected.xml'
        
        # when
        result = self.networkCreator.createXML(nodeIndex)
        
        # then
        self.assertTextEqualsContent(result, expectedFilename)
        
    def assertTextEqualsContent(self, text, expectedFilename):
        self.maxDiff = None
        self.assertMultiLineEqual(text, open(expectedFilename, 'r').read())

class EnhancesXMLForCreatingBridgeTest(VespaWithBootstrapAbstractTest):
    
    def setUp(self):
        super(EnhancesXMLForCreatingBridgeTest, self).setUp()
        physicalCluster = self.bootstrap.getPhysicalCluster()
        allVMDetails = self.bootstrap.getAllVMDetails()
        self.xmlEnhancer = EnhancesXMLForCreatingBridge(physicalCluster, allVMDetails)
        
    def testBuildLineForVM(self):
        # given
        vmName = 'kvm-pbs084-09'
        
        # when
        line = self.xmlEnhancer._buildLineForVM(vmName)
        
        # then expect the DHCP line
        expectedLine = '<host mac="00:16:36:ff:84:09" name="kvm-pbs084-09" ip="172.16.84.9" />\n'
        self.assertEqual(line, expectedLine)
        
    def testBuildLinesForNode(self):
        # given
        nodeName = 'node084'
        
        # when
        lines = self.xmlEnhancer._buildLinesForNode(nodeName)
        
        # then
        expectedLines = ['<host mac="00:16:36:ff:84:01" name="kvm-pbs084-01" ip="172.16.84.1" />\n',
                         '<host mac="00:16:36:ff:84:02" name="kvm-pbs084-02" ip="172.16.84.2" />\n',
                         '<host mac="00:16:36:ff:84:03" name="kvm-pbs084-03" ip="172.16.84.3" />\n',
                         '<host mac="00:16:36:ff:84:04" name="kvm-pbs084-04" ip="172.16.84.4" />\n',
                         '<host mac="00:16:36:ff:84:05" name="kvm-pbs084-05" ip="172.16.84.5" />\n',
                         '<host mac="00:16:36:ff:84:06" name="kvm-pbs084-06" ip="172.16.84.6" />\n',
                         '<host mac="00:16:36:ff:84:07" name="kvm-pbs084-07" ip="172.16.84.7" />\n',
                         '<host mac="00:16:36:ff:84:08" name="kvm-pbs084-08" ip="172.16.84.8" />\n',
                         '<host mac="00:16:36:ff:84:09" name="kvm-pbs084-09" ip="172.16.84.9" />\n',
                         '<host mac="00:16:36:ff:84:10" name="kvm-pbs084-10" ip="172.16.84.10" />\n',
                         '<host mac="00:16:36:ff:84:11" name="kvm-pbs084-11" ip="172.16.84.11" />\n',
                         '<host mac="00:16:36:ff:84:12" name="kvm-pbs084-12" ip="172.16.84.12" />\n']
        
        self.assertEqual(lines, expectedLines)
        
    def testAddDHCPLines(self):
        # given
        nodeName = 'node082'
        networkXML = open('resources/network/libvirt-bridge-0-expected.xml').read()
        
        # when
        ammendedXML = self.xmlEnhancer.addDHCPLines(networkXML, nodeName)
        
        # then
        expectedText = open('resources/network/libvirt-bridge-dhcp-expected.xml').read()
        self.maxDiff = None
        self.assertEqual(ammendedXML, expectedText)
        
class BuildsNetworkXMLsTest(VespaWithBootstrapAbstractTest):
    '''
    Integration test for BuildsNetworkXMLs, tests each networking strategy.
    '''
    
    def setUp(self):
        super(BuildsNetworkXMLsTest, self).setUp()
        self.buildsXMLs = self.bootstrap.getBuildsNetworkXMLs()
        
    def testForSRIOV(self):
        # given
        networkType = 'sriov'
        outputDir = '/tmp'
        
        # when
        self.buildsXMLs.createNetworkXMLs(networkType, outputDir)
        
        # then
        expectedFilename = 'resources/network/sriov-expected.xml'
        self.assertEqualsContent('/tmp/sriov.xml', expectedFilename)
        
    def testForUsingBridge(self):
        # given
        networkType = 'external-bridge'
        outputDir = '/tmp'
        
        # when
        self.buildsXMLs.createNetworkXMLs(networkType, outputDir)
        
        # then
        expectedFilename = 'resources/network/external-bridge-expected.xml'
        self.assertEqualsContent('/tmp/external-bridge.xml', expectedFilename)
        
    def testForCreatingBridge(self):
        # given
        networkType = 'libvirt-bridge'
        outputDir = '/tmp'
        
        # when
        self.buildsXMLs.createNetworkXMLs(networkType, outputDir)
        
        # then
        expectedFilename = 'resources/network/libvirt-bridge-node082-expected.xml'
        self.assertEqualsContent('/tmp/libvirt-bridge-node082.xml', expectedFilename)
        
        expectedFilename = 'resources/network/libvirt-bridge-node093-expected.xml'
        self.assertEqualsContent('/tmp/libvirt-bridge-node093.xml', expectedFilename)
        
        
    def assertEqualsContent(self, outputFilename, expectedFilename):
        self.maxDiff = None
        self.assertMultiLineEqual(open(outputFilename, 'r').read(), open(expectedFilename, 'r').read())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()