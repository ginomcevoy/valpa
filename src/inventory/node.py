'''
Created on Jun 23, 2015

@author: giacomo
'''

import sys

from start import bootstrap

if __name__ == "__main__":
    # verify input
    if len(sys.argv) < 2:
        raise ValueError("call: node <inventoryFilename>")
    inventoryFilename = sys.argv[1]
    
    # Bootstrap Vespa with default config, get dependencies
    bootstrap.doBootstrap()
    bootstrapper = bootstrap.getInstance()
    
    physicalCluster = bootstrapper.getPhysicalCluster()
    allVMDetails = bootstrapper.getAllVMDetails()
    
    # produce inventory file and output filename
    physicalCluster.createInventory(inventoryFilename, allVMDetails)
    print(inventoryFilename)
