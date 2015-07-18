'''
Created on Jan 15, 2014

@author: giacomo
'''

from core.experiment import Application
from .scenariogen import StandaloneExperimentGenerator
from core.enum import PinningOpt

if __name__ == '__main__':
    # Call from src directory!
    
    # Generate experiment XMLs for cavity3d benchmark
    # scalability XML: cpv = 1, df = min, nc = 1, 2
    # set cpv, df manually
    hwSpecs = {'cores' : 12}
    appInfo = Application('cavity3d', 10, '300')
    scalabilityGen = StandaloneExperimentGenerator(hwSpecs)
    scalabilityGen.cpvs = (1,)
    scalabilityGen.idfs = {'1' : (12,)}

    # scalability points    
    machines = (1, 2, 3, 4, 6, 8, 10, 12)
    scalabilityGen.withMachines(machines)
    scalabilityGen.withPstratValues((PinningOpt.BAL_ONE,))
    scalabilityGen.withPinCores((False,))
    scalabilityGen.generateXMLs(appInfo, '../output/autorun/cavity3d-scalability')
    
    # Generate experiments for placement strategies - manual generation
    # Placement strategies for nc = 12
    placementGen12 = StandaloneExperimentGenerator(hwSpecs)
    nc = 12
    idfs = {'1' : (12, 6, 4, 3, 2, 1), 
            '2' : (12, 6, 4, 2),
            '4' : (12, 4),
            '6' : (12, 6),
            '12': (12,)}
    placementGen12.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen12.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen12.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen12.withPinCores((False,))
    placementGen12.groupCombinations()
    placementGen12.generateXMLs(appInfo, '../output/autorun/cavity3d-place12')
    
    # Placement strategies for nc = 24
    placementGen24 = StandaloneExperimentGenerator(hwSpecs)
    nc = 24
    idfs = {'1' : (12, 8, 6, 4, 3, 2), 
            '2' : (12, 8, 6, 4,    2),
            '4' : (12, 8,    4      ),
            '6' : (12,    6),
            '8' : (8,),
            '12': (12,)}
    placementGen24.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen24.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen24.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen24.withPinCores((False,))
    placementGen24.groupCombinations()
    placementGen24.generateXMLs(appInfo, '../output/autorun/cavity3d-place24')
        
    # Placement strategies for nc = 36
    placementGen36 = StandaloneExperimentGenerator(hwSpecs)
    nc = 36
    idfs = {'1' : (12, 6, 4, 3), 
            '2' : (12, 6, 4),
            '4' : (12, 6, 4),
            '6' : (12, 6),
            '12': (12,)}
    placementGen36.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen36.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen36.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen36.withPinCores((False,))
    placementGen36.groupCombinations()
    placementGen36.generateXMLs(appInfo, '../output/autorun/cavity3d-place36')
        
    # Placement strategies for nc = 48
    placementGen48 = StandaloneExperimentGenerator(hwSpecs)
    nc = 48
    idfs = {'1' : (12, 8, 6, 4), 
            '2' : (12, 8, 6, 4),
            '4' : (12, 8, 4),
            '6' : (12, 6),
            '8' : (8,),
            '12': (12,)}
    placementGen48.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen48.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen48.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen48.withPinCores((False,))
    placementGen48.groupCombinations()
    placementGen48.generateXMLs(appInfo, '../output/autorun/cavity3d-place48')
    
    # Placement strategies for nc = 60 (12, 6)
    placementGen60 = StandaloneExperimentGenerator(hwSpecs)
    nc = 60
    idfs = {'1' : (12, 6), 
            '2' : (12, 6),
            '4' : (12,),
            '6' : (12, 6),
            '12': (12,)}
    placementGen60.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen60.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen60.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen60.withPinCores((False,))
    placementGen60.groupCombinations()
    placementGen60.generateXMLs(appInfo, '../output/autorun/cavity3d-place60')
    
    # Placement strategies for nc = 72
    placementGen72 = StandaloneExperimentGenerator(hwSpecs)
    nc = 72
    idfs = {'1' : (12, 8, 6), 
            '2' : (12, 8, 6),
            '4' : (12, 8),
            '6' : (12, 6),
            '8' : (8,),
            '12': (12,)}
    placementGen72.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen72.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen72.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen72.withPinCores((False,))
    placementGen72.groupCombinations()
    placementGen72.generateXMLs(appInfo, '../output/autorun/cavity3d-place72')
    
    # Placement strategies for nc = 84
    placementGen84 = StandaloneExperimentGenerator(hwSpecs)
    nc = 84
    idfs = {'1' : (12, 7), 
            '2' : (12,),
            '4' : (12,),
            '6' : (12,),
            '12': (12,)}
    placementGen84.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen84.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen84.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen84.withPinCores((False,))
    placementGen84.groupCombinations()
    placementGen84.generateXMLs(appInfo, '../output/autorun/cavity3d-place84')
    
    # Placement strategies for nc = 96
    placementGen96 = StandaloneExperimentGenerator(hwSpecs)
    nc = 96
    idfs = {'1' : (12, 8), 
            '2' : (12, 8),
            '4' : (12, 8),
            '6' : (12,),
            '8' : (8,),
            '12': (12,)}
    placementGen96.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen96.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen96.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen96.withPinCores((False,))
    placementGen96.groupCombinations()
    placementGen96.generateXMLs(appInfo, '../output/autorun/cavity3d-place96')
    
    # Placement strategies for nc = 108
    placementGen108 = StandaloneExperimentGenerator(hwSpecs)
    nc = 108
    idfs = {'1' : (12,), 
            '2' : (12,),
            '4' : (12,),
            '6' : (12,),
            '12': (12,)}
    placementGen108.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen108.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen108.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen108.withPinCores((False,))
    placementGen108.groupCombinations()
    placementGen108.generateXMLs(appInfo, '../output/autorun/cavity3d-place108')
    
    # Placement strategies for nc = 120
    placementGen120 = StandaloneExperimentGenerator(hwSpecs)
    nc = 120
    idfs = {'1' : (12,), 
            '2' : (12,),
            '4' : (12,),
            '6' : (12,),
            '12': (12,)}
    placementGen120.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGen120.combinations.append((nc, cpv, idf))
            
    # process combinations and generate XMLs
    placementGen120.withPstratValues((PinningOpt.BAL_ONE,))
    placementGen120.withPinCores((False,))
    placementGen120.groupCombinations()
    placementGen120.generateXMLs(appInfo, '../output/autorun/cavity3d-place120')
    
    
    