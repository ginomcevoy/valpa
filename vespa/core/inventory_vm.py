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
    
    # Bootstrap Vespa with default config and get dependencies
    bootstrap.doBootstrap()
    bootstrapper = bootstrap.getInstance()
    
    physicalCluster = bootstrapper.getPhysicalCluster()
    allVMDetails = bootstrapper.getAllVMDetails()
    
    # Build a subset of the possible VMs that represent the request
    # Get the nodes that fit the hostCount, then get vmsPerHost VMs
    # for each of these hosts
    vmNames = []
    subsetNodes = physicalCluster.getSubsetForHostCount(hostCount)
    for nodeName in subsetNodes.nodeDict.keys():
        node = subsetNodes.getNode(nodeName)
        vmForNode = allVMDetails.getVMNamesForNode(node)
        vmNames.extend(vmForNode[0:vmsPerHost])
    vmNames = sorted(vmNames)
    subsetVMs = allVMDetails.getSubset(vmNames)
    
    # produce inventory file and output filename
    subsetVMs.createVirtualInventory(inventoryFilename)
    print(inventoryFilename)
