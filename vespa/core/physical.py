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
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name
        
class PhysicalCluster:
    """An aggregation of physical machines (PhysicalNode instances) that 
    represent either the whole cluster or a subset.
    
    This class is iterable on its nodes (for node in physicalCluster).
    
    @type nodeDict: dictionary {nodeName : PhysicalNode instance}
    """
    
    def __init__(self, nodeDict):
        self.nodeDict = nodeDict
        self.nodeNames = tuple(sorted(nodeDict.keys()))
        self.orderedNodes = []      # keep an ordered list too 
        for nodeName in self.nodeNames:
            self.orderedNodes.append(nodeDict[nodeName])  
        self.orderedNodes = tuple(self.orderedNodes)
        
    def __len__(self):
        return len(self.nodeNames)
    
    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError
        return self.orderedNodes[index]
    
    def getNode(self, nodeName):
        return self.nodeDict[nodeName]
    
    def getSubset(self, nodeNames):
        '''
        Extracts a subset of the nodes.
        @return: PhysicalCluster, None if nodeNames is empty list
        '''
        subsetDict = {}
        for nodeName in nodeNames:
            subsetDict[nodeName] = self.nodeDict[nodeName]
            
        return PhysicalCluster(subsetDict)
    
    def getSubsetForHostCount(self, hostCount):
        """ Uses the first `hostCount` nodes to get a subset cluster.
        
        @return: PhysicalCluster instance
        """
        if hostCount > len(self):
            raise ValueError('Not enough nodes in cluster: ' + hostCount)
        someNodeNames =  self.nodeNames[0:hostCount]
        return self.getSubset(someNodeNames)
    
    def toFile(self, filename):
        '''
        Outputs the node names to a file, one node per line.
        Overwrites file if exists.
        '''
        # open file for writing
        with open(filename, 'w') as nodeFile:
            for nodeName in sorted(self.nodeNames):
                nodeFile.write(nodeName + '\n')
                
    def createInventory(self, inventoryFilename, allVMDetails):
        '''
        Creates an inventory for Ansible. Overwrites file if exists.
        Example using 'vespa' as node name and 'kvm-pbs' as vm prefix:
        vespa02 nodeSuffix=02 nodeIndex=0 nodeNumber=2 \
        vmNames='["kvm-pbs02-01", "kvm-pbs02-02", ...]'
        vespa03 nodeSuffix=03 nodeIndex=1 nodeNumber=3 \
        vmNames='["kvm-pbs03-01", "kvm-pbs03-02", ...]'
        @param inventoryFilename: the name of the file
        @param allVMDetails: a valid instance of AllVMDetails 
        '''
        with open(inventoryFilename, 'w') as inventoryFile:
            for node in self:
                # build list of vmNames as string
                vmNames = allVMDetails.getVMNamesForNode(node)
                vmNamesString = ''
                for vmName in vmNames:
                    vmNamesString = vmNamesString + '"' + vmName + '",'
                vmNamesString = vmNamesString[0:len(vmNamesString)-1] 
                
                # write name, suffix, index and vmNames for each node
                suffix = node.suffix
                index = str(node.index)
                number = str(node.number)
                line = node.name + " nodeSuffix=" +  suffix + " nodeIndex=" + index + " nodeNumber=" + number + " vmNames='[" + vmNamesString + "]'\n"
                inventoryFile.write(line)

class PhysicalNodeFactory(object):
    '''
    Creates the PhysicalCluster object for all physical nodes in the cluster.
    '''

    def __init__(self, hwInfo):
        '''
        Constructor
        '''
        self.hwInfo = hwInfo
        self.allNodes = None
        
    def getAllNodes(self):
        """Return a PhysicalCluster object of all nodes in physical cluster.
        """
        if self.allNodes is None:
            
            nodeNames = self.hwInfo.getNodeNames()
            nodeDict = {}
            nodeIndex = 0 # zero-based index

            # node loop
            for nodeName in nodeNames:
                nodeSuffix = self.findNumberSuffix(nodeName)
                nodeNumber = int(nodeSuffix)

                # add node object to dict
                physicalNode = PhysicalNode(nodeName, nodeIndex, nodeNumber, nodeSuffix)
                nodeDict[nodeName] = physicalNode
                
                nodeIndex += 1
            
            self.allNodes = PhysicalCluster(nodeDict)
                
        return self.allNodes
    
    def findNumberSuffix(self, nodeName):
        """Find the longest final substring of the nodeName that is a number.                 
        """
        pos = len(nodeName) - 1
        while pos > 0:
            char = nodeName[pos]
            
            # check if this is a number
            try:
                int(char)
            except ValueError:
                # here pos points to a non-numerical character, stop    
                break
            
            # pos still points to a number, increase pos
            pos = pos - 1
            
        return nodeName[pos+1:len(nodeName)] 
