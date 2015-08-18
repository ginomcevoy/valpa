import unittest
from unit.test_abstract import ConsolidateAbstractTest
from integration.vespa_bootstrap import VespaWithBootstrapAbstractTest
from consolidate import analyzer
import os
import warnings

class AnalyzerTest(VespaWithBootstrapAbstractTest, ConsolidateAbstractTest):
    """ Integration tests for consolidate.analyzer.
    
    The config for the consolidation is read from test parameters
    using the bootstrapper.
    """

    def setUp(self):
        # load configuration for consolidation, set up consolidate input 
        VespaWithBootstrapAbstractTest.setUp(self)
        ConsolidateAbstractTest.setUp(self)
        
    def testGetAppMetrics(self):
        """ Test for getAppMetrics(relevantConfig, configDir) 
        
        Tests the loading of the Parpac external module to read application-specific
        metrics. Scans a directory containing two experiments and aggregates the metrics.
        
        """
        
        # given
        consolidateConfig = self.bootstrap.getConsolidateConfig('parpac')
        configDir = 'resources/consolidate/arriving/parpac/nc4-cpv2-idf0-psBAL_ONE/968f3b98fcab1bc5ae27a8d17a88be0c3a5ff9339b54a958d23957ba51272f9c/'
        
        # when
        appMetrics = analyzer.getAppMetrics(consolidateConfig, configDir)
        
        # then
        #122.12;3.197;1.909
        #122.2;3.195;1.908
        self.assertEqual(len(appMetrics), 3)
        self.assertEqual(appMetrics['appTime'], [122.12, 122.2])
        self.assertEqual(appMetrics['fluidRate'], [3.197, 3.195])
        self.assertEqual(appMetrics['floatRate'], [1.909, 1.908])
        
    def testAnalyzeWithoutCustomMetrics(self):
        # given
        noCustomConfig = self.bootstrap.getConsolidateConfig('parpac-nocustom')
        metricsFilename = noCustomConfig.consolidateParams['consolidate_metrics_same']
        
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            
            # when analyzing experiments without a custom reader for
            # application-specific metrics, a warning will be triggered
            # (User module not loaded for parpac-nocustom)
            analyzer.analyze(noCustomConfig, appName='parpac-nocustom', 
                         consolidateKey='nocustom', override=True)
            
            # then verify warnings (two experiments means two warnings)
            assert len(w) == 2
            assert issubclass(w[-1].category, UserWarning)
            assert "User module not loaded" in str(w[-1].message)

        # then verify that consolidated CSV has been created in each config
        config1 = os.path.join(self.consolidateDir, 'parpac-nocustom/someExp1/someConfig1')
        metrics1 = os.path.join(config1, metricsFilename)
        self.assertFileContentEqual(metrics1, 'resources/consolidate/parpac-nocustom1.csv')
        
        config2 = os.path.join(self.consolidateDir, 'parpac-nocustom/someExp2/someConfig2')
        metrics2 = os.path.join(config2, metricsFilename)
        self.assertFileContentEqual(metrics2, 'resources/consolidate/parpac-nocustom2.csv')
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
