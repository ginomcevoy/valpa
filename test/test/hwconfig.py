'''
Created on Oct 13, 2013

@author: giacomo
'''

from config import hwconfig

import unittest

class GetHardwareInfoTest (unittest.TestCase):

    def testHardwareInfo(self):
        hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')

        # hardware
        specs = hwInfo.getHwSpecs()
        self.failUnlessEqual(specs['cores'], 12, 'cores wrong')
        self.failUnlessEqual(specs['sockets'], 2, 'sockets wrong')
        self.failUnlessEqual(specs['mem'], 24, 'mem wrong')

        # nodes
        self.failUnlessEqual(hwInfo.nodePrefix, 'node', 'prefix wrong')
        self.failUnlessEqual(hwInfo.nodeZeros, 3, 'nodeZeros wrong')
        self.failUnlessEqual(hwInfo.nodeFirst, 82, 'nodeFirst wrong')
        
#def suite():
#    suite = unittest.TestSuite()
#   suite.addTest (GetHardwareInfoTest())
#   return suite

#if __name__ == '__main__':
#    runner = unittest.TextTestRunner()
#    runner.run(suite())


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()