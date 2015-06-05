'''
Created on Sep 21, 2014

@author: giacomo
'''
import unittest
from config import hwconfig
from bean import simple
from bean.enum import PinningOpt
from bean.cluster import Topology, Mapping
from bean.simple import SimpleRules
from bean.specs import SimpleMappingSpecification,\
    SimpleClusterPlacementSpecification, SimpleTopologySpecification

#  copy.deepcopy(x)

class SimpleRulesTest(unittest.TestCase):
    '''
    Unit test for bean.SimpleRules
    '''
    
    def setUp(self):
        hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')
        hwSpecs = hwInfo.getHwSpecs()
        self.simpleRules = SimpleRules(hwSpecs)
        
    def testDivisorsOf1(self):
        divisors = simple.divisorsOf(12)
        self.assertEqual(divisors, [1, 2, 3, 4, 6, 12])
        
    def testDivisorsOf2(self):
        divisors = simple.divisorsOf(1)
        self.assertEqual(divisors, [1])
        
    def testDivisorsOf3(self):
        divisors = simple.divisorsOf(12, 4)
        self.assertEqual(divisors, [1, 2, 3, 4])
        
    def testMultiplesOf1(self):
        multiples = simple.multiplesOf(2, 12)
        self.assertEqual(multiples, [2, 4, 6, 8, 10, 12])
        
    def testMultiplesOf2(self):
        multiples = simple.multiplesOf(5, 12)
        self.assertEqual(multiples, [5, 10])
        
    def testMultiplesOf3(self):
        multiples = simple.multiplesOf(12, 12)
        self.assertEqual(multiples, [12, ])
        
    def testMultiplesOf4(self):
        multiples = simple.multiplesOf(22, 12)
        self.assertEqual(multiples, [])
        
    def removeLowerEqualsThan1(self):
        highEnough = simple.removeLowerEqualsThan([1, 2, 3, 4, 5, 6], 3)
        self.assertEqual(highEnough, [3, 4, 5, 6])
        
    def removeLowerEqualsThan2(self):
        highEnough = simple.removeLowerEqualsThan([1, 2, 3, 4, 5, 6], 7)
        self.assertEqual(highEnough, [])

    def testIsNcPermitted1(self):
        self.assertTrue(self.simpleRules.isNcPermitted(12))
        
    def testIsNcPermitted2(self):
        self.assertTrue(self.simpleRules.isNcPermitted(144))
        
    def testIsNcPermitted3(self):
        self.assertFalse(self.simpleRules.isNcPermitted(0))
        
    def testIsNcPermitted4(self):
        self.assertFalse(self.simpleRules.isNcPermitted(145))
    
    def testIsNcPermitted5(self):
        self.assertFalse(self.simpleRules.isNcPermitted(12.5))
        
    def testIsCpvPermitted1(self):
        self.assertTrue(self.simpleRules.isCpvPermitted(1))
        
    def testIsCpvPermitted2(self):
        self.assertTrue(self.simpleRules.isCpvPermitted(12))
        
    def testIsCpvPermitted3(self):
        self.assertFalse(self.simpleRules.isCpvPermitted(0))
        
    def testIsCpvPermitted4(self):
        self.assertFalse(self.simpleRules.isCpvPermitted(13))
        
    def testIsCpvPermitted5(self):
        self.assertFalse(self.simpleRules.isCpvPermitted(1.5))
    
    def testIsIdfPermitted1(self):
        self.assertTrue(self.simpleRules.isIdfPermitted(-1))
        
    def testIsIdfPermitted2(self):
        self.assertTrue(self.simpleRules.isIdfPermitted(0))
        
    def testIsIdfPermitted3(self):
        self.assertTrue(self.simpleRules.isIdfPermitted(1))
    
    def testIsIdfPermitted4(self):
        self.assertTrue(self.simpleRules.isIdfPermitted(12))
        
    def testIsIdfPermitted5(self):
        self.assertFalse(self.simpleRules.isIdfPermitted(-2))
        
    def testIsIdfPermitted6(self):
        self.assertFalse(self.simpleRules.isIdfPermitted(13))
        
    def testIsIdfPermitted7(self):
        self.assertFalse(self.simpleRules.isIdfPermitted(1.5))
        
    def testAllNcGivenCpv3(self):
        result = self.simpleRules.allNcGivenCpv(24)
        self.assertEqual(result, [])

    def testAllCpvGivenNc1(self):
        result = self.simpleRules.allCpvGivenNc(1)
        self.assertEqual(result, [1, ])
        
    def testAllCpvGivenNc2(self):
        result = self.simpleRules.allCpvGivenNc(12)
        self.assertEqual(result, [1, 2, 3, 4, 6, 12])
        
    def testAllCpvGivenNc3(self):
        result = self.simpleRules.allCpvGivenNc(24)
        self.assertEqual(result, [1, 2, 3, 4, 6, 8, 12])
        
    def testAllCpvGivenIdf1(self):
        result = self.simpleRules.allCpvGivenIdf(0)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        
    def testAllCpvGivenIdf2(self):
        result = self.simpleRules.allCpvGivenIdf(-1)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        
    def testAllCpvGivenIdf3(self):
        result = self.simpleRules.allCpvGivenIdf(8)
        self.assertEqual(result, [1, 2, 4, 8])
        
    def testAllIdfGivenNc1(self):
        result = self.simpleRules.allIdfGivenNc(12)
        self.assertEqual(result, [0, 1, 2, 3, 4, 6])
        
    def testAllIdfGivenNc2(self):
        result = self.simpleRules.allIdfGivenNc(16)
        self.assertEqual(result, [2, 4, 8])
        
    def testAllIdfGivenNc3(self):
        result = self.simpleRules.allIdfGivenNc(4)
        self.assertEqual(result, [0, 1, 2])
        
    def testAllIdfGivenNc4(self):
        result = self.simpleRules.allIdfGivenNc(144)
        self.assertEqual(result, [12])
        
    def testAllIdfGivenCpv1(self):
        result = self.simpleRules.allIdfGivenCpv(12)
        self.assertEqual(result, [0, 12])
        
    def testAllIdfGivenCpv2(self):
        result = self.simpleRules.allIdfGivenCpv(4)
        self.assertEqual(result, [0, 4, 8, 12])
        
    def testAllCpvGiven1(self):
        result = self.simpleRules.allCpvGiven(144, 12)
        self.assertEqual(result, [1, 2, 3, 4, 6, 12])
        
    def testAllCpvGiven2(self):
        result = self.simpleRules.allCpvGiven(12, 2)
        self.assertEqual(result, [1, 2])
        
    def testAllCpvGiven3(self):
        result = self.simpleRules.allCpvGiven(36, 2) # doesn't fit
        self.assertEqual(result, [])
        
    def testAllIdfGiven1(self):
        result = self.simpleRules.allIdfGiven(144, 12)
        self.assertEqual(result, [12, ])
        
    def testAllIdfGiven2(self):
        result = self.simpleRules.allIdfGiven(12, 1)
        self.assertEqual(result, [0, 1, 2, 3, 4, 6])
        
    def testAllIdfGiven3(self):
        result = self.simpleRules.allIdfGiven(48, 2)
        self.assertEqual(result, [4, 6, 8, 12])
        
    def testAllNcGivenCpv1(self):
        result = self.simpleRules.allNcGivenCpv(12)
        self.assertEqual(result, [12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144])
        
    def testAllNcGivenCpv2(self):
        result = self.simpleRules.allNcGivenCpv(6)
        # 78, 90 .. are not possible because there is no idf that satisfies
        self.assertEqual(result, [6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 84, 96, 108, 120, 132, 144])

    def testAllNcGivenIdf1(self):
        result = self.simpleRules.allNcGivenIdf(12)
        self.assertEqual(result, [24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144])
    
    def testAllNcGivenIdf2(self):
        result = self.simpleRules.allNcGivenIdf(6)
        # 84, ... are not possible because there are not enough PMs
        self.assertEqual(result, [12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72])
        
    def testAllNcGivenIdf0(self):
        result = self.simpleRules.allNcGivenIdf(0)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        
    def testAllNcGiven1(self):
        result = self.simpleRules.allNcGiven(6, 3)
        self.assertEqual(result, [])
        
    def testAllNcGiven2(self):
        result = self.simpleRules.allNcGiven(6, 6)
        self.assertEqual(result, [12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72])
        
    def testAllNcGiven3(self):
        result = self.simpleRules.allNcGiven(2, 0)
        self.assertEqual(result, [2, 4, 6, 8, 10, 12])
        
    def testallPstratGiven1(self):
        result = self.simpleRules.allPstratGiven(6, 2, 0)
        self.assertEqual(sorted(list(result)), [PinningOpt.BAL_ONE, PinningOpt.BAL_SET, PinningOpt.GREEDY, PinningOpt.NONE, PinningOpt.SPLIT])
        
    def testallPstratGiven2(self):
        result = self.simpleRules.allPstratGiven(1, 1, 0)
        self.assertEqual(sorted(list(result)), [PinningOpt.BAL_ONE, PinningOpt.NONE])
        
    def testallPstratGiven3(self):
        result = self.simpleRules.allPstratGiven(12, 12, 0)
        self.assertEqual(sorted(list(result)), [PinningOpt.BAL_ONE, PinningOpt.BAL_SET, PinningOpt.NONE])
        
    def testallPstratGiven4(self):
        result = self.simpleRules.allPstratGiven(144, 1, 12)
        self.assertEqual(sorted(list(result)), [PinningOpt.BAL_ONE, PinningOpt.NONE])
        
    def testallPstratGiven5(self):
        result = self.simpleRules.allPstratGiven(144, 12, 12)
        self.assertEqual(sorted(list(result)), [PinningOpt.BAL_ONE, PinningOpt.BAL_SET, PinningOpt.NONE])
        
    def testCanBeDeployedInAny1(self):
        physicalMachinesTuple = [1, ]
        self.assertTrue(self.simpleRules.canBeDeployedInAny(12, 0, physicalMachinesTuple))
        
    def testCanBeDeployedInAny2(self):
        physicalMachinesTuple = [1, ]
        self.assertFalse(self.simpleRules.canBeDeployedInAny(24, 0, physicalMachinesTuple))
        
    def testCanBeDeployedInAny3(self):
        physicalMachinesTuple = [2, 3]
        self.assertTrue(self.simpleRules.canBeDeployedInAny(4, 2, physicalMachinesTuple))
        
    def testCanBeDeployedInAny4(self):
        physicalMachinesTuple = [2, 3]
        self.assertFalse(self.simpleRules.canBeDeployedInAny(4, 0, physicalMachinesTuple))

                 
