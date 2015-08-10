'''
Created on Nov 1, 2013
Unit tests for ConfiguratorFactory
@author: giacomo
'''
import unittest
import shutil

from unit.test_abstract import VespaDeploymentAbstractTest
from submit.config import ConfiguratorFactory,\
    ApplicationConfiguratorPBS, ExecutionConfiguratorPBS

class MockApplicationConfigurator():
    
    def isTorqueBased(self, appRequest):
        return True
    
    def getConfigFor(self, appRequest):
        mockParams = {'app.home' : '/home/giacomo2/shared/PARPACBench-1.4',
                    'app.executable' : 'PARPACBench',
                    'exec.walltime' : '120:00',
                    'exec.needsoutputcopy' : 'Y',
                    'exec.otheroutput' : '/home/giacomo2/shared/PARPACBench-1.4/results/parpacbench_${np}cpu_32lbu.out',
                    'exec.outputrename' : 'custom.out'}
        return mockParams
    

class ConfiguratorFactoryTest(VespaDeploymentAbstractTest):

    def setUp(self):
        VespaDeploymentAbstractTest.setUp(self)
        
        # mock appConfig for this unit test
        appConfig = MockApplicationConfigurator()
        self.configFactory = ConfiguratorFactory(self.runOpts, appConfig, None) # no NetworkAddresses

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
        appConfigurator = self.configFactory.createApplicationConfigurator(self.appRequest, experimentPath, False)
        
        # then
        self.assertTrue(isinstance(appConfigurator, ApplicationConfiguratorPBS))
        
    def testCreateExecutionConfigurator(self):
        
        # when
        execConfigurator = self.configFactory.createExecutionConfigurator(self.appRequest, self.clusterRequest, self.deploymentInfo)
        
        # then
        self.assertTrue(isinstance(execConfigurator, ExecutionConfiguratorPBS))
        
class ApplicationConfiguratorPBSTest(VespaDeploymentAbstractTest):
    
    def setUp(self):
        VespaDeploymentAbstractTest.setUp(self)
        appParams = {'app.home' : '/home/giacomo2/shared/PARPACBench-1.4',
                    'app.executable' : 'PARPACBench',
                    'exec.walltime' : '120:00',
                    'exec.needsoutputcopy' : 'Y',
                    'exec.otheroutput' : '/home/giacomo2/shared/PARPACBench-1.4/results/parpacbench_${np}cpu_32lbu.out',
                    'exec.outputrename' : 'custom.out'}
        experimentPath = '/home/giacomo2/shared/execs/parpac/nc16-cpv4-idf8-psBAL_ONE/8cdcf43265bb69439bb1ce16e5af43e2f54a60526af23d61238359ec6ff6405f'
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
        
class MockNetworkAddresses():
        
        def networkCIDR(self):
            return '172.16.0.0/16'
        
class ExecutionConfiguratorPBSTest(VespaDeploymentAbstractTest):
    '''
<<<<<<< HEAD:tests/unit/run_config.py
    Unit test for ExecutionConfiguratorPBS. Tests the construction of the PBS_TOPOLOGY
    string, as well as the enhancement of the PBS file. The NetworkAddresses class
=======
    Unit tests for ExecutionConfiguratorPBS. Tests the construction of the PBS_TOPOLOGY
    string, as well as the enhancement of the PBS file.
>>>>>>> develop:tests/unit/submit_config.py
    '''

    def setUp(self):
        VespaDeploymentAbstractTest.setUp(self)
        mock = MockNetworkAddresses()
        self.execConfigurator = ExecutionConfiguratorPBS(self.clusterRequest, self.deploymentInfo, mock)
    
    def testCreateTopologyString(self):
        # when
        topologyLine = self.execConfigurator.createTopologyString()
        
        # then
        self.assertEqual(topologyLine, 'kvm-pbs082-01:ppn=4+kvm-pbs082-02:ppn=4+kvm-pbs083-01:ppn=4+kvm-pbs083-02:ppn=4')
        
    def testCreateNetworkingString(self):
        # when
        networkString = self.execConfigurator.createNetworkingString()
        
        # then
        self.assertEqual(networkString, '--mca btl_tcp_if_include 172.16.0.0/16 --mca btl self,sm,tcp')
        
        
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
