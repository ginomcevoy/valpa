'''
Created on Jun 26, 2015

@author: giacomo
'''

import sys

import bootstrap

def buildVespaInventory(inventoryFilename):
    '''
    Creates Ansible inventory containing all Vespa nodes and all possible VMs.
    Uses [nodes] group for physical cluster, [vms] group for virtual machines.
    '''
    # Bootstrap Vespa with default config, get dependencies
    bootstrap.doBootstrap()
    bootstrapper = bootstrap.getInstance()
    
    # get all nodes and vms
    physicalCluster = bootstrapper.getPhysicalCluster()
    allVMDetails = bootstrapper.getAllVMDetails()
    
    # produce inventory files for nodes and vms 
    temporaryNodeFilename = '/tmp/vespa-nodeinv-temp'
    physicalCluster.createInventory(temporaryNodeFilename, allVMDetails)
    
    temporaryVmFilename = '/tmp/vespa-vminv-temp'
    allVMDetails.createVirtualInventory(temporaryVmFilename, physicalCluster)
    
    # join both inventories in a single file
    with open(inventoryFilename, 'w') as inventoryFile:
        inventoryFile.write('[nodes]\n')
        with open(temporaryNodeFilename, 'r') as nodeFile:
            inventoryFile.write(nodeFile.read()) 
        
        inventoryFile.write('\n[vms]\n')
        with open(temporaryVmFilename, 'r') as vmFile:
            inventoryFile.write(vmFile.read())
            
    print(inventoryFilename)

if __name__ == '__main__':
    
    # verify input
    if len(sys.argv) < 2:
        raise ValueError("call: " + sys.argv[0] + " <inventoryFilename>")
    inventoryFilename = sys.argv[1]
    
    # write Inventory
    buildVespaInventory(inventoryFilename)