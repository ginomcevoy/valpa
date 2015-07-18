'''
Created on Jan 15, 2014

@author: giacomo
'''

from core.experiment import Application
from .expgen import ExperimentGenerator, NPBExecutableGenerator

if __name__ == '__main__':
    # Call from src directory!
    
    # Generate experiment XMLs for NPB-EP benchmark
    # up to 12 machines, cpv = {1, 2, 4, 6, 8, 12} (300 * 5 DIST values)
    hwSpecs = {'cores' : 12}
    appInfo = Application('npb-ep', 10, '')
    cpvs = (1, 2, 4, 6, 8, 12)
    
    scalabilityGen = ExperimentGenerator(hwSpecs)
    scalabilityGen.withCpvValues(cpvs)
    scalabilityGen.withMachines((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12))
    scalabilityGen.withPstratValues()
    scalabilityGen.withPinCores()
    scalabilityGen.generateXMLs(appInfo, 'autorun/generated')
    
    # Generate suite files for NPB EP
    execGen = NPBExecutableGenerator(hwSpecs)
    coreSet = execGen.produceCoreSet(cpvs, 12)
    execGen.writeSuiteFile(coreSet, 'autorun/generated/suite.def', 'ep', 'D')