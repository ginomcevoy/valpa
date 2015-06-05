'''
Created on Nov 2, 2014

@author: giacomo
'''
import unittest
from bean.node import PhysicalNodeFactory
from config import hwconfig


class PhysicalNodeFactoryTest(unittest.TestCase):

    def setUp(self):
        hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')
        self.nodeFactory = PhysicalNodeFactory(hwInfo) 

    def testGetAllNodes(self):
        allNodes = self.nodeFactory.getAllNodes()

        self.failIf(allNodes is None)
        self.failUnlessEqual(len(allNodes.nodeTuple), 12, 'wrong length nodes')
        self.failUnlessEqual(allNodes.getNames()[0], 'node082', 'wrong first node')
        self.failUnlessEqual(allNodes.getNames()[11], 'node093', 'wrong last node')

        self.failUnlessEqual(allNodes.getNodeSuffix('node083'), '083', 'wrong node')
        self.failUnlessEqual(allNodes.getNodeSuffix('node093'), '093', 'wrong last node')
        
        self.failUnlessEqual(allNodes.getNodeIndex('node083'), 1, 'wrong indexing')
        self.failUnlessEqual(allNodes.getNodeIndex('node093'), 11, 'wrong indexing')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()