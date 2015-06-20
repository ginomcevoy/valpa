'''
Created on Nov 7, 2014

Integration tests for bootstrap module. ValpaWithBootstrapAbstractTest
serves as a base test for other integration tests that use the bootstrap.

@author: giacomo
'''
import unittest
from start import bootstrap
from deploy.runner import ExperimentSetRunner

class ValpaWithBootstrapAbstractTest(unittest.TestCase):

    def setUp(self):
        forReal = False # only simulate VM definitions/instantiations
        valpaFilename = 'resources/valpa.params'
        hardwareFilename = 'resources/hardware.params'
        masterXML = 'resources/master.xml'
        bootstrap.doBootstrap(forReal, valpaFilename, hardwareFilename, masterXML)
        self.bootstrap = bootstrap.getInstance()
        
class BootstrapNetworkingTest(ValpaWithBootstrapAbstractTest):
    
    def setUp(self):
        super(BootstrapNetworkingTest, self).setUp()
        
    def testVMNetworking(self):
        allVMDetails = self.bootstrap.getAllVMDetails()
        
        ipAddress = allVMDetails.getIpAddressOf('kvm-pbs086-11')
        self.assertEquals(ipAddress, '172.16.86.11')
        
        macAddress = allVMDetails.getMacAddressOf('kvm-pbs093-04')
        self.assertEquals(macAddress, '00:16:36:ff:93:04')
        
    def testGetExperimentSetRunner(self):
        runner = self.bootstrap.getExperimentSetRunner()
        self.assertTrue(isinstance(runner, ExperimentSetRunner))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()