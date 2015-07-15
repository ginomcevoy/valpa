'''
Created on Nov 1, 2013
Unit tests for ConfiguratorFactory
@author: giacomo
'''
import unittest
from run.config import ConfiguratorFactory, ApplicationConfiguratorPBS,\
    ExecutionConfiguratorPBS
import shutil
from test.test_abstract import VespaDeploymentAbstractTest

class ConfiguratorFactoryTest(VespaDeploymentAbstractTest):

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
        
        # then it should be a copy of the master file
        self.assertEquals(pbsFile, '/tmp/submit.pbs')
        self.assertFileContentEqual(pbsFile, 'resources/torque/master.pbs') 
        
    def testCreateVespaExecutionFile(self):
        # given
        experimentPath = '/tmp' # should exist!
        expectedContentFile = 'resources/torque/pbs-vespa-expected.pbs'
        
        # when
        pbsFile = self.configFactory.createVespaExecutionFile(self.appRequest, experimentPath)
        
        # then
        self.maxDiff = None
        self.assertEquals(pbsFile, '/tmp/submit.pbs')
        self.assertFileContentEqual(pbsFile, expectedContentFile)
        
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

        
class ApplicationConfiguratorPBSTest(VespaDeploymentAbstractTest):
    
    def setUp(self):
        super(ApplicationConfiguratorPBSTest, self).setUp()
        appParams = {'app.home' : '/home/giacomo2/shared/PARPACBench-1.4',
                    'app.executable' : 'PARPACBench',
                    'exec.walltime' : '60:00',
                    'exec.needsoutputcopy' : 'Y',
                    'exec.otheroutput' : '/home/giacomo2/shared/PARPACBench-1.4/results/parpacbench_${np}cpu_32lbu.out',
                    'exec.outputrename' : 'custom.out'}
        experimentPath = '/home/giacomo2/shared/execs/parpac/nc16-cpv4-idf8-psBAL_ONE/a8adc50779f75c6b36fa9c95ddb7fa8a5033df6791235f727a20b0e3e6780e93'
        self.appConfigurator = ApplicationConfiguratorPBS(self.appRequest, experimentPath, appParams, False)
                 
    def testEnhanceExecutionFile(self):
        # given
        executionFile = '/tmp/submit.pbs'
        shutil.copyfile('resources/torque/pbs-vespa-expected.pbs', executionFile)
        
        # when
        pbsFile = self.appConfigurator.enhanceExecutionFile(executionFile)
        
        # then
        self.assertEquals(pbsFile, '/tmp/submit.pbs')
        self.assertFileContentEqual(pbsFile, 'resources/torque/pbs-app-expected.pbs')
        
class ExecutionConfiguratorPBSTest(VespaDeploymentAbstractTest):
    '''
    Unit test for ExecutionConfiguratorPBS. Tests the construction of the PBS_TOPOLOGY
    string, as well as the enhancement of the PBS file.
    '''
    
    def setUp(self):
        super(ExecutionConfiguratorPBSTest, self).setUp()
        self.execConfigurator = ExecutionConfiguratorPBS(self.clusterRequest, self.deploymentInfo)
    
    def testCreateTopologyString(self):
        # when
        topologyLine = self.execConfigurator.createTopologyString()
        
        # then
        self.assertEqual(topologyLine, 'kvm-pbs082-01:ppn=4+kvm-pbs082-02:ppn=4+kvm-pbs083-01:ppn=4+kvm-pbs083-02:ppn=4')
        
        
    def testEnhanceExecutionFile(self):
        # given
        executionFile = '/tmp/submit.pbs'
        shutil.copyfile('resources/torque/pbs-app-expected.pbs', executionFile)
        
        # when
        pbsFile = self.execConfigurator.enhanceExecutionFile(executionFile)
        
        # then
        self.assertEquals(pbsFile, '/tmp/submit.pbs')
        self.assertFileContentEqual(pbsFile, 'resources/torque/pbs-exec-expected.pbs')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()