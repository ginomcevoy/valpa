'''
Created on Oct 22, 2014

Unit tests for network.address module

@author: giacomo
'''
import unittest
from test.network_base import NetworkAbstractTest
from network.address import NetworkAddresses

class NetworkAddressesTest(NetworkAbstractTest):

    def setUp(self):
        super(NetworkAddressesTest, self).setUp()
        self.networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalNodes, self.hwSpecs)
        
    def testAddressRangeStartB1(self):
        # given node082
        nodeIndex = 0 
        
        # when
        rangeStart = self.networkAddresses.addressRangeStart(nodeIndex)
        
        # then
        self.assertEqual(rangeStart, '172.16.82.1')
        
    def testAddressRangeStartB2(self):
        # given node083
        nodeIndex = 1
        
        # when
        rangeStart = self.networkAddresses.addressRangeStart(nodeIndex)
        
        # then
        self.assertEqual(rangeStart, '172.16.83.1')
        
    def testAddressRangeStartC1(self):
        # given node082 and C class
        nodeIndex = 0 
        self.networkingOpts['net_class'] = 'C'
        
        # when
        rangeStart = self.networkAddresses.addressRangeStart(nodeIndex)
        
        # then
        self.assertEqual(rangeStart, '192.168.3.15')
        
    def testAddressRangeStartC2(self):
        # given node083 and C class
        nodeIndex = 1 
        self.networkingOpts['net_class'] = 'C'
        
        # when
        rangeStart = self.networkAddresses.addressRangeStart(nodeIndex)
        
        # then
        self.assertEqual(rangeStart, '192.168.3.30')


    def testAddressRangeEndB1(self):
        # given node082
        nodeIndex = 0 
        
        # when
        rangeEnd = self.networkAddresses.addressRangeEnd(nodeIndex)
        
        # then
        self.assertEqual(rangeEnd, '172.16.82.12')
        
    def testAddressRangeEndB2(self):
        # given node083
        nodeIndex = 1
        
        # when
        rangeEnd = self.networkAddresses.addressRangeEnd(nodeIndex)
        
        # then
        self.assertEqual(rangeEnd, '172.16.83.12')
        
    def testAddressRangeEndC1(self):
        # given node082 and C class
        nodeIndex = 0 
        self.networkingOpts['net_class'] = 'C'
        
        # when
        rangeEnd = self.networkAddresses.addressRangeEnd(nodeIndex)
        
        # then
        self.assertEqual(rangeEnd, '192.168.3.26')
        
    def testAddressRangeEndC2(self):
        # given node083 and C class
        nodeIndex = 1 
        self.networkingOpts['net_class'] = 'C'
        
        # when
        rangeEnd = self.networkAddresses.addressRangeEnd(nodeIndex)
        
        # then
        self.assertEqual(rangeEnd, '192.168.3.41')
                
    def testGetNodeAddressB1(self):
        # given node082
        nodeIndex = 0 
        
        # when
        nodeAddress = self.networkAddresses.getNodeAddress(nodeIndex)
        
        # then
        self.assertEqual(nodeAddress, '172.16.82.254')
        
    def testGetNodeAddressB2(self):
        # given node083
        nodeIndex = 1
        
        # when
        nodeAddress = self.networkAddresses.getNodeAddress(nodeIndex)
        
        # then
        self.assertEqual(nodeAddress, '172.16.83.254')
        
    def testGetNodeAddressC1(self):
        # given node082 and C class
        nodeIndex = 0 
        self.networkingOpts['net_class'] = 'C'
        
        # when
        nodeAddress = self.networkAddresses.getNodeAddress(nodeIndex)
        
        # then
        self.assertEqual(nodeAddress, '192.168.3.1')
        
    def testGetNodeAddressC2(self):
        # given node083 and C class
        nodeIndex = 1 
        self.networkingOpts['net_class'] = 'C'
        
        # when
        nodeAddress = self.networkAddresses.getNodeAddress(nodeIndex)
        
        # then
        self.assertEqual(nodeAddress, '192.168.3.2')
        
    def testGetVMAddressB1(self):
        # given node082 and second VM
        nodeIndex = 0 
        vmIndex = 1
        
        # when
        vmAddress = self.networkAddresses.getVMAddress(nodeIndex, vmIndex)
        
        # then
        self.assertEqual(vmAddress, '172.16.82.2')
        
    def testGetVMAddressB2(self):
        # given node083 and last VM
        nodeIndex = 1
        vmIndex = 11
        
        # when
        nodeAddress = self.networkAddresses.getVMAddress(nodeIndex, vmIndex)
        
        # then
        self.assertEqual(nodeAddress, '172.16.83.12')
        
    def testGetVMAddressC1(self):
        # given node082, third VM and C class
        nodeIndex = 0 
        vmIndex = 2
        self.networkingOpts['net_class'] = 'C'
        
        # when
        vmAddress = self.networkAddresses.getVMAddress(nodeIndex, vmIndex)
        
        # then
        self.assertEqual(vmAddress, '192.168.3.17')
        
    def testGetVMAddressC2(self):
        # given node083, last VM and C class
        nodeIndex = 1
        vmIndex = 11 
        self.networkingOpts['net_class'] = 'C'
        
        # when
        vmAddress = self.networkAddresses.getVMAddress(nodeIndex, vmIndex)
        
        # then
        self.assertEqual(vmAddress, '192.168.3.41')
        
    def testGetVMMAC1(self):
        # given node082, third VM
        nodeIndex = 0 
        vmIndex = 2
        
        # when
        macAddress = self.networkAddresses.getVMMAC(nodeIndex, vmIndex)
        
        # then
        self.assertEqual(macAddress, '00:16:36:ff:82:03')
        
    def testGetVMMAC2(self):
        # given node083, last VM
        nodeIndex = 1 
        vmIndex = 11
        
        # when
        macAddress = self.networkAddresses.getVMMAC(nodeIndex, vmIndex)
        
        # then
        self.assertEqual(macAddress, '00:16:36:ff:83:12')
        
    def testNetworkBroadcastB(self):
        # B is default
        broadcast = self.networkAddresses.networkBroadcast()
        self.assertEqual(broadcast, '172.16.255.255')
        
    def testNetworkBroadcastC(self):
        # switch to C class
        self.networkingOpts['net_class'] = 'C'
        broadcast = self.networkAddresses.networkBroadcast()
        self.assertEqual(broadcast, '192.168.3.255')

    def testNetworkNetmaskB(self):
        # B is default
        netmask = self.networkAddresses.networkNetmask()
        self.assertEqual(netmask, '255.255.0.0')
        
    def testNetworkNetmaskC(self):
        # switch to C class
        self.networkingOpts['net_class'] = 'C'
        netmask = self.networkAddresses.networkNetmask()
        self.assertEqual(netmask, '255.255.255.0')
        
    def testNetworkRouterB(self):
        # B is default
        router = self.networkAddresses.networkRouter()
        self.assertEqual(router, '172.16.0.254')
        
    def testNetworkRouterC(self):
        # switch to C class
        self.networkingOpts['net_class'] = 'C'
        router = self.networkAddresses.networkRouter()
        self.assertEqual(router, '192.168.3.1')
        
    def testNetworkSubnetB(self):
        # B is default
        subnet = self.networkAddresses.networkSubnet()
        self.assertEqual(subnet, '172.16.0.0')
        
    def testNetworkSubnetC(self):
        # switch to C class
        self.networkingOpts['net_class'] = 'C'
        subnet = self.networkAddresses.networkSubnet()
        self.assertEqual(subnet, '192.168.3.0')
        
    def testNetworkCIDRB(self):
        # B is default
        cidr = self.networkAddresses.networkCIDR()
        self.assertEqual(cidr, '172.16.0.0/16')
        
    def testNetworkCIDRC(self):
        # switch to C class
        self.networkingOpts['net_class'] = 'C'
        cidr = self.networkAddresses.networkCIDR()
        self.assertEqual(cidr, '192.168.3.0/24')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()