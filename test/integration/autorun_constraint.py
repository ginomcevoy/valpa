'''
Created on Sep 29, 2014

@author: giacomo
'''
import unittest
from config import hwconfig
from autorun.constraint import SimpleClusterGenerationSpecification,\
    SimpleClusterConstraint
from bean.enum import PinningOpt
import pprint

class ClusterGenerationSpecificationTest(unittest.TestCase):
    '''
    Integration test for SimpleClusterConstraint and SimpleClusterGenerationSpecification.
    Tests the generated space for virtual clusters after aggregating some constraints.
    '''

    def setUp(self):
        hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')
        hwSpecs = hwInfo.getHwSpecs()
        self.simpleGenSpec = SimpleClusterGenerationSpecification(hwSpecs)

    def testSingleVM1(self):
        '''
        Tests for a single virtual cluster with one VM, using nc=1.
        '''
        # nc constraint
        clusterConstraint1 = SimpleClusterConstraint()
        clusterConstraint1.constrainNc([1, ])
        
        # pstrat constraint
        clusterConstraint2 = SimpleClusterConstraint()
        clusterConstraint2.constrainPstrat([PinningOpt.BAL_ONE, ])
        
        # aggregate constraints
        constrainedSpec = self.simpleGenSpec.constrainWith(clusterConstraint1)
        constrainedSpec = constrainedSpec.constrainWith(clusterConstraint2)
        
        # single virtual cluster with single core, BAL_ONE
        clusterSpace = constrainedSpec.internalSpace
        pstrats = constrainedSpec.pstrats
        
        self.assertEquals(len(clusterSpace), 1)
        self.assertEquals(pstrats, set([PinningOpt.BAL_ONE, ]))
        
    def testSingleVM2(self):
        '''
        Tests for a single virtual cluster with one VM, using physicalMachines=1.
        '''
        # nc constraint
        clusterConstraint1 = SimpleClusterConstraint()
        clusterConstraint1.constrainNc([12, ])
        
        # PMs constraint
        clusterConstraint2 = SimpleClusterConstraint()
        clusterConstraint2.constrainPhysicalMachines([1, ])
        
        # pstrat constraint
        clusterConstraint3 = SimpleClusterConstraint()
        clusterConstraint3.constrainPstrat([PinningOpt.BAL_ONE, ])
        
        # aggregate constraints
        constrainedSpec = self.simpleGenSpec.constrainWith(clusterConstraint1)
        constrainedSpec = constrainedSpec.constrainWith(clusterConstraint2)
        constrainedSpec = constrainedSpec.constrainWith(clusterConstraint3)
        
        # 6 virtual cluster with 12 cores total (cpv=1, 2, 3, 4, 6, 12), BAL_ONE
        clusterSpace = constrainedSpec.internalSpace
        pstrats = constrainedSpec.pstrats
        
        if False:
            pprint.pprint(clusterSpace)
            
        self.assertEquals(list(clusterSpace.keys()), [12, ])
        self.assertEquals(pstrats, set([PinningOpt.BAL_ONE, ]))
        
        # check all combinations for nc = 12
        nc12 = sorted(list(clusterSpace[12]))
        self.assertEquals(nc12, [(1, 0), (2, 0), (3, 0), (4, 0), (6, 0), (12, 0)])
        
    def testUpToTwoMachines(self):
        
        # PMs constraint
        clusterConstraint1 = SimpleClusterConstraint()
        clusterConstraint1.constrainPhysicalMachines([1, 2])
        
        clusterConstraint2 = SimpleClusterConstraint()
        clusterConstraint2.constrainPstrat([PinningOpt.BAL_ONE, ])
        
        # aggregate constraints
        constrainedSpec = self.simpleGenSpec.constrainWith(clusterConstraint1)
        constrainedSpec = constrainedSpec.constrainWith(clusterConstraint2)
        
        if True:
            pprint.pprint(constrainedSpec.internalSpace)
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()