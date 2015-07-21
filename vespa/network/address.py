'''
Created on Oct 22, 2014

Routines for newtork addresses

@author: giacomo
'''

class NetworkAddresses:
        
    def __init__(self, networkingOpts, physicalCluster, hwSpecs):
        self.networkingOpts = networkingOpts
        self.physicalCluster = physicalCluster
        self.hwSpecs = hwSpecs
            
    def addressRangeStart(self, nodeIndex):
        '''
        DHCP range start, given zero-based node index.
        '''
        nodeName = self.physicalCluster.nodeNames[nodeIndex]
        node = self.physicalCluster.getNode(nodeName)
        
        # behavior depends on class
        if self.__usingCClass__():
            # First VM of first machine will get $IP_PREFIX.($DHCP_START)
            # First VM of second machine will get $IP_PREFIX.($DHCP_START + DHCP_STEP )
            dhcpStart = self.networkingOpts['dhcp_c_start']
            dhcpStep = self.networkingOpts['dhcp_c_step']
            rangeStartSuffix = int(dhcpStart) + (int(dhcpStep) * nodeIndex) 

            rangeStartPrefix =self.networkingOpts['dhcp_c_prefix']
            rangeStart = rangeStartPrefix + '.' + str(rangeStartSuffix)
            
        elif self.__usingBClass__():
            dhcpStart = self.networkingOpts['dhcp_b_start']
            rangeStartPrefix = self.networkingOpts['dhcp_b_prefix']
            rangeStart = rangeStartPrefix + '.' + str(node.number) + '.' + str(dhcpStart) 
            
        else:
            self.__invalidClass__()
            
        return rangeStart

    def addressRangeEnd(self, nodeIndex):
        '''
        DHCP range end, given zero-based node index.
        '''
        vmsPerHost = self.hwSpecs['cores']
        nodeName = self.physicalCluster.nodeNames[nodeIndex]
        node = self.physicalCluster.getNode(nodeName)
        
        # behavior depends on class
        if self.__usingCClass__():
            dhcpStart = self.networkingOpts['dhcp_c_start']
            dhcpStep = self.networkingOpts['dhcp_c_step'] 
            rangeEndSuffix = int(dhcpStart) + int(dhcpStep) * nodeIndex + vmsPerHost - 1
            
            rangeEndPrefix = self.networkingOpts['dhcp_c_prefix']
            rangeEnd = rangeEndPrefix + '.' + str(rangeEndSuffix) 
            
        elif self.__usingBClass__():
            dhcpStart = self.networkingOpts['dhcp_b_start']
            rangeEndSuffix = int(dhcpStart) + vmsPerHost - 1
            
            rangeEndPrefix = self.networkingOpts['dhcp_b_prefix']
            rangeEnd = rangeEndPrefix + '.' + str(node.number) + '.' + str(rangeEndSuffix)
            
        else:
            self.__invalidClass__() 
            
        return rangeEnd
    
    def getNodeAddress(self, nodeIndex):
        '''
        Returns IP address of node given its zero-based index
        '''
        nodeName = self.physicalCluster.nodeNames[nodeIndex]
        node = self.physicalCluster.getNode(nodeName)
        
        # behavior depends on class
        if self.__usingCClass__():
            prefix = self.networkingOpts['dhcp_c_prefix']
            nodeAddress = prefix + '.' + str(nodeIndex + 1)
            
        elif self.__usingBClass__():
            prefix = self.networkingOpts['dhcp_b_prefix']
            nodeAddress = prefix + '.' + str(node.number) + '.254'
            
        else:
            self.__invalidClass__() 
            
        return nodeAddress
    
    def getVMAddress(self, nodeIndex, vmIndex):
        '''
        Returns IP address of VM given node and VM zero-based indexes.
        '''
        nodeName = self.physicalCluster.nodeNames[nodeIndex]
        node = self.physicalCluster.getNode(nodeName)
        
        # behavior depends on class
        if self.__usingCClass__():
            # First VM of first machine will get $IP_PREFIX.$DHCP_START
            # First VM of second machine will get $IP_PREFIX.($DHCP_START + $DHCP_STEP)
            dhcpStart = self.networkingOpts['dhcp_c_start']
            dhcpStep = self.networkingOpts['dhcp_c_step']
            vmAddressSuffix = int(dhcpStart) + (int(dhcpStep) * nodeIndex) + vmIndex 

            vmAddressPrefix =self.networkingOpts['dhcp_c_prefix']
            vmAddress = vmAddressPrefix + '.' + str(vmAddressSuffix)
            
        elif self.__usingBClass__():
            vmAddressPrefix = self.networkingOpts['dhcp_b_prefix']
            vmAddress = vmAddressPrefix + '.' + str(node.number) + '.' + str(vmIndex + 1)

        else:
            self.__invalidClass__() 
            
        return vmAddress
    
    def getVMMAC(self, nodeIndex, vmIndex):
        '''
        Returns MAC address of VM given node and VM zero-based indexes.
        TODO: Does not work for node number > 99!
        '''
        nodeName = self.physicalCluster.nodeNames[nodeIndex]
        node = self.physicalCluster.getNode(nodeName)
        
        # strategy for large node numbers (UNTESTED)
        if node.number < 100:
            # e.g. 82, 01 (tested)
            nodePart = '%02d' % node.number
        elif node.number < 256:
            # contingency for 3 digits, use hexadecimal
            nodePart = '%02x' % node.number
        else:
            raise ValueError('Vespa limitation: cannot issue MAC addresses for nodeNumber > 255!') 
        
        # apply same strategy for vm suffix
        if vmIndex < 100:
            vmPart = '%02d' % (vmIndex + 1)
        elif vmIndex  < 256:
            vmPart = '%02x' % (vmIndex + 1)
        else:
            raise ValueError('Vespa limitation: cannot issue MAC addresses for vmIndex > 255!')
        
        macSuffix = self.networkingOpts['net_mac_prefix']
        
        return macSuffix + ':' + nodePart + ':' + vmPart
        
    
    def networkBroadcast(self):
        if self.__usingBClass__():
            prefix = self.networkingOpts['dhcp_b_prefix']
            broadcast = prefix + '.255.255'
        elif self.__usingCClass__():
            prefix = self.networkingOpts['dhcp_c_prefix']
            broadcast = prefix + '.255'
        else:
            self.__invalidClass__()
        
        return broadcast
    
    def networkNetmask(self):
        if self.__usingBClass__():
            netmask = '255.255.0.0'
        elif self.__usingCClass__():
            netmask = '255.255.255.0'
        else:
            self.__invalidClass__()
            
        return netmask

    def networkRouter(self):
        if self.__usingBClass__():
            prefix = self.networkingOpts['dhcp_b_prefix']
            router = prefix + '.0.254'
        elif self.__usingCClass__():
            prefix = self.networkingOpts['dhcp_c_prefix']
            router = prefix + '.1'
        else:
            self.__invalidClass__()
            
        return router
    
    def networkSubnet(self):
        if self.__usingBClass__():
            prefix = self.networkingOpts['dhcp_b_prefix']
            subnet = prefix + '.0.0'
        elif self.__usingCClass__():
            prefix = self.networkingOpts['dhcp_c_prefix']
            subnet = prefix + '.0'
        else:
            self.__invalidClass__()
            
        return subnet
    
    def networkCIDR(self):
        if self.__usingBClass__():
            subnetBits = '16' 
        else:
            subnetBits = '24'
        return self.networkSubnet() + "/" + subnetBits 
    
    def __usingBClass__(self):
        return self.networkingOpts['net_class'] == 'B'
    
    def __usingCClass__(self):
        return self.networkingOpts['net_class'] == 'C'
    
    def __invalidClass__(self):
        raise ValueError('Invalid net_class parameter in vespa.params: ', self.networkingOpts['net_class'])

if __name__ == '__main__':
    pass