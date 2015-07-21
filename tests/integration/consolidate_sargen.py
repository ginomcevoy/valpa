'''
Created on Jul 9, 2015

@author: giacomo
'''
import os
import unittest

from consolidate import sargen
from unit.test_abstract import VespaAbstractTest

class SargenTest(VespaAbstractTest):
    '''
    Unit test for datagen.sargen. Calls the analyzeSingleConfig function to 
    verify the output of a single call to sargen-metrics.R.
    '''
    def setUp(self):
        VespaAbstractTest.setUp(self)
        
        # create output directories
        self.configOutputDir =  '/tmp/vespa/test/datagen/parpac/cfg1/'
        if not os.path.exists(self.configOutputDir):
            os.makedirs(self.configOutputDir)
        

    def testName(self):
        # given
        baseDir = 'resources/datagen/arriving/parpac/nc4-cpv2-idf2-psNONE/'
        configDirName = 'e9b01aa4132532a40308d51c7ba99e6048cdcafd3a193af72d6619bdaa5d5980'
        configDir = baseDir + configDirName
        configDir = os.path.abspath(configDir)
        phycores = '12'
        
        verifyDir = 'resources/datagen/analyzed/parpac/cfg1/'
        expectedHeader = verifyDir + 'header.txt'
        expectedFile1 = verifyDir + 'exc001.csv'
        expectedFile2 = verifyDir + 'exc002.csv'
        
        # when
        sargen.analyzeSingleConfig(configDir, phycores, self.configOutputDir)
        
        # then verify outputs: 2 CSV files and 1 header file
        testOutputHeader = self.configOutputDir + 'header.txt'
        testOutputFile1 = self.configOutputDir + 'exc001.csv'
        testOutputFile2 = self.configOutputDir + 'exc002.csv'
        self.assertFileContentEqual(testOutputHeader, expectedHeader)
        self.assertFileContentEqual(testOutputFile1, expectedFile1)
        self.assertFileContentEqual(testOutputFile2, expectedFile2)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()