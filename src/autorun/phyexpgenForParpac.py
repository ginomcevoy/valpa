'''
Created on Jan 15, 2014

@author: giacomo
'''

from bean.experiment import Application
from autorun.phyexpgen import PhysicalExperimentGenerator
from config import hwconfig

if __name__ == '__main__':
    # Call from src directory!
    hwInfo = hwconfig.getHardwareInfo()
    allNodes = hwInfo.getAllNodes()
    
    # Generate experiment XMLs for Parpac physical
    appInfo = Application('parpac', 2, '')
    
    # Placement strategies for nc = 12,24,48
    placementGen = PhysicalExperimentGenerator(allNodes)
    placementGen.withNCs([12,24,48])\
                .withCPVs([1, 2, 4, 6, 12])\
                .withMPIBinds()\
                .generateCombinations()
    
    placementGen.generateXMLs(appInfo, '../output/autorun/parpac-physical')
