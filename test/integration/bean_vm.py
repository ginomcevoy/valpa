'''
Created on Jun 23, 2015

@author: giacomo
'''
import unittest

from test.test_abstract import VespaWithNodesAbstractTest

class TestVirtualClusterTemplates(VespaWithNodesAbstractTest):
    '''
    Integration test for AllVMDetails that uses the bootstrapper 
    to create an Ansible inventory for the VMs.
    '''
    def setUp(self):
        super(TestVirtualClusterTemplates, self).setUp()
        self.inventoryFilename = '/tmp/vespa-vm-inventory.test'
    
    def testCreateVirtualInventory(self):
        # when
        self.allVMDetails.createVirtualInventory(self.inventoryFilename)
        
        # then get expected content in the inventory file
        actualContent = open(self.inventoryFilename, 'r').read()
        expectedContent = open('resources/inventory-vm-expected.txt', 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent)
        
    def testCreateVirtualPartialInventory(self):
        # when
        virtualCluster = self.allVMDetails.getSubset(('kvm-pbs082-01', 'kvm-pbs082-02',
                                    'kvm-pbs083-01', 'kvm-pbs083-02',
                                    'kvm-pbs084-01', 'kvm-pbs084-02'
                                    ))
        virtualCluster.createVirtualInventory(self.inventoryFilename)
        
        # then get expected content in the inventory file
        actualContent = open(self.inventoryFilename, 'r').read()
        expectedContent = open('resources/inventory-vm-partial-expected.txt', 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent)
        
    def testCreateVirtualInventoryWithVariables(self):
        # given
        virtualCluster = self.allVMDetails.getSubset(('kvm-pbs082-01', 'kvm-pbs082-02',
                                    'kvm-pbs083-01', 'kvm-pbs083-02',
                                    'kvm-pbs084-01', 'kvm-pbs084-02'
                                    ))
        inventoryVars = {'vmCount' : '6', 'deploymentType' : 'Torque'}
        
        # when
        virtualCluster.createVirtualInventory(self.inventoryFilename, inventoryVars)
        
        # then get expected content in the inventory file
        actualContent = open(self.inventoryFilename, 'r').read()
        expectedContent = open('resources/inventory-vm-vars-expected.txt', 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent)

if __name__ == "__main__":
    unittest.main()
