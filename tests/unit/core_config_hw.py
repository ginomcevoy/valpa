'''
Created on Oct 13, 2013

@author: giacomo
'''

import unittest
from unit.test_abstract import VespaAbstractTest

class GetHardwareInfoTest(VespaAbstractTest):
    
    def setUp(self):
        VespaAbstractTest.setUp(self)

    def testHardwareInfo(self):

        # hardware
        specs = self.hwSpecs
        self.failUnlessEqual(specs['cores'], 12, 'cores wrong')
        self.failUnlessEqual(specs['sockets'], 2, 'sockets wrong')
        self.failUnlessEqual(specs['mem'], 24, 'mem wrong')

    def testReadInventoryFile(self):
        nodeNames = self.nodeNames
        self.assertEqual(12, len(nodeNames))
        self.assertEqual('node082', nodeNames[0])
        self.assertEqual('node093', nodeNames[11])
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()