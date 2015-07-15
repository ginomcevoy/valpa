"""Unit tests for deploy.parser module. """

import unittest

from deploy import parser
from bean.enum import MPIBindOpt, PinningOpt, NetworkOpt, DiskOpt

class ParserTest(unittest.TestCase):
    
    def setUp(self):
        self.scenarioXML = 'resources/integration/two-exps.xml'

    def testName(self):
        scenarios = parser.parseScenarios(self.scenarioXML)
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
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()