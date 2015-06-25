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
    
    def testCreateInventory(self):
        # when
        self.allVMDetails.createInventory(self.inventoryFilename, self.physicalCluster)
        
        # then get expected content in the inventory file
        actualContent = open(self.inventoryFilename, 'r').read()
        expectedContent = open('resources/inventory-vm-expected.txt', 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent, 'VM inventory')

if __name__ == "__main__":
    unittest.main()