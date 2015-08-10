'''
Created on Oct 31, 2013

Unit tests for submit.prepare

@author: giacomo
'''

import unittest
from submit.prepare import PreparesExperiment
from unit.test_abstract import VespaDeploymentAbstractTest

class PreparesExperimentTest(VespaDeploymentAbstractTest):
    
    def setUp(self):
        VespaDeploymentAbstractTest.setUp(self)
        self.prepsExperiment = PreparesExperiment(False, self.vespaPrefs, self.runOpts)
        
    def testPrepare(self):
        # when
        (execConfig, experimentPath) = self.prepsExperiment.prepare(self.clusterRequest, self.deploymentInfo, self.appRequest)
        
        # then
        self.maxDiff = None
        self.assertEquals(execConfig, '/tmp/vespa/execs/446bf85f-b4ba-459b-8e04-60394fc00d5c')
        self.assertEquals(open(execConfig, 'r').read(), open('resources/execConfig-expected.output', 'r').read())
        
        self.assertEquals(experimentPath, '/home/giacomo2/shared/execs/parpac/nc16-cpv4-idf8-psBAL_ONE/8cdcf43265bb69439bb1ce16e5af43e2f54a60526af23d61238359ec6ff6405f')
        
if __name__ == '__main__':
    unittest.main()