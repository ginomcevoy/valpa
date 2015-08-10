""" Integration test for consolidate module. """

import unittest
from consolidate import __main__
from integration.vespa_bootstrap import VespaWithBootstrapAbstractTest
from unit.test_abstract import ConsolidateAbstractTest


class ConsolidateTest(VespaWithBootstrapAbstractTest, ConsolidateAbstractTest):

    def setUp(self):
        VespaWithBootstrapAbstractTest.setUp(self)
        ConsolidateAbstractTest.setUp(self)

    def testMain(self):
        # given
        appName = 'parpac'
        consolidateConfig = self.bootstrap.getConsolidateConfig(appName)
        configVars = ('nc', 'cpv', 'idf', 'pstrat')
        consolidateKey = None
        
        # when
        __main__.consolidate(consolidateConfig, appName, configVars, consolidateKey)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()