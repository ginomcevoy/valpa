'''
Created on Nov 2, 2014

@author: giacomo
'''

class PhysicalNode(object):
    '''
    Represents a computing node of the physical cluster.
    Contains the following attributes:
    @ivar name: full name of the node, e.g node083
    @ivar index: zero-based index of node, 0 for first node
    @ivar number: number representing the node, e.g. 83, used for IP and MAC of VMs
    @ivar suffix: full suffix of the node name, e.g. 083, used for naming objects related to node
    @ivar ipAddress: added after instantiation, IP address of node 
        (ip addressing is based on node number, read from this object) 
    '''
    
    def __init__(self, nodeName, nodeIndex, nodeNumber, nodeSuffix):
        self.name = nodeName
        self.index = nodeIndex
        self.number = nodeNumber
        self.suffix = nodeSuffix
        self.ipAddress = None
        
    def setIpAddress(self, ipAddress):
        self.ipAddress = ipAddress
        
    def getIpAddress(self):
        if self.ipAddress is None:
            raise ValueError('IP address not set')
        return self.ipAddress
        
class NodeCluster:
    '''
    @type nodeDict: dictionary {nodeName : PhysicalNode instance}
    @type nodeTuple: tuple of node names
    '''
    
    def __init__(self, nodeDict, nodeTuple):
        self.nodeDict = nodeDict
        self.nodeTuple = nodeTuple
        
    def getNodeIndex(self, nodeName):
        return self.nodeDict[nodeName].index
    
    def getNodeNumber(self, nodeName):
        return self.nodeDict[nodeName].number
    
    def getNodeSuffix(self, nodeName):
        return self.nodeDict[nodeName].suffix
    
    def getNode(self, nodeName):
        return self.nodeDict[nodeName]
    
    def getNames(self):
        return self.nodeTuple
    
    def setIpAddressTo(self, nodeName, ipAddress):
        self.nodeDict[nodeName].setIpAddress(ipAddress)
        
    def getIpAddressOf(self, nodeName):
        return self.nodeDict[nodeName].getIpAddress()
    
    def getSubset(self, nodeNames):
        '''
        Extracts a subset of the nodes.
        @return: DeployNodes, None if nodeNames is empty list
        '''
        subsetDict = {}
        for nodeName in nodeNames:
            subsetDict[nodeName] = self.nodeDict[nodeName]
            
        return NodeCluster(subsetDict, tuple(nodeNames))
    
    def toFile(self, filename):
        '''
        Outputs the node names to a file, one node per line.
        Overwrites file if exists.
        '''
        # open file for writing
        with open(filename, 'w') as nodeFile:
            for node in sorted(self.nodeTuple):
                nodeFile.write(node + '\n')
                
    def createInventory(self, inventoryFilename, allVMDetails):
        '''
        Creates an inventory for Ansible. Overwrites file if exists.
        Example using 'vespa' as node name and 'kvm-pbs' as vm prefix:
        vespa02 nodeSuffix=02 nodeIndex=0 vmNames='["kvm-pbs02-01", "kvm-pbs02-02", ...]'
        vespa03 nodeSuffix=03 nodeIndex=1 vmNames='["kvm-pbs03-01", "kvm-pbs03-02", ...]'
        @param inventoryFilename: the name of the file
        @param allVMDetails: a valid instance of AllVMDetails 
        '''
        with open(inventoryFilename, 'w') as inventoryFile:
            for nodeName in sorted(self.nodeTuple):
                
                # build list of vmNames as string
                vmNames = allVMDetails.getVMNamesForNode(nodeName)
                vmNamesString = ''
                for vmName in vmNames:
                    vmNamesString = vmNamesString + '"' + vmName + '",'
                vmNamesString = vmNamesString[0:len(vmNamesString)-1] 
                
                # write name, suffix, index and vmNames for each node
                suffix = self.getNodeSuffix(nodeName)
                index = str(self.getNodeIndex(nodeName))
                line = nodeName + " nodeSuffix=" +  suffix + " nodeIndex=" + index + " vmNames='[" + vmNamesString + "]'\n"
                inventoryFile.write(line)

class PhysicalNodeFactory(object):
    '''
    Creates the NodeCluster object for all physical nodes in the cluster.
    '''

    def __init__(self, hwInfo):
        '''
        Constructor
        '''
        self.hwInfo = hwInfo
        self.allNodes = None
        
    def getAllNodes(self):
        '''
        Returns a NodeCluster object of all nodes in physical cluster.
        Nodes are inferred from sequence, it is calculated only once
        '''
        if self.allNodes is None:
            
            # build node list from sequence
            nodeNamesList = []
            
            nodeDict = {}
            nodeIndex = 0 # zero-based index

            # ex. '%03d' for 083, 084...
            formatString = '%0' + str(self.hwInfo.nodeZeros) + 'd'

            # node loop
            while (nodeIndex < self.hwInfo.nodeCount):
                nodeNumber = self.hwInfo.nodeFirst + nodeIndex

                # ex. node083
                nodeSuffix = formatString % nodeNumber 
                nodeName = self.hwInfo.nodePrefix + nodeSuffix

                # grow dict and list
                nodeNamesList.append(nodeName)
                physicalNode = PhysicalNode(nodeName, nodeIndex, nodeNumber, nodeSuffix)
                nodeDict[nodeName] = physicalNode
                
                nodeIndex += 1
            
            self.allNodes = NodeCluster(nodeDict, tuple(nodeNamesList))
                
        return self.allNodes 