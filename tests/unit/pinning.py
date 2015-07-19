'''
Created on Oct 14, 2013

@author: giacomo
'''
import unittest
from create.pinning import PinningTextGenerator, \
    PinningVirshTextGenerator, PinningCoreMapper, PinningWriter
from core.enum import PinningOpt
from unit.test_abstract import VespaDeploymentAbstractTest


class PinningTestBase(unittest.TestCase):

    def setUp(self):
        self.hwSpecs = {'cores' : 12, 'sockets' : 2}
        
class EnhancesXMLWithPinningsTest(VespaDeploymentAbstractTest):
    
    def setUp(self):
        VespaDeploymentAbstractTest.setUp(self)
        coreMapper = PinningCoreMapper(self.hwSpecs)
        pinningTextGen = PinningTextGenerator(self.hwSpecs, coreMapper)
        self.pinningWriter = PinningWriter(self.vespaPrefs, pinningTextGen)
        
        self.xmlDict = {'kvm-pbs082-01' : open('resources/vms/kvm-pbs082-01-basic.xml', 'r').read(),
                          'kvm-pbs082-02' : open('resources/vms/kvm-pbs082-02-basic.xml', 'r').read()}
        
    def testEnhanceXMLsBalOne(self):
        # given
        cpv = self.clusterRequest.topology.cpv
        pinningOpt = PinningOpt.BAL_ONE
        
        self.maxDiff = None
        self.pinningWriter.setDeploymentContext(self.deploymentInfo)
        outputDict = self.pinningWriter.enhanceXMLs(self.xmlDict, cpv, pinningOpt)
        
        firstXML = outputDict['kvm-pbs082-01']
        self.failUnlessEqual(firstXML, open('resources/vms/kvm-pbs082-01-balone.xml', 'r').read())
        
        secondXML = outputDict['kvm-pbs082-02']
        self.failUnlessEqual(secondXML, open('resources/vms/kvm-pbs082-02-balone.xml', 'r').read())
        
    def testEnhanceXMLsBalSet(self):
        # given
        cpv = self.clusterRequest.topology.cpv
        pinningOpt = PinningOpt.BAL_SET 
        
        self.maxDiff = None
        self.pinningWriter.setDeploymentContext(self.deploymentInfo)
        outputDict = self.pinningWriter.enhanceXMLs(self.xmlDict, cpv, pinningOpt)
        
        firstXML = outputDict['kvm-pbs082-01']
        self.failUnlessEqual(firstXML, open('resources/vms/kvm-pbs082-01-balset.xml', 'r').read())
        
        secondXML = outputDict['kvm-pbs082-02']
        self.failUnlessEqual(secondXML, open('resources/vms/kvm-pbs082-02-balset.xml', 'r').read())

