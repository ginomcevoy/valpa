'''
Created on Oct 10, 2014

@author: giacomo
'''
import unittest
from consolidate import beff
import pprint
import os


class BeffTest(unittest.TestCase):

    def setUp(self):
        self.beffFilename = 'resources/beff.plot'
        self.beffFilenames = (self.beffFilename, self.beffFilename) 
        self.singleOutputFilename = '/tmp/beff-output'
        self.twoOutputFilename = '/tmp/beff-twooutput'
        self.dataType = 'compareRingRandom'
        if os.path.exists(self.singleOutputFilename):
            os.remove(self.singleOutputFilename)

    def testSelectCompareRingRandom(self):
        
        # given manual open
        beffText = open(self.beffFilename, 'r').read()
        
        # when
        textLines = beff.selectCompareRingRandomLines(beffText)
        
        # then
        if False:
            print(textLines)
        
        self.assertEquals(textLines[0], '         1   1.957   1.971   1.985   2.013   2.081   2.136   2.026 ')

    def testBeffLinesToMatrix(self):
        
        # given line reading
        beffText = open(self.beffFilename, 'r').read()
        beffLines = beff.selectCompareRingRandomLines(beffText)
        
        # when
        beffMatrix = beff.beffLinesToMatrix(beffLines)
        
        # then
        if False:
            pprint.pprint(beffMatrix)
            
        self.assertEquals(beffMatrix[0], [1, 1.957, 1.971, 1.985, 2.013, 2.081, 2.136, 2.026])
        self.assertEquals(beffMatrix[20], [8388608, 2679.489, 2687.659, 2694.675, 2675.211, 2688.266, 2698.809, 2687.963])
        
    def testAppendExperimentData(self):
        
        # given
        experimentName = 'test1'
        expectedFilename = 'resources/beff-single.expected'
        
        # when
        beff.appendExperimentData(experimentName, self.beffFilename, self.singleOutputFilename, self.dataType)
        
        # then assert equal contents
        self.maxDiff = None
        self.assertEquals(open(self.singleOutputFilename, 'r').read(), open(expectedFilename, 'r').read())
        
    def testFindDataColumnCount(self): 
        columnCount = beff.findDataColumnCount(self.beffFilenames, self.dataType)
        self.assertEquals(columnCount, 7) 
        
    def testProcessExperiments(self):
        # given
        experimentNames = ('test1', 'test2')
        expectedFilename = 'resources/beff-two.expected'
         
        # when
        beff.processExperiments(experimentNames, self.beffFilenames, self.twoOutputFilename, self.dataType)
        
        # then assert equal contents
        self.maxDiff = None
        self.assertEquals(open(self.twoOutputFilename, 'r').read(), open(expectedFilename, 'r').read())
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()