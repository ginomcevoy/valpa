'''
Created on Sep 21, 2014

@author: giacomo
'''
import unittest

from core import simple_rules
from core.enum import PinningOpt
from core.simple_rules import SimpleRules
from unit.test_abstract import VespaAbstractTest


class SimpleRulesTest(VespaAbstractTest):
    """Unit tests for core.simple_rules.SimpleRules. """
    
    def setUp(self):
        VespaAbstractTest.setUp(self)
        self.simpleRules = SimpleRules(self.hwSpecs)
        
    def testDivisorsOf1(self):
        divisors = simple_rules.divisorsOf(12)
        self.assertEqual(divisors, [1, 2, 3, 4, 6, 12])
        
    def testDivisorsOf2(self):
        divisors = simple_rules.divisorsOf(1)
        self.assertEqual(divisors, [1])
        
    def testDivisorsOf3(self):
        divisors = simple_rules.divisorsOf(12, 4)
        self.assertEqual(divisors, [1, 2, 3, 4])
        
    def testMultiplesOf1(self):
        multiples = simple_rules.multiplesOf(2, 12)
        self.assertEqual(multiples, [2, 4, 6, 8, 10, 12])
        
    def testMultiplesOf2(self):
        multiples = simple_rules.multiplesOf(5, 12)
        self.assertEqual(multiples, [5, 10])
        
    def testMultiplesOf3(self):
        multiples = simple_rules.multiplesOf(12, 12)
        self.assertEqual(multiples, [12, ])
        
    def testMultiplesOf4(self):
        multiples = simple_rules.multiplesOf(22, 12)
        self.assertEqual(multiples, [])
        
    def removeLowerEqualsThan1(self):
        highEnough = simple_rules.removeLowerEqualsThan([1, 2, 3, 4, 5, 6], 3)
        self.assertEqual(highEnough, [3, 4, 5, 6])
        
    def removeLowerEqualsThan2(self):
        highEnough = simple_rules.removeLowerEqualsThan([1, 2, 3, 4, 5, 6], 7)
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
        
    def testFirstNodeIndexPermitted(self):
        self.assertTrue(self.simpleRules.isFirstNodeIndexPermitted(0))
        self.assertTrue(self.simpleRules.isFirstNodeIndexPermitted(3))
        self.assertTrue(self.simpleRules.isFirstNodeIndexPermitted(11))
        self.assertFalse(self.simpleRules.isFirstNodeIndexPermitted(12))
        self.assertFalse(self.simpleRules.isFirstNodeIndexPermitted(-1))
        
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
        
    def testAllNcGivenCpv3(self):
        result = self.simpleRules.allNcGivenCpv(24)
        self.assertEqual(result, [])

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
                
class SimpleRulesSingleNodeTest(VespaAbstractTest):
    """Unit tests for core.simple_rules.SimpleRules, where the physical 
    architecture has been restricted to a single node. 
    
    """
    
    def setUp(self):
        # This call to super will initialize self.hwSpecs,
        # modify it before instantiating SimpleRules object. 
        VespaAbstractTest.setUp(self)
        self.hwSpecs['nodes'] = 1
        self.hwSpecs['coresInCluster'] = 12
        self.simpleRules = SimpleRules(self.hwSpecs)
        
    def testIsNcPermitted(self):
        self.assertTrue(self.simpleRules.isNcPermitted(1))
        self.assertTrue(self.simpleRules.isNcPermitted(2))
        self.assertTrue(self.simpleRules.isNcPermitted(4))
        self.assertTrue(self.simpleRules.isNcPermitted(6))
        self.assertTrue(self.simpleRules.isNcPermitted(12))
        
        self.assertFalse(self.simpleRules.isNcPermitted(0))
        self.assertFalse(self.simpleRules.isNcPermitted(13))
        self.assertFalse(self.simpleRules.isNcPermitted(24))
        
    def testIsCpvPermitted(self):
        self.assertTrue(self.simpleRules.isCpvPermitted(1))
        self.assertTrue(self.simpleRules.isCpvPermitted(2))
        self.assertTrue(self.simpleRules.isCpvPermitted(4))
        self.assertTrue(self.simpleRules.isCpvPermitted(6))
        self.assertTrue(self.simpleRules.isCpvPermitted(12))
        
        self.assertFalse(self.simpleRules.isCpvPermitted(0))
        self.assertFalse(self.simpleRules.isCpvPermitted(13))
        
    def testIsIdfPermitted1(self):
        self.assertTrue(self.simpleRules.isIdfPermitted(-1))
        self.assertTrue(self.simpleRules.isIdfPermitted(0))
        
        self.assertFalse(self.simpleRules.isIdfPermitted(1))
        self.assertFalse(self.simpleRules.isIdfPermitted(2))
        self.assertFalse(self.simpleRules.isIdfPermitted(6))
        self.assertFalse(self.simpleRules.isIdfPermitted(12))
        
    def testAllCpvGivenNc1(self):
        result = self.simpleRules.allCpvGivenNc(1)
        self.assertEqual(result, [1, ])
        
    def testAllCpvGivenNc12(self):
        result = self.simpleRules.allCpvGivenNc(12)
        self.assertEqual(result, [1, 2, 3, 4, 6, 12])
        
    def testAllNcGivenCpv1(self):
        result = self.simpleRules.allNcGivenCpv(1)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        
    def testAllNcGivenCpv2(self):
        result = self.simpleRules.allNcGivenCpv(2)
        self.assertEqual(result, [2, 4, 6, 8, 10, 12])
        
    def testAllNcGivenCpv12(self):
        result = self.simpleRules.allNcGivenCpv(12)
        self.assertEqual(result, [12, ])
        
    def testAllIdfGivenNc6(self):
        result = self.simpleRules.allIdfGivenNc(6)
        self.assertEqual(result, [0, ])
        
    def testAllIdfGivenNc12(self):
        result = self.simpleRules.allIdfGivenNc(12)
        self.assertEqual(result, [0, ])
        
    def testAllIdfGivenCpv1(self):
        result = self.simpleRules.allIdfGivenCpv(1)
        self.assertEqual(result, [0, ])
        
    def testAllNcGivenIdf0(self):
        result = self.simpleRules.allNcGivenIdf(0)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
                
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()