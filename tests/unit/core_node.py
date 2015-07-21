'''
Created on Nov 2, 2014

@author: giacomo
'''
import unittest

from core.physical import PhysicalNodeFactory
from unit.test_abstract import VespaAbstractTest


class PhysicalNodeFactoryTest(VespaAbstractTest):

    def setUp(self):
        VespaAbstractTest.setUp(self)
        self.nodeFactory = PhysicalNodeFactory(self.hwInfo)
        self.subsetNames = ('node084', 'node086', 'node088') 

    def testGetAllNodes(self):
        allNodes = self.nodeFactory.getAllNodes()

        self.failIf(allNodes is None)
        self.assertEqual(len(allNodes), 12, 'wrong length nodes')
        
        self.assertEqual(allNodes.nodeNames[0], 'node082', 'wrong first node')
        self.assertEqual(allNodes.nodeNames[11], 'node093', 'wrong last node')
        
        node083 = allNodes.getNode('node083')
        node093 = allNodes.getNode('node093')

        self.assertEqual(node083.suffix, '083', 'wrong suffix')
        self.assertEqual(node093.suffix, '093', 'wrong suffix')
        
        self.assertEqual(node083.index, 1, 'wrong index')
        self.assertEqual(node093.index, 11, 'wrong index')
        
    def testGetSubset(self):
        # given
        allNodes = self.nodeFactory.getAllNodes()
        
        # when select a subset
        nodeSubset = allNodes.getSubset(self.subsetNames)
        
        # the
        self.assertEqual(len(nodeSubset), 3, 'wrong size')
        
        self.assertEqual(nodeSubset.getNode('node084').index, 2, 'wrong indexing')
        self.assertEqual(nodeSubset.getNode('node086').index, 4, 'wrong indexing')
        self.assertEqual(nodeSubset.getNode('node088').index, 6, 'wrong indexing')
        
    def testToFile(self):
        # given 
        allNodes = self.nodeFactory.getAllNodes()
        filename = '/tmp/vespa-allnodes.txt'
        
        # when representing as file
        allNodes.toFile(filename)
        
        # verify content
        self.assertFileContentEqual(filename, 'resources/nodes-tofile-expected.txt')
        
    def testFindNumberSuffix(self):
        nodeName = 'node083'
        suffix = self.nodeFactory.findNumberSuffix(nodeName)
        self.assertEqual(suffix, '083')
        
    def testIteration(self):
        # given a subset
        allNodes = self.nodeFactory.getAllNodes()
        nodeSubset = allNodes.getSubset(self.subsetNames)
        
        # iterate and collect names
        gathered = []
        for node in nodeSubset:
            gathered.append(node.name)
        
        self.assertEqual(tuple(gathered), self.subsetNames)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()