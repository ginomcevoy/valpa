'''
Created on Jan 15, 2014

@author: giacomo
'''

from bean.experiment import Application
from autorun.expgen import ExperimentGenerator
from bean.enum import PinningOpt

if __name__ == '__main__':
    # Call from src directory!
    
    # Generate experiment XMLs for cavity3d benchmark
    # scalability XML: cpv = 1, df = min, nc = 1, 2
    # set cpv, df manually
    hwSpecs = {'cores' : 12}
    appInfo = Application('cavity3d', 10, '300')
    
    # Placement strategies for nc = 64
    placementGenPower2 = ExperimentGenerator(hwSpecs)
    nc = 64
    idfs = {'1' : (8,), 
            '2' : (8,),
            '4' : (8,),
            '8' : (8,),}
    placementGenPower2.combinations = []
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGenPower2.combinations.append((nc, cpv, idf))
            
    # Placement strategies for nc = 32
    nc = 32
    idfs = {'1' : (8, 4), 
            '2' : (8, 4),
            '4' : (8, 4),
            '8' : (8,),}
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGenPower2.combinations.append((nc, cpv, idf))
            
    # Placement strategies for nc = 16
    nc = 16
    idfs = {'1' : (8, 4, 2), 
            '2' : (8, 4, 2),
            '4' : (8, 4),
            '8' : (8,),}
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGenPower2.combinations.append((nc, cpv, idf))        
            
    # Placement strategies for nc = 8
    nc = 8
    idfs = {'1' : (8, 4, 2, 1), 
            '2' : (8, 4, 2),
            '4' : (8, 4),
            '8' : (8,),}
    
    # add each combination
    for cpv in idfs.keys():
        for idf in idfs.get(cpv):
            placementGenPower2.combinations.append((nc, cpv, idf))        
    
    # process combinations and generate XMLs
    placementGenPower2.withPstratValues((PinningOpt.BAL_ONE, PinningOpt.NONE))
    placementGenPower2.withPinCores((False,))
    placementGenPower2.groupCombinations()
    placementGenPower2.generateXMLs(appInfo, '../output/autorun/cavity3d-power2')
    
    
    