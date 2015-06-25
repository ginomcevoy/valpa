'''
Created on Jun 25, 2015

@author: giacomo
'''

import sys

from start import bootstrap

if __name__ == "__main__":
    # verify input
    if len(sys.argv) < 4:
        raise ValueError("call: vm <hostCount> <vmsPerHost> <inventoryFilename>")
    hostCount = int(sys.argv[1])
    vmsPerHost = int(sys.argv[2])
    inventoryFilename = sys.argv[3]
    
    # Bootstrap Vespa with default config, get dependencies
    bootstrap.doBootstrap()
    bootstrapper = bootstrap.getInstance()
    
    physicalCluster = bootstrapper.getPhysicalCluster()
    allVMDetails = bootstrapper.getAllVMDetails()
    
    # produce inventory file and output filename
    allVMDetails.createVirtualInventory(inventoryFilename, physicalCluster, hostCount, vmsPerHost)
    print(inventoryFilename)
