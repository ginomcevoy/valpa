'''
Created on Aug 24, 2014

Unit unit for config.shellparams

@author: giacomo
'''
import pprint
import unittest

from core.shellparams import ShellParameters
from integration.root_bootstrap import VespaWithBootstrapAbstractTest


class ShellParametersTest(VespaWithBootstrapAbstractTest):

    def setUp(self):
        # load fixed Vespa settings
        VespaWithBootstrapAbstractTest.setUp(self)
        
        self.desiredFilename = '/tmp/vespa-shell-params'
        self.expectedOutput = 'resources/vespa-shell-params-expected'
        
        self.shellParams = ShellParameters(self.bootstrap)

    def testCreateParamsTemplate(self):
        
        # call function        
        paramFilename = self.shellParams.createParamsFromTemplate(self.desiredFilename)
        
        if False:
            pprint.pprint(self.shellParams.allParams)
        
        # assertions: filename and contents
        self.assertEqual(paramFilename, self.desiredFilename, 'filename wrong')
        actualContent = open(paramFilename, 'r').read()
        expectedContent = open(self.expectedOutput, 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreateParamsTemplate']
    unittest.main()