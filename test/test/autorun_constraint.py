'''
Created on Sep 26, 2014

@author: giacomo
'''
import unittest
from autorun.constraint import SimpleClusterGenerationSpecification,\
    SimpleClusterConstraint
from test.test_abstract import VespaAbstractTest


class SimpleClusterGenerationSpecificationTest(VespaAbstractTest):
    '''
    Unit test for SimpleClusterGenerationSpecification.
    '''

    def setUp(self):
        super(SimpleClusterGenerationSpecificationTest, self).setUp()
        self.simpleGenSpec = SimpleClusterGenerationSpecification(self.hwSpecs)

    def testBuildInternalSpace(self):
        internalSpace = self.simpleGenSpec.internalSpace
        
        # some ncs
        self.assertTrue(12 in internalSpace.keys())
        self.assertFalse(13 in internalSpace.keys())
        
        self.assertFalse(143 in internalSpace.keys())
        self.assertTrue(144 in internalSpace.keys())
        self.assertFalse(145 in internalSpace.keys())
            
        # get combination for nc = 1
        list1 = list(internalSpace[1])
        self.assertEquals(list1, [(1, 0), ])
        
        # get combinations for nc = 2
        list2 = list(internalSpace[2])
        list2.sort()
        self.assertEquals(list2, [(1, 0), (1, 1), (2, 0)])
        
        # get combinations for nc=144
        # combinations are cpv = {1, 2, 3, 4, 6, 12} with idf = 12
        list144 = list(internalSpace[144])
        list144.sort()
        self.assertEquals(list144, [(1, 12), (2, 12), (3, 12), (4, 12), (6, 12), (12, 12)])
        
    def testConstrainWithNc(self):
        # given nc constraint
        ncConstraint = SimpleClusterConstraint()
        ncConstraint.constrainNc([2, 144, 1000])  # 1000 should be ignored
        
        # when
        updatedSpec = self.simpleGenSpec.constrainWith(ncConstraint)
        internalSpace = updatedSpec.internalSpace
        
        # then only 2 and 144 expected
        self.assertEquals(2, len(internalSpace.keys()))
        self.assertTrue(2 in internalSpace.keys())
        self.assertTrue(144 in internalSpace.keys())
        
        # get combinations for nc = 2
        list2 = list(internalSpace[2])
        list2.sort()
        self.assertEquals(list2, [(1, 0), (1, 1), (2, 0)])
        
    def testConstrainWithCpv(self):
        # given cpv constraint
        cpvConstraint = SimpleClusterConstraint()
        cpvConstraint.constrainCpv([2, 6, 13])  # 13 should be ignored
        
        # when
        updatedSpec = self.simpleGenSpec.constrainWith(cpvConstraint)
        internalSpace = updatedSpec.internalSpace
        
        # get combinations for nc = 2
        list2 = list(internalSpace[2])
        list2.sort()
        self.assertEquals(list2, [(2, 0), ])
        
        # get combinations for nc=144
        # combinations are cpv = {2, 6, 12} with idf = 12
        list144 = list(internalSpace[144])
        list144.sort()
        self.assertEquals(list144, [(2, 12), (6, 12)])
        
        # there should be no combinations for nc = 3 or 25
        self.assertFalse(3 in internalSpace.keys())
        self.assertFalse(25 in internalSpace.keys())
        
    def testConstrainWithIdf(self):
        # given idf constraint
        idfConstraint = SimpleClusterConstraint()
        idfConstraint.constrainIdf([0, 16])  # 13 should be ignored
        
        # when
        updatedSpec = self.simpleGenSpec.constrainWith(idfConstraint)
        internalSpace = updatedSpec.internalSpace
        
        # single machine, only nc <= 12
        ncs = internalSpace.keys()
        self.assertEquals(sorted(ncs), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        
        # cpv = 1, 2, 4, 8 for nc = 8
        list8 = list(internalSpace[8])
        list8.sort()
        self.assertEquals(list8, [(1, 0), (2, 0), (4, 0), (8, 0)])
        
    def testTwoConstraints(self):
        
        # given cpv constraint, then idf constraint
        cpvConstraint = SimpleClusterConstraint()
        cpvConstraint.constrainCpv([3, 6, 8])  # 13 should be ignored
        
        idfConstraint = SimpleClusterConstraint()
        idfConstraint.constrainIdf([0, 8])  # 13 should be ignored
        
        # when
        updatedSpec = self.simpleGenSpec.constrainWith(cpvConstraint)
        updatedSpec = updatedSpec.constrainWith(idfConstraint)
        internalSpace = updatedSpec.internalSpace
        
        # then only nc = 3, 6, 8, 9, 12 in a single PM together with all cpv=8,idf=8
        ncs = internalSpace.keys()
        self.assertEquals(sorted(ncs), [3, 6, 8, 9, 12, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96])
        
    def testThreeConstraints(self):
        
        # given nc constraint, then cpv constraint, then idf constraint
        ncConstraint = SimpleClusterConstraint()
        ncConstraint.constrainNc([6, 9, 32, 40, 72])
        
        cpvConstraint = SimpleClusterConstraint()
        cpvConstraint.constrainCpv([3, 6, 8])  # 13 should be ignored
        
        idfConstraint = SimpleClusterConstraint()
        idfConstraint.constrainIdf([0, 8])  # 13 should be ignored
        
        # when
        updatedSpec = self.simpleGenSpec.constrainWith(ncConstraint)
        updatedSpec = updatedSpec.constrainWith(cpvConstraint)
        updatedSpec = updatedSpec.constrainWith(idfConstraint)
        internalSpace = updatedSpec.internalSpace
        
        # then only nc = 6, 9 in a single PM together with nc=(32,40,72) and cpv=8,idf=8
        ncs = internalSpace.keys()
        self.assertEquals(sorted(ncs), [6, 9, 32, 40, 72])
        
        # for nc = 6, 9 only idf = 0
        list6 = list(internalSpace[6])
        self.assertEquals(sorted(list6), [(3, 0), (6, 0)])
        
        list9 = list(internalSpace[9])
        self.assertEquals(sorted(list9), [(3, 0), ])
        
        # for nc=(32,40,72) only cpv=8,idf=8
        list32 = list(internalSpace[32])
        self.assertEquals(sorted(list32), [(8, 8), ])
        
        list40 = list(internalSpace[40])
        self.assertEquals(sorted(list40), [(8, 8), ])
        
        list72 = list(internalSpace[72])
        self.assertEquals(sorted(list72), [(8, 8), ])
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()