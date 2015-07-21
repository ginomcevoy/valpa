'''
Created on Sep 30, 2014

@author: giacomo
'''
import unittest

from define.scenariogen import SimpleScenarioGenerator
from define.constraint import SimpleClusterConstraint,\
    SimpleClusterGenerationSpecification
from define.appgen import ApplicationGenerationSpecification
from core.enum import MPIBindOpt, PinningOpt
from unit.test_abstract import VespaAbstractTest

class SimpleScenarioGeneratorTest(VespaAbstractTest):
    '''
    Integration unit for SimpleScenarioGenerator, tests every step of
    generating the XML for 4 experiments (2 variations of cpv, 2 variations
    of MPIBindOpt)
    '''

    def setUp(self):
        VespaAbstractTest.setUp(self)
        
        self.scenarioGenerator = SimpleScenarioGenerator(self.hwSpecs)
        self.clusterSpecification = SimpleClusterGenerationSpecification(self.hwSpecs)

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
        applicationSpec = ApplicationGenerationSpecification('parpac', 6, [MPIBindOpt.none, MPIBindOpt.core])
        
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
        self.assertFileContentEqual(xmlFilename, 'resources/integration/scenariogen-expected.xml')
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()