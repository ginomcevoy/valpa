'''
Created on Aug 24, 2014

Unit test for config.shellparams

@author: giacomo
'''
import unittest

from config.shellparams import ShellParameters
import pprint

class ShellParametersTest(unittest.TestCase):

    def setUp(self):
        self.desiredFilename = '/tmp/valpa-shell-params'
        self.expectedOutput = 'resources/valpa-shell-params-expected'
        
        self.valpaParamFile = 'resources/valpa.params'
        self.hwParamFile = 'resources/hardware.params'
        
        self.shellParams = ShellParameters()

    def testCreateParamsTemplate(self):
        # load VALPA parameters
        self.shellParams.loadValpaParams(self.valpaParamFile, self.hwParamFile)
        
        # call function        
        paramFilename = self.shellParams.createParamsFromTemplate(self.desiredFilename)
        
        if False:
            pprint.pprint(self.shellParams.allParams)
        
        # assertions: filename and contents
        self.maxDiff = None
        self.assertEqual(paramFilename, self.desiredFilename, 'filename wrong')
        self.assertEquals(open(paramFilename, 'r').read(), open(self.expectedOutput, 'r').read())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreateParamsTemplate']
    unittest.main()