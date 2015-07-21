'''
Created on Oct 22, 2014

Defines Vespa parameters for testing networking

@author: giacomo
'''
import unittest
from unit.test_abstract import VespaDeploymentAbstractTest

class NetworkAbstractTest(VespaDeploymentAbstractTest):

    def setUp(self):
        VespaDeploymentAbstractTest.setUp(self)
        
        self.networkingOpts = {
                            'network_source' : 'external-bridge',
                            'net_dev' : 'eth0',
                            'net_class' : 'B',
                            'dhcp_b_prefix' : '172.16',
                            'dhcp_b_start' : '1',
                            'dhcp_c_prefix' : '192.168.3',
                            'dhcp_c_start' : '15',
                            'dhcp_c_step' : '15',
                            'net_bridge' : 'br0',
                            'net_name_sriov' : 'vespa-sriov',
                            'net_name_bridge_create' : 'vespa-external-bridge',
                            'net_name_bridge_use' : 'vespa-libvirt-bridge',
                            'net_mac_prefix' : '00:16:36:ff'
                            }
        
        self.physicalNodes = self.deploymentInfo[0]

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()