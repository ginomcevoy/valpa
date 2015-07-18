'''
Created on Nov 2, 2014

@author: giacomo
'''
import unittest
from unit.test_abstract import VespaWithNodesAbstractTest
from core.vm import BuildsAllVMDetails, VirtualClusterFactory

class BuildsAllVMDetailsTest(VespaWithNodesAbstractTest):

    def setUp(self):
        super(BuildsAllVMDetailsTest, self).setUp()
        self.vmFactory = BuildsAllVMDetails(self.vespaPrefs, self.hwSpecs, self.physicalCluster)

    def testGetAllNodes(self):
        allVMDetails = self.vmFactory.build()

        self.failIf(allVMDetails is None)
        self.failUnlessEqual(len(allVMDetails.vmDict.keys()), 72, 'wrong amount of VMs')
        
        firstNode = self.physicalCluster.getNode('node082')
        vmsInFirstNode = allVMDetails.byNode[firstNode]
        self.failUnlessEqual(vmsInFirstNode[0], 'kvm-pbs082-01')
        self.failUnlessEqual(vmsInFirstNode[11], 'kvm-pbs082-12')

        node087 = self.physicalCluster.getNode('node087')
        vmsInLastNode = allVMDetails.byNode[node087]
        self.failUnlessEqual(vmsInLastNode[5], 'kvm-pbs087-06')
                
        allNames = allVMDetails.getNames()
        self.failUnlessEqual(len(allNames), 72)
        
        aVMIndex = allVMDetails.getVMIndex('kvm-pbs084-02')
        self.failUnlessEqual(aVMIndex, 1)
        
        aVMNumber = allVMDetails.getVMNumber('kvm-pbs085-12')
        self.failUnlessEqual(aVMNumber, 12)
        
        aVMSuffix = allVMDetails.getVMSuffix('kvm-pbs086-08')
        self.failUnlessEqual(aVMSuffix, '08')
        
class AllVMDetailsTest(VespaWithNodesAbstractTest):
    
    def setUp(self):
        super(AllVMDetailsTest, self).setUp()
        self.vmFactory = BuildsAllVMDetails(self.vespaPrefs, self.hwSpecs, self.physicalCluster)
        self.allVMDetails = self.vmFactory.build()
        
    def testGetSubset(self):
        # Choose according to nc=6, cpv=1, idf=2
        vmNames = ('kvm-pbs082-01', 'kvm-pbs082-02',
                   'kvm-pbs083-01', 'kvm-pbs083-02',
                   'kvm-pbs084-01', 'kvm-pbs084-02',)
        subsetDetails = self.allVMDetails.getSubset(vmNames)
        
        # then
        vmDictKeys = subsetDetails.vmDict.keys()
        self.assertEquals(len(vmDictKeys), 6)
        self.assertEquals(sorted(vmDictKeys), sorted(vmNames))
        self.assertEquals(subsetDetails.getHostingNode('kvm-pbs082-02').name, 'node082')
        
        byNodeKeys = subsetDetails.byNode.keys()
        self.assertEquals(len(byNodeKeys), 3)
        
        node082 = self.physicalCluster.getNode('node082')
        node083 = self.physicalCluster.getNode('node083')
        node084 = self.physicalCluster.getNode('node084')
        
        self.assertTrue(node082 in byNodeKeys)
        self.assertTrue(node083 in byNodeKeys)
        self.assertTrue(node084 in byNodeKeys)
        self.assertEquals(sorted(subsetDetails.byNode[node084]), sorted(('kvm-pbs084-01', 'kvm-pbs084-02')))
        

class VirtualClusterFactoryTest(VespaWithNodesAbstractTest):

    def setUp(self):
        super(VirtualClusterFactoryTest, self).setUp()
        vmDetailsFactory = BuildsAllVMDetails(self.vespaPrefs, self.hwSpecs, self.physicalCluster)
        allVMDetails = vmDetailsFactory.build()
        self.vmTemplateFactory = VirtualClusterFactory(allVMDetails)
        
    def testCreate(self):
        # given VMs according to nc=6, cpv=2, idf=4
        vmNames = ('kvm-pbs082-01', 'kvm-pbs082-02',
                   'kvm-pbs083-01', 'kvm-pbs083-02',
                   'kvm-pbs084-01', 'kvm-pbs084-02',)
        cpv = 2
        
        # when
        clusterTemplate = self.vmTemplateFactory.create(vmNames, cpv)
        
        # then
        self.failIf(clusterTemplate is None)
        self.failUnlessEqual(len(clusterTemplate.vmTemplateDict.keys()), 6, 'wrong amount of VMs')
        
        node082 = self.physicalCluster.getNode('node082')
        vmsInFirstNode = clusterTemplate.byNode[node082]
        self.failUnlessEqual(vmsInFirstNode[0], 'kvm-pbs082-01')
        self.failUnlessEqual(vmsInFirstNode[1], 'kvm-pbs082-02')

        node084 = self.physicalCluster.getNode('node084')
        vmsInLastNode = clusterTemplate.byNode[node084]
        self.failUnlessEqual(vmsInLastNode[1], 'kvm-pbs084-02')
                
        allNames = clusterTemplate.getNames()
        self.failUnlessEqual(sorted(allNames), sorted(vmNames))
        
        aVMIndex = clusterTemplate.getVMIndex('kvm-pbs084-02')
        self.failUnlessEqual(aVMIndex, 1)
        
        aVMNumber = clusterTemplate.getVMNumber('kvm-pbs083-02')
        self.failUnlessEqual(aVMNumber, 2)
        
        aVMSuffix = clusterTemplate.getVMSuffix('kvm-pbs082-01')
        self.failUnlessEqual(aVMSuffix, '01')
        
        aCpv = clusterTemplate.getCpv('kvm-pbs084-01')
        self.failUnlessEqual(aCpv, 2)

    def testDefinitionsToFile(self):
        # given VMs according to nc=6, cpv=2, idf=4
        vmNames = ('kvm-pbs082-01', 'kvm-pbs082-02',
                   'kvm-pbs083-01', 'kvm-pbs083-02',
                   'kvm-pbs084-01', 'kvm-pbs084-02',)
        cpv = 2
        clusterTemplate = self.vmTemplateFactory.create(vmNames, cpv)

        # given their templates with XML definitions
        definitionDict = {
            'kvm-pbs082-01' : '/tmp/vespa/kvm-pbs082-01.xml',
            'kvm-pbs082-02' : '/tmp/vespa/kvm-pbs082-02.xml',
            'kvm-pbs083-01' : '/tmp/vespa/kvm-pbs083-01.xml',
            'kvm-pbs083-02' : '/tmp/vespa/kvm-pbs083-02.xml',
            'kvm-pbs084-01' : '/tmp/vespa/kvm-pbs084-01.xml',
            'kvm-pbs084-02' : '/tmp/vespa/kvm-pbs084-02.xml'}
        clusterTemplate.setDefinitions(definitionDict)

        outputFile = '/tmp/clusterTemplate-definitions.txt'
        expectedFile = 'resources/definitions-tofile-expected.txt'
        expectedContent = open(expectedFile, 'r').read()

        # when
        clusterTemplate.definitionsToFile(outputFile)

        # then get expected file content
        self.maxDiff = None
        self.assertEquals(open(outputFile, 'r').read(), expectedContent)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()