'''
Created on Jun 23, 2015

@author: giacomo
'''

import sys

import bootstrap

if __name__ == "__main__":
    # verify input
    if len(sys.argv) < 3:
        raise ValueError("call: node <hostCount> <inventoryFilename>")
    hostCount = int(sys.argv[1])
    inventoryFilename = sys.argv[2]
    
    # Bootstrap Vespa with default config, get dependencies
    bootstrap.doBootstrap()
    bootstrapper = bootstrap.getInstance()
    
    physicalCluster = bootstrapper.getPhysicalCluster()
    clusterSubset = physicalCluster.getSubsetForHostCount(hostCount)
    allVMDetails = bootstrapper.getAllVMDetails()
    
    # produce inventory file and output filename
    clusterSubset.createInventory(inventoryFilename, allVMDetails)
    print(inventoryFilename)
