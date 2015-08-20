'''
Created on Aug 31, 2014

@author: giacomo
'''
import sys
from datetime import date

from .scenariogen import SimpleScenarioGenerator
from .constraint import SimpleClusterGenerationSpecification,\
    SimpleClusterConstraint
from .appgen import ApplicationGenerationSpecification
from core import config_hw, config_vespa
import os

class SimplePlacementScenarioGenerator():
    '''
    Generates XML based on scenarios that matches all possible cluster placements
    for a given virtual cluster size. Optionally, the number of physical machines 
    can be specified. Restricted to the DIST tuple, all pstrat values, no special
    VMM settings and no MPI pinning options (NONE)
    '''
    
    def __init__(self, vespaFilename='../config/vespa.params', hwParamFile='../config/hardware.params'):
        
        # Read Vespa configuration file
        vespaConfig = config_vespa.readVespaConfig(vespaFilename)
        self.definedDir = vespaConfig.miscParams['defined_dir']
        
        # load hardware specification
        hwInfo = config_hw.getHardwareInfo()
        hwSpecs = hwInfo.getHwSpecs()
        
        # delegate to generator
        self.scenarioGenerator = SimpleScenarioGenerator(vespaConfig.createParams, hwSpecs)
        
        # specifications are built using some user input
        self.clusterSpecification = SimpleClusterGenerationSpecification(hwSpecs)
        self.physicalMachinesTuple = None
        
    def forApplication(self, appName, runs):
        self.appName = appName
        self.applicationSpecification = ApplicationGenerationSpecification(appName, runs)
        
    def forClusterSize(self, nc):
        self.nc = nc
        self.forClusterSizes([nc, ])
        
    def forClusterSizes(self, ncs):
        ncConstraint = SimpleClusterConstraint()
        ncConstraint.constrainNc(ncs)
        self.clusterSpecification = self.clusterSpecification.constrainWith(ncConstraint)
        
    def limitedToPhysicalMachines(self, physicalMachinesTuple):
        self.physicalMachinesTuple = physicalMachinesTuple
        physicalMachinesConstraint = SimpleClusterConstraint()
        physicalMachinesConstraint.constrainPhysicalMachines(physicalMachinesTuple)
        self.clusterSpecification = self.clusterSpecification.constrainWith(physicalMachinesConstraint)
        
    def produceXML(self, xmlName=None, xmlPath=None):
        # default XML name
        if xmlName is None:
            xmlName = self.appName + "-" + self.nc
            if self.physicalMachinesTuple is not None:
                for physicalMachines in self.physicalMachinesTuple:
                    xmlName = xmlName + "_" + physicalMachines
                    
        # default XML path
        if xmlPath is None:
            xmlPath = self.definedDir
        if not os.path.exists(xmlPath):
            os.makedirs(xmlPath)
        
        # call scenario generator
        self.scenarioGenerator.withApplicationSpecification(self.applicationSpecification)
        self.scenarioGenerator.withClusterSpecification(self.clusterSpecification)
        self.scenarioGenerator.withXML(xmlPath, xmlName)
        self.scenarioGenerator.produceXML()
        xmlFile = os.path.join(xmlPath, xmlName)
        print(xmlFile)
        
if __name__ == '__main__':
    
    # check input
    if len(sys.argv) < 4:
        raise ValueError("call: placementgen <appName> <runs> <nc> [pmCount1, pmCount2, ...]")

    # parse arguments
    appName = sys.argv[1]
    runs = int(sys.argv[2])
    nc = int(sys.argv[3])
    
    if len(sys.argv) > 4:
        pmCounts = sys.argv[4:]
        pmCounts = [int(i) for i in pmCounts]
    else:
        pmCounts = None
        
    # call generator
    scenarioGenerator = SimplePlacementScenarioGenerator()
    scenarioGenerator.forApplication(appName, runs)
    scenarioGenerator.forClusterSize(nc)
    if pmCounts is not None:
        scenarioGenerator.limitedToPhysicalMachines(pmCounts)
        
    # default xml name
    today = date.today().isoformat()    
    xmlName = ''.join((appName,'_placement_',str(nc), '_', today, '.xml')) 
    scenarioGenerator.produceXML(xmlName)
