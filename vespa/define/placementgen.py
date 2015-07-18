'''
Created on Aug 31, 2014

@author: giacomo
'''
from autorun.scenariogen import SimpleScenarioGenerator
from autorun.constraint import SimpleClusterGenerationSpecification,\
    SimpleClusterConstraint
from autorun.appgen import ApplicationGenerationSpecification
from config import hwconfig
import sys

class SimplePlacementScenarioGenerator():
    '''
    Generates XML based on scenarios that matches all possible cluster placements
    for a given virtual cluster size. Optionally, the number of physical machines 
    can be specified. Restricted to the DIST tuple, all pstrat values, no special
    VMM settings and no MPI pinning options (NONE)
    '''
    
    def __init__(self, hwParamFile='../input/hardware.params'):
        
        # load hardware specification
        hwInfo = hwconfig.getHardwareInfo()
        hwSpecs = hwInfo.getHwSpecs()
        
        # delegate to generator
        self.scenarioGenerator = SimpleScenarioGenerator(hwSpecs)
        
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
        
    def produceXML(self, xmlName=None, xmlPath='../output/placement'):
        if xmlName is None:
            xmlName = self.appName + "-" + self.nc
            if self.physicalMachinesTuple is not None:
                for physicalMachines in self.physicalMachinesTuple:
                    xmlName = xmlName + "_" + physicalMachines
        
        # call scenario generator
        self.scenarioGenerator.withApplicationSpecification(self.applicationSpecification)
        self.scenarioGenerator.withClusterSpecification(self.clusterSpecification)
        self.scenarioGenerator.withXML(xmlPath, xmlName)
        self.scenarioGenerator.produceXML()
        
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
        
    # default values
    xmlName = appName + '-place-' + str(nc) + '.xml' 
    scenarioGenerator.produceXML(xmlName)