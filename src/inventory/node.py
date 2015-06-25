'''
Created on Jun 23, 2015

@author: giacomo
'''

import sys

from start import bootstrap

if __name__ == "__main__":
    # verify input
    if len(sys.argv) < 3:
        raise ValueError("call: node <inventoryFilename>")
    inventoryFilename = sys.argv[1]
    
    # Bootstrap Vespa with default config
    bootstrap.doBootstrap()
    bootstrapper = bootstrap.getInstance()
    
    # execute all experiments in xml
    physicalCluster = bootstrapper.getPhysicalCluster() 
    physicalCluster.createInventory(inventoryFilename)
