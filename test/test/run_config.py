'''
Created on Nov 1, 2013
Unit tests for ConfiguratorFactory
@author: giacomo
'''
import unittest
from run.config import ConfiguratorFactory, ApplicationConfiguratorPBS,\
    ExecutionConfiguratorPBS
import shutil
from test.test_abstract import ValpaDeploymentAbstractTest

class ConfiguratorFactoryTest(ValpaDeploymentAbstractTest):

    def setUp(self):
        super(ConfiguratorFactoryTest, self).setUp()
        self.appParams = {'app.home' : '/home/giacomo2/shared/PARPACBench-1.4',
                    'app.executable' : 'PARPACBench',
                    'exec.walltime' : '60:00',
                    'exec.needsoutputcopy' : 'Y',
                    'exec.otheroutput' : '/home/giacomo2/shared/PARPACBench-1.4/results/parpacbench_${np}cpu_32lbu.out',
                    'exec.outputrename' : 'custom.out'}
        self.configFactory = ConfiguratorFactory(self.runOpts)

    def testCreateBasicExecutionFile(self):
        # given
        experimentPath = '/tmp' # should exist!
        
        # when
        pbsFile = self.configFactory.createBasicExecutionFile(self.appRequest, experimentPath)
        
        # then
        self.maxDiff = None
        self.assertEquals(pbsFile, '/tmp/submit.pbs')
        self.assertEquals(open(pbsFile, 'r').read(), open('resources/pbs-copy-expected.pbs', 'r').read())
        
    def testCreateValpaExecutionFile(self):
        # given
        experimentPath = '/tmp' # should exist!
        expectedContent = open('resources/pbs-valpa-expected.pbs', 'r').read()
        
        # when
        pbsFile = self.configFactory.createValpaExecutionFile(self.appRequest, experimentPath)
        
        # then
        self.maxDiff = None
        self.assertEquals(pbsFile, '/tmp/submit.pbs')
        self.assertMultiLineEqual(open(pbsFile, 'r').read(), expectedContent)
        #self.assertEquals(open(pbsFile, 'r').read(), )
        
    def testCreateApplicationConfigurator(self):
        # given
        experimentPath = '/home/giacomo2/shared/execs/parpac/nc16-cpv4-idf8-psBAL_ONE/f2f8b46e1b3decd0735b9247756f92e8e451a4a46b489f66852b2ddd78a68c52'
        
        # when
        appConfigurator = self.configFactory.createApplicationConfigurator(self.appRequest, experimentPath, self.appParams, False)
        
        # then
        self.assertTrue(isinstance(appConfigurator, ApplicationConfiguratorPBS))
        
    def testCreateExecutionConfigurator(self):
        
        # when
        execConfigurator = self.configFactory.createExecutionConfigurator(self.appRequest, self.clusterRequest, self.deploymentInfo)
        
        # then
        self.assertTrue(isinstance(execConfigurator, ExecutionConfiguratorPBS))
        
    def testReadAppParams(self):
        # when
        gotAppParams = self.configFactory.readAppParams(self.appRequest)
        
        # then
        self.assertEquals(gotAppParams, self.appParams)

        
class ApplicationConfiguratorPBSTest(ValpaDeploymentAbstractTest):
    
    def setUp(self):
        super(ApplicationConfiguratorPBSTest, self).setUp()
        appParams = {'app.home' : '/home/giacomo2/shared/PARPACBench-1.4',
                    'app.executable' : 'PARPACBench',
                    'exec.walltime' : '60:00',
                    'exec.needsoutputcopy' : 'Y',
                    'exec.otheroutput' : '/home/giacomo2/shared/PARPACBench-1.4/results/parpacbench_${np}cpu_32lbu.out',
                    'exec.outputrename' : 'custom.out'}
        experimentPath = '/home/giacomo2/shared/execs/parpac/nc16-cpv4-idf8-psBAL_ONE/f2f8b46e1b3decd0735b9247756f92e8e451a4a46b489f66852b2ddd78a68c52'
        self.appConfigurator = ApplicationConfiguratorPBS(self.appRequest, experimentPath, appParams, False)
                 
    def testEnhanceExecutionFile(self):
        # given
        executionFile = '/tmp/submit.pbs'
        shutil.copyfile('resources/pbs-valpa-expected.pbs', executionFile)
        
        # when
        pbsFile = self.appConfigurator.enhanceExecutionFile(executionFile)
        
        # then
        self.maxDiff = None
        self.assertEquals(pbsFile, '/tmp/submit.pbs')
        self.assertEquals(open(pbsFile, 'r').read(), open('resources/pbs-app-expected.pbs', 'r').read())
        
class ExecutionConfiguratorPBSTest(ValpaDeploymentAbstractTest):
    
    def setUp(self):
        super(ExecutionConfiguratorPBSTest, self).setUp()
        self.execConfigurator = ExecutionConfiguratorPBS(self.clusterRequest, self.deploymentInfo)
        
    def testEnhanceExecutionFile(self):
        # given
        executionFile = '/tmp/submit.pbs'
        shutil.copyfile('resources/pbs-app-expected.pbs', executionFile)
        
        # when
        pbsFile = self.execConfigurator.enhanceExecutionFile(executionFile)
        
        # then
        self.maxDiff = None
        self.assertEquals(pbsFile, '/tmp/submit.pbs')
        self.assertEquals(open(pbsFile, 'r').read(), open('resources/pbs-exec-expected.pbs', 'r').read())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()