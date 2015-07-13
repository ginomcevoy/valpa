'''
Created on Jun 23, 2015

@author: giacomo
'''
import unittest

from test.test_abstract import VespaWithNodesAbstractTest

class TestVirtualClusterTemplates(VespaWithNodesAbstractTest):
    '''
    Integration test for NodeCluster that uses the bootstrapper 
    to create an Ansible inventory for the physical nodes.
    '''
    def setUp(self):
        super(TestVirtualClusterTemplates, self).setUp()
        self.inventoryFilename = '/tmp/vespa-vm-inventory.test'
    
    def testCreateVirtualInventory(self):
        # when
        hostCount = len(self.physicalCluster.getNames())
        vmsPerHost = self.allVMDetails.getVMNamesForNode(self.physicalCluster.getNames()[0])
        self.allVMDetails.createVirtualInventory(self.inventoryFilename, self.physicalCluster, hostCount, vmsPerHost)
        
        # then get expected content in the inventory file
        actualContent = open(self.inventoryFilename, 'r').read()
        expectedContent = open('resources/inventory-vm-expected.txt', 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent)
        
    def testCreateVirtualPartialInventory(self):
        # when
        hostCount = 3
        vmsPerHost = 2
        self.allVMDetails.createVirtualInventory(self.inventoryFilename, self.physicalCluster, hostCount, vmsPerHost)
        
        # then get expected content in the inventory file
        actualContent = open(self.inventoryFilename, 'r').read()
        expectedContent = open('resources/inventory-vm-partial-expected.txt', 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent)
        
    def testCreateVirtualInventoryWithVariables(self):
        # given
        hostCount = 3
        vmsPerHost = 2
        inventoryVars = {'vmCount' : '6', 'deploymentType' : 'Torque'}
        
        # when
        self.allVMDetails.createVirtualInventory(self.inventoryFilename, 
                                                 self.physicalCluster, hostCount, 
                                                 vmsPerHost, inventoryVars)
        
        # then get expected content in the inventory file
        actualContent = open(self.inventoryFilename, 'r').read()
        expectedContent = open('resources/inventory-vm-vars-expected.txt', 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent)

if __name__ == "__main__":
    unittest.main()