class PinningCoreMapperTest(PinningTestBase):
    
    def setUp(self):
        PinningTestBase.setUp(self)
        self.coreMapper = PinningCoreMapper(self.hwSpecs)
    
    def testGetBalOneCores1(self):
        phyCores = self.coreMapper.getBalOneCores(0, 1)
        self.failUnlessEqual(phyCores, ((0,),))
                                                                                    
        phyCores = self.coreMapper.getBalOneCores(1, 1)
        self.failUnlessEqual(phyCores, ((6,),))
        
        phyCores = self.coreMapper.getBalOneCores(3, 1)
        self.failUnlessEqual(phyCores, ((7,),))
        
        phyCores = self.coreMapper.getBalOneCores(11, 1)
        self.failUnlessEqual(phyCores, ((11,),))
        
    def testGetBalOneCores2(self):
        phyCores = self.coreMapper.getBalOneCores(0, 2)
        self.failUnlessEqual(phyCores, ((0,), (1,)))
        
        phyCores = self.coreMapper.getBalOneCores(1, 2)
        self.failUnlessEqual(phyCores, ((6,), (7,)))
        
        phyCores = self.coreMapper.getBalOneCores(4, 2)
        self.failUnlessEqual(phyCores, ((4,), (5,)))
        
        phyCores = self.coreMapper.getBalOneCores(5, 2)
        self.failUnlessEqual(phyCores, ((10,), (11,)))
        
    def testGetBalOneCores3(self):
        phyCores = self.coreMapper.getBalOneCores(0, 3)
        self.failUnlessEqual(phyCores, ((0,), (1,), (2,)))
        
        phyCores = self.coreMapper.getBalOneCores(1, 3)
        self.failUnlessEqual(phyCores, ((6,), (7,), (8,)))
                
    def testGetBalOneCores4(self):
        phyCores = self.coreMapper.getBalOneCores(0, 4)
        self.failUnlessEqual(phyCores, ((0,), (1,), (2,), (3,)))
        
        phyCores = self.coreMapper.getBalOneCores(1, 4)
        self.failUnlessEqual(phyCores, ((6,), (7,), (8,), (9,)))
        
        phyCores = self.coreMapper.getBalOneCores(2, 4)
        self.failUnlessEqual(phyCores, ((4,), (5,), (10,), (11,)))
        
    def testGetBalOneCores6(self):
        phyCores = self.coreMapper.getBalOneCores(0, 6)
        self.failUnlessEqual(phyCores, ((0,), (1,), (2,), (3,), (4,), (5,)))
        
        phyCores = self.coreMapper.getBalOneCores(1, 6)
        self.failUnlessEqual(phyCores, ((6,), (7,), (8,), (9,), (10,), (11,)))
        
    def testGetBalSetCores1(self):
        phyCores = self.coreMapper.getBalSetCores(0, 1)
        self.failUnlessEqual(phyCores, ((0,),))
                                                                                    
        phyCores = self.coreMapper.getBalSetCores(1, 1)
        self.failUnlessEqual(phyCores, ((6,),))
        
        phyCores = self.coreMapper.getBalSetCores(3, 1)
        self.failUnlessEqual(phyCores, ((7,),))
        
        phyCores = self.coreMapper.getBalSetCores(11, 1)
        self.failUnlessEqual(phyCores, ((11,),))
        
    def testGetBalSetCores3(self):
        phyCores = self.coreMapper.getBalSetCores(0, 3)
        self.failUnlessEqual(phyCores, ((0,1,2), (0,1,2), (0,1,2)))
        
        phyCores = self.coreMapper.getBalSetCores(1, 3)
        self.failUnlessEqual(phyCores, ((6,7,8), (6,7,8), (6,7,8)))
        
    def testGetBalSetCores4(self):
        phyCores = self.coreMapper.getBalSetCores(0, 4)
        self.failUnlessEqual(phyCores, ((0,1,2,3), (0,1,2,3), (0,1,2,3), (0,1,2,3)))
        
        phyCores = self.coreMapper.getBalSetCores(2, 4)
        self.failUnlessEqual(phyCores, ((4,5), (4,5), (10,11), (10,11)))
        
    def testGetBalSetCores12(self):
        phyCores = self.coreMapper.getBalSetCores(0, 12)
        self.failUnlessEqual(phyCores, ((0,1,2,3,4,5), (0,1,2,3,4,5), (0,1,2,3,4,5), (0,1,2,3,4,5), (0,1,2,3,4,5), (0,1,2,3,4,5), (6,7,8,9,10,11), (6,7,8,9,10,11), (6,7,8,9,10,11), (6,7,8,9,10,11), (6,7,8,9,10,11), (6,7,8,9,10,11)))
        
    def testGetGreedyCores1(self):
        phyCores = self.coreMapper.getGreedyCores(0, 1)
        self.failUnlessEqual(phyCores, ((0,),))
                                                                                    
        phyCores = self.coreMapper.getGreedyCores(1, 1)
        self.failUnlessEqual(phyCores, ((1,),))
        
        phyCores = self.coreMapper.getGreedyCores(3, 1)
        self.failUnlessEqual(phyCores, ((3,),))
        
        phyCores = self.coreMapper.getGreedyCores(11, 1)
        self.failUnlessEqual(phyCores, ((11,),))
        
    def testGetGreedyCores3(self):
        phyCores = self.coreMapper.getGreedyCores(0, 3)
        self.failUnlessEqual(phyCores, ((0,),(1,),(2,)))
        
        phyCores = self.coreMapper.getGreedyCores(1, 3)
        self.failUnlessEqual(phyCores, ((3,),(4,),(5,)))
        
        phyCores = self.coreMapper.getGreedyCores(2, 3)
        self.failUnlessEqual(phyCores, ((6,),(7,),(8,)))
        
        phyCores = self.coreMapper.getGreedyCores(3, 3)
        self.failUnlessEqual(phyCores, ((9,),(10,),(11,)))
        
    def testGetGreedyCores4(self):
        phyCores = self.coreMapper.getGreedyCores(0, 4)
        self.failUnlessEqual(phyCores, ((0,), (1,), (2,), (3,)))
        
        phyCores = self.coreMapper.getGreedyCores(1, 4)
        self.failUnlessEqual(phyCores, ((4,), (5,), (6,), (7,)))
        
        phyCores = self.coreMapper.getGreedyCores(2, 4)
        self.failUnlessEqual(phyCores, ((8,), (9,), (10,), (11,)))
        
    def testGetGreedyCores6(self):
        phyCores = self.coreMapper.getGreedyCores(0, 6)
        self.failUnlessEqual(phyCores, ((0,), (1,), (2,), (3,), (4,), (5,)))
        
        phyCores = self.coreMapper.getGreedyCores(1, 6)
        self.failUnlessEqual(phyCores, ((6,), (7,), (8,), (9,), (10,), (11,)))
        
    def testGetSplitCores1(self): # should work as balanced...
        phyCores = self.coreMapper.getSplitCores(0, 1)
        self.failUnlessEqual(phyCores, ((0,),))
                                                                                    
        phyCores = self.coreMapper.getSplitCores(1, 1)
        self.failUnlessEqual(phyCores, ((6,),))
        
        phyCores = self.coreMapper.getSplitCores(3, 1)
        self.failUnlessEqual(phyCores, ((7,),))
        
        phyCores = self.coreMapper.getSplitCores(11, 1)
        self.failUnlessEqual(phyCores, ((11,),))
        
    def testGetSplitCores4(self):
        phyCores = self.coreMapper.getSplitCores(0, 4)
        self.failUnlessEqual(phyCores, ((0,), (1,), (6,), (7,)))
        
        phyCores = self.coreMapper.getSplitCores(1, 4)
        self.failUnlessEqual(phyCores, ((2,), (3,), (8,), (9,)))
        
        phyCores = self.coreMapper.getSplitCores(2, 4)
        self.failUnlessEqual(phyCores, ((4,), (5,), (10,), (11,)))
        
    def testGetSplitCores6(self):
        phyCores = self.coreMapper.getSplitCores(0, 6)
        self.failUnlessEqual(phyCores, ((0,), (1,), (2,), (6,), (7,), (8,)))
        
        phyCores = self.coreMapper.getSplitCores(1, 6)
        self.failUnlessEqual(phyCores, ((3,), (4,), (5,), (9,), (10,), (11,)))
        
    def testGetPhysicalCores(self):
        phyCores = self.coreMapper.getPhysicalCores(PinningOpt.SPLIT, 0, 6)
        self.failUnlessEqual(phyCores, ((0,), (1,), (2,), (6,), (7,), (8,)))
        
        phyCores = self.coreMapper.getPhysicalCores(PinningOpt.GREEDY, 2, 4)
        self.failUnlessEqual(phyCores, ((8,), (9,), (10,), (11,)))
        
        phyCores = self.coreMapper.getPhysicalCores(PinningOpt.BAL_SET, 2, 4)
        self.failUnlessEqual(phyCores, ((4,5), (4,5), (10,11), (10,11)))
        
        phyCores = self.coreMapper.getPhysicalCores(PinningOpt.BAL_ONE, 4, 2)
        self.failUnlessEqual(phyCores, ((4,), (5,)))
        
