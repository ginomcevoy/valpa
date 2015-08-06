import unittest
from unit.test_abstract import ParpacAbstractTest
from integration.vespa_bootstrap import VespaWithBootstrapAbstractTest
from consolidate import analyzer

class AnalyzerTest(VespaWithBootstrapAbstractTest):
    """ Integration tests for consolidate.analyzer.
    
    The config for the consolidation is read from test parameters
    using the bootstrapper.
    """

    def setUp(self):
        # load configuration for consolidation, set up plugin for Parpac 
        VespaWithBootstrapAbstractTest.setUp(self)
        self.consolidateConfig = self.bootstrap.getConsolidateConfig('parpac')
        
    def testGetAppMetrics(self):
        """ Test for getAppMetrics(relevantConfig, configDir) 
        
        Tests the loading of the Parpac external module to read application-specific
        metrics. Scans a directory containing two experiments and aggregates the metrics.
        
        """
        
        # given
        configDir = 'resources/datagen/arriving/parpac/nc4-cpv2-idf0-psBAL_ONE/968f3b98fcab1bc5ae27a8d17a88be0c3a5ff9339b54a958d23957ba51272f9c/'
        
        # when
        appMetrics = analyzer.getAppMetrics(self.consolidateConfig, configDir)
        
        # then
        #122.12;3.197;1.909
        #122.2;3.195;1.908
        self.assertEqual(len(appMetrics), 3)
        self.assertEqual(appMetrics['appTime'], [122.12, 122.2])
        self.assertEqual(appMetrics['fluidRate'], [3.197, 3.195])
        self.assertEqual(appMetrics['floatRate'], [1.909, 1.908])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
