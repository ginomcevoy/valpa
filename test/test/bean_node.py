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
        self.subsetNames = ('node084', 'node086', 'node088') 

    def testGetAllNodes(self):
        allNodes = self.nodeFactory.getAllNodes()

        self.failIf(allNodes is None)
        self.assertEqual(len(allNodes.nodeTuple), 12, 'wrong length nodes')
        self.assertEqual(allNodes.getNames()[0], 'node082', 'wrong first node')
        self.assertEqual(allNodes.getNames()[11], 'node093', 'wrong last node')

        self.assertEqual(allNodes.getNodeSuffix('node083'), '083', 'wrong node')
        self.assertEqual(allNodes.getNodeSuffix('node093'), '093', 'wrong last node')
        
        self.assertEqual(allNodes.getNodeIndex('node083'), 1, 'wrong indexing')
        self.assertEqual(allNodes.getNodeIndex('node093'), 11, 'wrong indexing')
        
    def testGetSubset(self):
        # given
        allNodes = self.nodeFactory.getAllNodes()
        
        # when select a subset
        nodeSubset = allNodes.getSubset(self.subsetNames)
        
        # the
        self.assertEqual(len(nodeSubset.getNames()), 3, 'wrong size') 
        self.assertEqual(nodeSubset.getNodeIndex('node084'), 2, 'wrong indexing')
        self.assertEqual(nodeSubset.getNodeIndex('node086'), 4, 'wrong indexing')
        self.assertEqual(nodeSubset.getNodeIndex('node088'), 6, 'wrong indexing')
        
    def testToFile(self):
        # given 
        allNodes = self.nodeFactory.getAllNodes()
        filename = '/tmp/vespa-allnodes.txt'
        expectedContent = open('resources/nodes-tofile-expected.txt', 'r').read()
        
        # when representing as file
        allNodes.toFile(filename)
        
        # verify content
        self.maxDiff = None
        self.assertEquals(open(filename, 'r').read(), expectedContent)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()