class PinningTextGeneratorTest(PinningTestBase):
    
    def setUp(self):
        PinningTestBase.setUp(self)
        coreMapper = PinningCoreMapper(self.hwSpecs)
        self.pinningTextGen = PinningTextGenerator(self.hwSpecs, coreMapper)
        
    def testProducePinningText(self):
        self.maxDiff = None
        
        pinningText = self.pinningTextGen.producePinningText(PinningOpt.SPLIT, 0, 6)
        expectedText = '<cputune>\n<vcpupin vcpu="0" cpuset="0"/>\n<vcpupin vcpu="1" cpuset="1"/>\n<vcpupin vcpu="2" cpuset="2"/>\n<vcpupin vcpu="3" cpuset="6"/>\n<vcpupin vcpu="4" cpuset="7"/>\n<vcpupin vcpu="5" cpuset="8"/>\n</cputune>\n'
        self.failUnlessEqual(pinningText, expectedText)
        
        pinningText = self.pinningTextGen.producePinningText(PinningOpt.GREEDY, 2, 4)
        expectedText = '<cputune>\n<vcpupin vcpu="0" cpuset="8"/>\n<vcpupin vcpu="1" cpuset="9"/>\n<vcpupin vcpu="2" cpuset="10"/>\n<vcpupin vcpu="3" cpuset="11"/>\n</cputune>\n'
        self.failUnlessEqual(pinningText, expectedText)
        
        pinningText = self.pinningTextGen.producePinningText(PinningOpt.BAL_SET, 2, 4)
        expectedText = '<cputune>\n<vcpupin vcpu="0" cpuset="4,5"/>\n<vcpupin vcpu="1" cpuset="4,5"/>\n<vcpupin vcpu="2" cpuset="10,11"/>\n<vcpupin vcpu="3" cpuset="10,11"/>\n</cputune>\n'
        self.failUnlessEqual(pinningText, expectedText)

