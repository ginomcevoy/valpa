'''
Created on Jan 15, 2014

@author: giacomo
'''

import sys

from core.experiment import Application
from .phyexpgen import PhysicalExperimentGenerator
import bootstrap


if __name__ == '__main__':
    
    # verify input
    if len(sys.argv) < 2:
        raise ValueError("argument: <outputPath>")
    outputPath = sys.argv[1] 
    
    # Generate experiment XMLs for Parpac physical
    appInfo = Application('parpac', 2, '')
    
    # Bootstrap Vespa with default config
    bootstrap.doBootstrap(True)
    bootstrapper = bootstrap.getInstance()
    
    physicalCluster = bootstrapper.getPhysicalCluster()
    
    # Placement strategies for nc = 12,24,48
    placementGen = PhysicalExperimentGenerator(physicalCluster)
    placementGen.withNCs([12,24,48])\
                .withCPVs([1, 2, 4, 6, 12])\
                .withMPIBinds()\
                .generateCombinations()
    
    placementGen.generateXMLs(appInfo, outputPath)
