'''
Created on Sep 30, 2014

@author: giacomo
'''
import unittest
from autorun.scenariogen import SimpleScenarioGenerator
from config import hwconfig
from autorun.constraint import SimpleClusterConstraint,\
    SimpleClusterGenerationSpecification
from autorun.appgen import ApplicationGenerationSpecification
from bean.enum import MPIBindOpt, PinningOpt


class SimpleScenarioGeneratorTest(unittest.TestCase):
    '''
    Integration test for SimpleScenarioGenerator, tests every step of
    generating the XML for 4 experiments (2 variations of cpv, 2 variations
    of MPIBindOpt)
    '''

    def setUp(self):
        # get stub hardware
        hwInfo = hwconfig.getHardwareInfo('resources/hardware.params')
        hwSpecs = hwInfo.getHwSpecs()
        
        self.scenarioGenerator = SimpleScenarioGenerator(hwSpecs)
        self.clusterSpecification = SimpleClusterGenerationSpecification(hwSpecs)

    def testXMLExport(self):
        
        # create cluster request with nc=2, single PM, BAL_ONE (two possible placements)
        ncConstraint = SimpleClusterConstraint()
        ncConstraint.constrainNc([2, ])
        clusterSpec = self.clusterSpecification.constrainWith(ncConstraint)
        
        singlePMConstraint = SimpleClusterConstraint()
        singlePMConstraint.constrainPhysicalMachines([1, ])
        clusterSpec = clusterSpec.constrainWith(singlePMConstraint)
        
        pstratConstraint = SimpleClusterConstraint()
        pstratConstraint.constrainPstrat([PinningOpt.BAL_ONE, ])
        clusterSpec = clusterSpec.constrainWith(pstratConstraint)
        
        # application can be deployed with two MPI options
        applicationSpec = ApplicationGenerationSpecification('parpac', 6, [MPIBindOpt.NONE, MPIBindOpt.BIND_CORE])
        
        self.scenarioGenerator.withClusterSpecification(clusterSpec)
        self.scenarioGenerator.withApplicationSpecification(applicationSpec)
        
        # create the XML
        xmlPath = 'resources/integration'
        xmlName = 'scenariogen-generated.xml'
        self.scenarioGenerator.withXML(xmlPath, xmlName)
        xmlFilename = self.scenarioGenerator.produceXML()
        
        # verify name and contents
        self.assertEquals(xmlFilename, 'resources/integration/scenariogen-generated.xml')
        self.maxDiff = None
        self.assertEqual(open(xmlFilename, 'r').read(), open('resources/integration/scenariogen-expected.xml', 'r').read())
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()