class SimpleTopologySpecificationTest(unittest.TestCase):
    '''
    Unit test for bean.SimpleTopologySpecification
    '''
    
    def setUp(self):
        hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')
        hwSpecs = hwInfo.getHwSpecs()
        self.topologySpec = SimpleTopologySpecification(hwSpecs)
        
    def testIsSatisfiedBy1(self):
        topologyRequest = Topology(24, 6)
        self.assertTrue(self.topologySpec.isSatisfiedBy(topologyRequest))
        
    def testIsSatisfiedBy2(self):
        topologyRequest = Topology(25, 6)
        self.assertFalse(self.topologySpec.isSatisfiedBy(topologyRequest))
        
    def testIsSatisfiedBy3(self):
        topologyRequest = Topology(48, 24)
        self.assertFalse(self.topologySpec.isSatisfiedBy(topologyRequest))
        
class SimpleMappingSpecificationTest(unittest.TestCase):
    '''
    Unit test for bean.SimpleMappingSpecification
    '''
    
    def setUp(self):
        hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')
        hwSpecs = hwInfo.getHwSpecs()
        self.mappingSpec = SimpleMappingSpecification(hwSpecs)
        
    def testIsSatisfiedBy1(self):
        mappingRequest = Mapping(6, PinningOpt.BAL_SET)
        self.assertTrue(self.mappingSpec.isSatisfiedBy(mappingRequest))
        
    def testIsSatisfiedBy2(self):
        mappingRequest = Mapping(6, "BAL_SET")
        self.assertTrue(self.mappingSpec.isSatisfiedBy(mappingRequest))
        
    def testIsSatisfiedBy3(self):
        mappingRequest = Mapping(6, "BAL_SAT")
        self.assertFalse(self.mappingSpec.isSatisfiedBy(mappingRequest))
        
    def testIsSatisfiedBy4(self):
        mappingRequest = Mapping(13, PinningOpt.BAL_SET)
        self.assertFalse(self.mappingSpec.isSatisfiedBy(mappingRequest))

class SimpleClusterSpecificationTest(unittest.TestCase):
    '''
    Unit test for bean.SimpleClusterSpecification
    '''
    
    def setUp(self):
        hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')
        hwSpecs = hwInfo.getHwSpecs()
        self.clusterSpec = SimpleClusterPlacementSpecification(hwSpecs)
        
    def testIsSatisfiedBy1(self):
        topologyRequest = Topology(18, 3)
        mappingRequest = Mapping(6, PinningOpt.BAL_SET)
        self.assertTrue(self.clusterSpec.isSatisfiedBy(topologyRequest, mappingRequest))
        
    def testIsSatisfiedBy2(self):
        topologyRequest = Topology(18, 1)
        mappingRequest = Mapping(6, PinningOpt.BAL_SET) # BAL_SET not valid (equals BAL_ONE)
        self.assertFalse(self.clusterSpec.isSatisfiedBy(topologyRequest, mappingRequest))
        
    def testIsSatisfiedBy3(self):
        topologyRequest = Topology(24, 12)
        mappingRequest = Mapping(6, PinningOpt.BAL_SET) # idf not valid with topology
        self.assertFalse(self.clusterSpec.isSatisfiedBy(topologyRequest, mappingRequest))
                
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()