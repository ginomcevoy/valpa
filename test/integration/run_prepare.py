'''
Created on Oct 31, 2013

Unit tests for run.prepare

@author: giacomo
'''

import unittest
from run.prepare import PreparesExperiment
from test.test_abstract import ValpaDeploymentAbstractTest

class PreparesExperimentTest(ValpaDeploymentAbstractTest):
    
    def setUp(self):
        super(PreparesExperimentTest, self).setUp()
        self.prepsExperiment = PreparesExperiment(False, self.valpaPrefs, self.runOpts)
        
    def testPrepare(self):
        # when
        (execConfig, experimentPath) = self.prepsExperiment.prepare(self.clusterRequest, self.deploymentInfo, self.appRequest)
        
        # then
        self.maxDiff = None
        self.assertEquals(execConfig, '/tmp/valpa/execs/446bf85f-b4ba-459b-8e04-60394fc00d5c')
        self.assertEquals(open(execConfig, 'r').read(), open('resources/execConfig-expected.output', 'r').read())
        
        self.assertEquals(experimentPath, '/home/giacomo2/shared/execs/parpac/nc16-cpv4-idf8-psBAL_ONE/f2f8b46e1b3decd0735b9247756f92e8e451a4a46b489f66852b2ddd78a68c52')
        
if __name__ == '__main__':
    unittest.main()