class PinningVirshTextGeneratorTest(PinningTestBase):
        
    def setUp(self):
        PinningTestBase.setUp(self)
        coreMapper = PinningCoreMapper(self.hwSpecs)
        self.pinningVirshGen = PinningVirshTextGenerator(coreMapper)
        
    def testProducePinningText(self):
        self.maxDiff = None
        
        pinningTuple = self.pinningVirshGen.producePinningCalls(PinningOpt.SPLIT, 0, 6)
        expectedTuple = ('virsh vcpupin 0 0', 'virsh vcpupin 1 1', 'virsh vcpupin 2 2', 'virsh vcpupin 3 6', 'virsh vcpupin 4 7', 'virsh vcpupin 5 8') 
        self.failUnlessEqual(pinningTuple, expectedTuple)
        
        pinningTuple = self.pinningVirshGen.producePinningCalls(PinningOpt.GREEDY, 2, 4)
        expectedTuple = ('virsh vcpupin 0 8', 'virsh vcpupin 1 9', 'virsh vcpupin 2 10', 'virsh vcpupin 3 11') 
        self.failUnlessEqual(pinningTuple, expectedTuple)
        
        pinningTuple = self.pinningVirshGen.producePinningCalls(PinningOpt.BAL_SET, 2, 4)
        expectedTuple = ('virsh vcpupin 0 4,5', 'virsh vcpupin 1 4,5', 'virsh vcpupin 2 10,11', 'virsh vcpupin 3 10,11') 
        self.failUnlessEqual(pinningTuple, expectedTuple)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()