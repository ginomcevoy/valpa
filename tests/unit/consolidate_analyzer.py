""" Unit tests for consolidate.analyzer module. """
import unittest
from consolidate import analyzer

class AnalyzerTest(unittest.TestCase):
    
    def setUp(self):
        self.inputDir = 'resources/datagen/arriving'
        self.parpacInputDir = self.inputDir + '/parpac'
        self.timeFilename = 'times.txt'

    def testGetTimeMetrics(self):
        # given this directory contains parpac-specific metrics
        #User    System    Ellapsed
        #227.99    16.56    122.73
        #User    System    Ellapsed
        #228.56    16.17    122.76 
        configDir = self.parpacInputDir + '/nc4-cpv2-idf0-psBAL_ONE/968f3b98fcab1bc5ae27a8d17a88be0c3a5ff9339b54a958d23957ba51272f9c'

        # when
        timeMetrics = analyzer.getTimeMetrics(configDir, self.timeFilename)
        
        # then 
        self.assertEqual(len(timeMetrics), 3)
        self.assertEqual(timeMetrics['userTime'], (227.99, 228.56))
        self.assertEqual(timeMetrics['systemTime'], (16.56, 16.17))
        self.assertEqual(timeMetrics['ellapsedTime'], (122.73, 122.76))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()