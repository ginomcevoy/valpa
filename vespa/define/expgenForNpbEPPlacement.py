'''
Created on Jan 15, 2014

@author: giacomo
'''

from core.experiment import Application
from core.enum import PinningOpt
from .expgen import ExperimentGenerator

if __name__ == '__main__':
    # Call from src directory!
    
    # Generate experiment XMLs for NPB EP benchmark, combinations of nc=48
    hwSpecs = {'cores' : 12}
    appInfo = Application('npb-ep', 10, '')
    
    # Placement strategies for nc = 48
    placementGen48 = ExperimentGenerator(hwSpecs)
    nc = 48
    idfs = {'1' : (12, 8, 6, 4), 
            '2' : (12, 8, 6, 4),
            '4' : (12, 8, 4),
            '6' : (6,),
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
    placementGen48.generateXMLs(appInfo, '../output/autorun/npb-ep-place48')
    