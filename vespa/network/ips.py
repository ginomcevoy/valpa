'''
Created on Nov 7, 2014

@author: giacomo
'''

class SetsAddressesToPhysicalCluster(object):
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
        
    def setAddresses(self, physicalCluster):
        for node in physicalCluster:
            # delegate ip address resolution
            ipAddress = self.networkAddresses.getNodeAddress(node.index)
            node.setIpAddress(ipAddress)
            
class SetsAddressesToAllPossibleVMs():
    '''
    Should be loaded by the VESPA bootstrapper. Receives the recently created
    AllPossibleVMs instance and fills the IP and MAC addresses.  
    '''
    def __init__(self, networkAddresses, physicalCluster):
        self.networkAddresses = networkAddresses
        self.physicalCluster = physicalCluster
        
    def setAddresses(self, allPossibleVMs):
        for vm in allPossibleVMs:
            # delegate ip address resolution
            node = vm.hostingNode
            
            ipAddress = self.networkAddresses.getVMAddress(node.index, vm.index)
            macAddress = self.networkAddresses.getVMMAC(node.index, vm.index)
            
            vm.setIpAddress(ipAddress)
            vm.setMacAddress(macAddress)
