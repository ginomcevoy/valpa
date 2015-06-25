'''
Created on Nov 7, 2014

@author: giacomo
'''

class SetsIpAddressesToPhysicalCluster(object):
    '''
    Should be loaded by the VESPA bootstrapper. Receives the recently created
    PhysicalCluster instance (all nodes) and fills the IP addresses. This is
    done after creating the PhysicalCluster due to dependency issues. 
    '''

    def __init__(self, networkAddresses):
        '''
        Constructor
        '''
        self.networkAddresses = networkAddresses
        
    def setIpAddresses(self, physicalCluster):
        for nodeName in physicalCluster.getNames():
            # get each node and delegate ip address resolution
            nodeIndex = physicalCluster.getNodeIndex(nodeName)
            ipAddress = self.networkAddresses.getNodeAddress(nodeIndex)
            physicalCluster.setIpAddressTo(nodeName, ipAddress)
            
class SetsAddressesToAllPossibleVMs():
    '''
    Should be loaded by the VESPA bootstrapper. Receives the recently created
    AllPossibleVMs instance and fills the IP and MAC addresses.  
    '''
    def __init__(self, networkAddresses, physicalCluster):
        self.networkAddresses = networkAddresses
        self.physicalCluster = physicalCluster
        
    def setAddresses(self, allPossibleVMs):
        for vmName in allPossibleVMs.getNames():
            # get each vm and delegate ip address resolution
            vmIndex = allPossibleVMs.getVMIndex(vmName)
            nodeName = allPossibleVMs.getHostingNode(vmName)
            nodeIndex = self.physicalCluster.getNodeIndex(nodeName)
            
            ipAddress = self.networkAddresses.getVMAddress(nodeIndex, vmIndex)
            macAddress = self.networkAddresses.getVMMAC(nodeIndex, vmIndex)
            
            allPossibleVMs.setIpAddressTo(vmName, ipAddress)
            allPossibleVMs.setMacAddressTo(vmName, macAddress)
