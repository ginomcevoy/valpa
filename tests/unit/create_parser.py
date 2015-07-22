"""Unit tests for create.parser module. """

import unittest

from create import parser
from core.enum import MPIBindOpt, PinningOpt, NetworkOpt, DiskOpt

class ParserTest(unittest.TestCase):
    
    def setUp(self):
        self.noOptionalValues = 'resources/integration/two-exps.xml'
        self.emptyApp = 'resources/scenario/empty-app.xml'
        self.infinibandOnly = 'resources/scenario/infiniband-only.xml'

    def testNoOptionalValues(self):
        scenarios = parser.parseScenarios(self.noOptionalValues)
        self.assertEqual(len(scenarios), 2)
        
        # Verify scenario1
        scenario = scenarios[0]
        
        experiment = scenario.exps[0]
        self.assertEqual(experiment.name, 'exp1')
        self.assertEqual(experiment.trials, 1)
        
        app = experiment.app
        self.assertEqual(app.name, 'parpac')
        self.assertEqual(app.runs, 2)
        
        appTuning = app.appTuning
        self.assertEqual(appTuning.procpin, MPIBindOpt.core)
        
        cluster = experiment.cluster
        self.assertFalse(cluster.physicalMachinesOnly)
        
        # <topology nc="16" cpv="4" />
        clusterPlacement = cluster.clusterPlacement
        topology = clusterPlacement.topology
        self.assertEqual(topology.nc, 16) 
        self.assertEqual(topology.cpv, 4)
        
        # <mapping idf="8" pstrat="BAL_ONE" />
        mapping = clusterPlacement.mapping
        self.assertEqual(mapping.idf, 8)
        self.assertEqual(mapping.pinningOpt, PinningOpt.BAL_ONE)
        
        # <technology network="vhost" disk="scsi" />
        technology = cluster.technology
        self.assertEqual(technology.networkOpt, NetworkOpt.vhost)
        self.assertEqual(technology.diskOpt, DiskOpt.scsi)
        
        # Verify scenario2
        scenario = scenarios[1]
        experiment = scenario.exps[0]
        
        # <technology network="virtio" disk="virtio" />
        technology = experiment.cluster.technology
        self.assertEqual(technology.networkOpt, NetworkOpt.virtio)
        self.assertEqual(technology.diskOpt, DiskOpt.virtio)
        
        # <procpin>NONE</procpin>
        appTuning = experiment.app.appTuning
        self.assertEqual(appTuning.procpin, MPIBindOpt.none)
        
    def testEmptyApp(self):
        # given
        scenarios = parser.parseScenarios(self.emptyApp)
        self.assertEqual(len(scenarios), 1)
        scenario = scenarios[0]
        experiment = scenario.exps[0]
        
        # then no application in XML, so default should be added
        # (also no exception thrown)
        defaultApplication = parser.defaultApplication()
        self.assertEqual(experiment.app.name, defaultApplication.name)
        
    def testInfinibandOnly(self):
        # given two scenarios
        scenarios = parser.parseScenarios(self.infinibandOnly)
        self.assertEqual(len(scenarios), 2)

        # then first: technology has infinibandFlag set to True
        # other items to None
        scenario = scenarios[0]
        experiment = scenario.exps[0]
        technology = experiment.cluster.technology
        self.assertTrue(technology.infinibandFlag)
        self.assertIsNone(technology.diskOpt)
        self.assertIsNone(technology.diskOpt)
        
        # then second: technology has infinibandFlag set to False
        # other items to None
        scenario = scenarios[1]
        experiment = scenario.exps[0]
        technology = experiment.cluster.technology
        self.assertFalse(technology.infinibandFlag)
        self.assertIsNone(technology.diskOpt)
        self.assertIsNone(technology.diskOpt)
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()