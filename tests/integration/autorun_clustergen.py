'''
Created on Sep 29, 2014

@author: giacomo
'''
import unittest

from autorun.clustergen import SimpleClusterGenerator
from autorun.constraint import SimpleClusterConstraint,\
    SimpleClusterGenerationSpecification
from bean.enum import PinningOpt
from unit.test_abstract import VespaAbstractTest


class ClusterGenerationTest(VespaAbstractTest):
    '''
    Integration unit for SimpleClusterGenerator. Tests the generated space
    for virtual clusters after aggregating some constraints.
    '''

    def setUp(self):
        # load fixed Vespa settings
        super(ClusterGenerationTest, self).setUp()
        
        self.clusterGenerator = SimpleClusterGenerator(self.hwSpecs)
        self.simpleGenSpec = SimpleClusterGenerationSpecification(self.hwSpecs)

    def testGenerateSingleCluster(self):
        
        # nc constraint
        clusterConstraint1 = SimpleClusterConstraint()
        clusterConstraint1.constrainNc([1, ])
        
        # pstrat constraint
        clusterConstraint2 = SimpleClusterConstraint()
        clusterConstraint2.constrainPstrat([PinningOpt.BAL_ONE, ])
        
        # aggregate constraints
        constrainedSpec = self.simpleGenSpec.constrainWith(clusterConstraint1)
        constrainedSpec = constrainedSpec.constrainWith(clusterConstraint2)
        
        clusterRequests = self.clusterGenerator.generateWithSpecification(constrainedSpec)
        
        # should be one cluster request (1, 1, 0, BAL_ONE)
        self.assertEquals(len(clusterRequests), 1)
        clusterRequest = clusterRequests[0]
        
        self.assertTrue(clusterRequest.isConsistentWith(self.hwSpecs))
        
        self.assertEqual(clusterRequest.topology.nc, 1)
        self.assertEqual(clusterRequest.topology.cpv, 1)
        
        self.assertEqual(clusterRequest.mapping.idf, 0)
        self.assertEqual(clusterRequest.mapping.pinningOpt, PinningOpt.BAL_ONE)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()