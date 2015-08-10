import unittest
import os
from unit.test_abstract import ParpacAbstractTest, ConsolidateAbstractTest

class ReadOutputParpacTest(ParpacAbstractTest, ConsolidateAbstractTest):
    """ Unit tests for the Parpac plugin. """
    
    def setUp(self):
        ParpacAbstractTest.setUp(self)
        ConsolidateAbstractTest.setUp(self)

    def testReadMetrics(self):
        # given 
        expRelative = 'parpac/nc4-cpv2-idf0-psBAL_ONE/968f3b98fcab1bc5ae27a8d17a88be0c3a5ff9339b54a958d23957ba51272f9c/parpac-2015-07-07-18:56-001'
        expDir = os.path.join(self.consolidateDir, expRelative)
        stdoutFilename = os.path.join(expDir, 'std.out')
        stderrFilename = os.path.join(expDir, 'std.err')
        customFilename = os.path.join(expDir, 'custom.out')
        
        stdoutFile = open(stdoutFilename, 'r') 
        stderrFile = open(stderrFilename, 'r')
        customFile = open(customFilename, 'r')
                
        parpacMetrics = self.read_output.read_metrics(stdoutFile, stderrFile, expDir, customFile)
        self.assertEqual(len(parpacMetrics), 3)
        self.assertEqual(parpacMetrics['appTime'], 122.12) 
        self.assertEqual(parpacMetrics['fluidRate'], 3.197)
        self.assertEqual(parpacMetrics['floatRate'], 1.909)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()