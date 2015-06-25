'''
Created on Aug 24, 2014

Unit test for config.shellparams

@author: giacomo
'''
import difflib
import pprint
import unittest

from config.shellparams import ShellParameters


class ShellParametersTest(unittest.TestCase):

    def setUp(self):
        self.desiredFilename = '/tmp/vespa-shell-params'
        self.expectedOutput = 'resources/vespa-shell-params-expected'
        
        self.vespaParamFile = 'resources/vespa.params'
        self.hwParamFile = 'resources/hardware.params'
        
        self.shellParams = ShellParameters()

    def testCreateParamsTemplate(self):
        # load Vespa parameters
        self.shellParams.loadVespaParams(self.vespaParamFile, self.hwParamFile)
        
        # call function        
        paramFilename = self.shellParams.createParamsFromTemplate(self.desiredFilename)
        
        if False:
            pprint.pprint(self.shellParams.allParams)
        
        # assertions: filename and contents
        self.assertEqual(paramFilename, self.desiredFilename, 'filename wrong')
        actualContent = open(paramFilename, 'r').read()
        expectedContent = open(self.expectedOutput, 'r').read()
        self.assertMultiLineEqual(actualContent, expectedContent)
        
    def assertMultiLineEqual(self, first, second, msg=None):
        '''
        Assert that two multi-line strings are equal.
        If they aren't, show a nice diff.
        '''
        self.assertTrue(isinstance(first, str),
                'First argument is not a string')
        self.assertTrue(isinstance(second, str),
                'Second argument is not a string')

        if first != second:
            message = ''.join(difflib.ndiff(first.splitlines(True),
                                                second.splitlines(True)))
            if msg:
                message += " : " + msg
            self.fail("Multi-line strings are unequal:\n" + message)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testCreateParamsTemplate']
    unittest.main()