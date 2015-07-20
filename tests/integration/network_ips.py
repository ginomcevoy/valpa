'''
Created on Nov 7, 2014

Integration tests for network.ips module

@author: giacomo
'''
import unittest
from unit.test_abstract import VespaWithNodesAbstractTest
from network.ips import SetsAddressesToPhysicalCluster,\
    SetsAddressesToAllPossibleVMs
from network.address import NetworkAddresses
from core.vm import BuildsAllVMDetails

class SetsIpAddressesToPhysicalClusterTest(VespaWithNodesAbstractTest):

    def setUp(self):
        VespaWithNodesAbstractTest.setUp(self)
        networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalCluster, self.hwSpecs)
        self.ipSetter = SetsAddressesToPhysicalCluster(networkAddresses)

    def testSetIpAddresses(self):
        # when
        self.ipSetter.setAddresses(self.physicalCluster)
        
        # unit ip addresses in physical cluster
        ipAddress1 = self.physicalCluster.getNode('node082').getIpAddress()
        self.assertEqual(ipAddress1, '172.16.82.254')
        
        ipAddress2 = self.physicalCluster.getNode('node083').getIpAddress()
        self.assertEqual(ipAddress2, '172.16.83.254')
        
class SetsAddressesToAllPossibleVMsTest(VespaWithNodesAbstractTest):

    def setUp(self):
        VespaWithNodesAbstractTest.setUp(self)
        
        self.vmFactory = BuildsAllVMDetails(self.vespaPrefs, self.hwSpecs, self.physicalCluster)
        self.allVMs = self.vmFactory.build()
        
        networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalCluster, self.hwSpecs)
        self.setter = SetsAddressesToAllPossibleVMs(networkAddresses, self.physicalCluster)

    def testSetAddresses(self):
        # when
        self.setter.setAddresses(self.allVMs)
        
        # then
        ipAddress1 = self.allVMs.getVM('kvm-pbs082-01').getIpAddress()
        macAddress1 = self.allVMs.getVM('kvm-pbs082-01').getMacAddress()
        
        self.assertEquals(ipAddress1, '172.16.82.1')
        self.assertEquals(macAddress1, '00:16:36:ff:82:01')
        
        ipAddress2 = self.allVMs.getVM('kvm-pbs087-12').getIpAddress()
        macAddress2 = self.allVMs.getVM('kvm-pbs087-12').getMacAddress()
        
        self.assertEquals(ipAddress2, '172.16.87.12')
        self.assertEquals(macAddress2, '00:16:36:ff:87:12')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()