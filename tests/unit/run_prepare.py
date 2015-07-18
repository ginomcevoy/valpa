'''
Created on Oct 31, 2013

Unit tests for run.prepare

@author: giacomo
'''

import unittest
from run.prepare import ConfigFileGenerator, PreparesExperiment
from unit.test_abstract import VespaDeploymentAbstractTest

class ConfigFileGeneratorTest(VespaDeploymentAbstractTest):
    
    def setUp(self):
        super(ConfigFileGeneratorTest, self).setUp()
        self.excConfigGen = ConfigFileGenerator(False, self.vespaPrefs, self.runOpts)
    
    def testCreateExecConfig(self):
        # when
        (excConfig, deployDir) = self.excConfigGen.createExecConfig(self.clusterRequest, self.deploymentInfo, self.appRequest)
        
        # then
        self.assertEquals(excConfig, '/tmp/vespa/execs/446bf85f-b4ba-459b-8e04-60394fc00d5c')
        self.assertFileContentEqual(excConfig, 'resources/execConfig-expected.output')
        
        self.assertEquals(deployDir, '/home/giacomo2/shared/execs/parpac/nc16-cpv4-idf8-psBAL_ONE')
        
    def testSaveTrimmedExecConfig(self):
        # given
        configFile = 'resources/execConfig-expected.output'
        outputPath = '/tmp'
        excConfigGen = ConfigFileGenerator(False, self.vespaPrefs, self.runOpts)
        
        # when
        trimmedConfigFile = excConfigGen.saveTrimmedExecConfig(configFile, outputPath)
        
        # then
        self.assertEquals(trimmedConfigFile, '/tmp/config.txt')
        self.assertFileContentEqual(trimmedConfigFile, 'resources/trimmedConfig-expected.output')
        
class PreparesExperimentTest(VespaDeploymentAbstractTest):
    
    def setUp(self):
        super(PreparesExperimentTest, self).setUp()
        self.prepsExperiment = PreparesExperiment(False, self.vespaPrefs, self.runOpts)
    
    def testSaveTopology(self):
        # given
        distPath = '/tmp'
        
        # when
        topologyFile = self.prepsExperiment.saveTopology(self.clusterRequest, distPath)
        
        # then
        self.maxDiff = None
        self.assertEquals(topologyFile, '/tmp/topology.txt')
        self.assertEquals(open(topologyFile, 'r').read(), open('resources/topology-expected.output', 'r').read())
        
    def testConfigHash(self):
        # given
        execConfigFile = 'resources/hash.input'
        
        # when
        theHash = self.prepsExperiment.configHash(execConfigFile)
        
        # then
        self.assertEquals(theHash, 'be178c0543eb17f5f3043021c9e5fcf30285e557a4fc309cce97ff9ca6182912')
        

if __name__ == '__main__':
    unittest.main()