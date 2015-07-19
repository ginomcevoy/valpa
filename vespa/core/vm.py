'''
Created on Nov 7, 2014

@author: giacomo
'''

class VMDetails:
    '''
    Stores details about Virtual Machines (templates or instances)
    @ivar name: hostname of the VM
    @ivar index: zero-based index of VM in the physical node
    @ivar suffix: string representing the suffix number of the VM, e.g. 01, 12.
    @ivar hostingNode: node that is hosting the VM (PhysicalNode instance)
    @ivar macAddress: MAC address of the VM
    @ivar ipAddress: IP address of the VM
    '''
    def __init__(self, name, index, suffix, hostingNode):
        self.name = name
        self.index = index
        self.suffix = suffix
        self.hostingNode = hostingNode
        
        self.ipAddress = None
        self.macAddress = None
        
    def setIpAddress(self, ipAddress):
        self.ipAddress = ipAddress
        
    def getIpAddress(self):
        if self.ipAddress is None:
            raise ValueError('IP address not set')
        return self.ipAddress
        
    def setMacAddress(self, ipAddress):
        self.macAddress = ipAddress
        
    def getMacAddress(self):
        if self.macAddress is None:
            raise ValueError('MAC address not set')
        return self.macAddress
    
    def __cmp__(self, other):
        # Sort according to VM index, then according to  name
        thisIndex = self.index
        otherIndex = other.index
        if cmp(thisIndex, otherIndex) != 0:
            return cmp(thisIndex, otherIndex)
        else:
            thisVM = self.name
            otherVM = other.name
            return cmp(thisVM, otherVM)
     
class AllVMDetails():
    '''
    @ivar vmDict: dictionary {vmName : vmDetails instance}
    @ivar byNode: dictionary {node obj : vmName tuple}
    '''

    def __init__(self, vmDict, byNode):
        self.vmDict = vmDict
        self.byNode = byNode
        
    def getVMIndex(self, vmName):
        return self.vmDict[vmName].index
    
    def getVMNumber(self, vmName):
        return (self.vmDict[vmName].index + 1)
    
    def getVMSuffix(self, vmName):
        return self.vmDict[vmName].suffix

    def getHostingNode(self, vmName):
        return self.vmDict[vmName].hostingNode
    
    def getVMNamesForNode(self, node):
        return self.byNode[node]
    
    def getNames(self):
        return tuple(self.vmDict.keys())
    
    def setIpAddressTo(self, vmName, ipAddress):
        self.vmDict[vmName].setIpAddress(ipAddress)
        
    def getIpAddressOf(self, vmName):
        return self.vmDict[vmName].getIpAddress()
    
    def setMacAddressTo(self, vmName, macAddress):
        self.vmDict[vmName].setMacAddress(macAddress)
        
    def getMacAddressOf(self, vmName):
        return self.vmDict[vmName].getMacAddress()
    
    def getSubset(self, vmNames):
        '''
        Returns an AllVMDetails instance for only the specified VMs.
        Will correctly return the byNode dictionary with the
        nodes that host at least one VM.
        '''
        vmDictSubset = {}
        byNodeSubset = {}
        
        for vmName in vmNames:
            # build vmDictSubset as a subset dictionary of vmDict
            vmDetails = self.vmDict[vmName]
            vmDictSubset[vmName] = vmDetails
            
            # find the node that hosts this VM
            for node in self.byNode.keys():
                # if node is not hosting this VM, skip
                if self.getHostingNode(vmName) == node:
                    if node not in byNodeSubset.keys():
                        # initial case: node has not been added yet
                        byNodeSubset[node] = [vmName]
                    else:
                        # node has other VMs, add to list
                        byNodeSubset[node].append(vmName)
                        
        # convert node dictionary elements to tuples
        for node in byNodeSubset.keys():
            byNodeSubset[node] = tuple(byNodeSubset[node])
                
        return AllVMDetails(vmDictSubset, byNodeSubset)
    
    def createVirtualInventory(self, inventoryFilename, inventoryVars=None):
        '''
        Creates an inventory for Ansible. Overwrites file if exists.
        Example using 'node' as node name and 'kvm-pbs' as vm prefix:
        kvm-pbs082-01 vmSuffix=01 nodeSuffix=082 hostingNode=node082
        kvm-pbs082-02 vmSuffix=02 nodeSuffix=082 hostingNode=node082
        @param inventoryFilename: the name of the file for VM inventory
        @param inventoryVars (optional): dictionary of variables
        '''
        # the templates get sorted using the __cmp__ function
        sortedVmDetails = sorted(self.vmDict.values())
        
        # infer hostCount and vmsPerHost from current state
        hostCount = len(self.byNode.keys())
        vmsPerHost = len(self.byNode[self.byNode.keys()[0]])
         
        with open(inventoryFilename, 'w') as inventoryFile:
            # write VM lines
            for vmDetails in sortedVmDetails:
                hostingNode = vmDetails.hostingNode
                vmIndex = vmDetails.index
                if hostingNode.index < hostCount and vmIndex < vmsPerHost:
                    nodeSuffix = hostingNode.suffix
                    nodeName = hostingNode.name
                    line = vmDetails.name + " vmSuffix=" +  vmDetails.suffix + " nodeSuffix=" + nodeSuffix + " hostingNode=" + nodeName + "\n"
                    inventoryFile.write(line)
                    
            # write variables if present
            if inventoryVars is not None:
                inventoryFile.write('\n[all:vars]\n')
                for key in sorted(inventoryVars.keys()):
                    inventoryFile.write(key + '=' + inventoryVars[key] + '\n')
    
class VMTemplate:
    '''
    Contains all the necessary information to instantiate a VM. Besides the
    VMDetails instance, it has the domain XML to be used by libvirt.
    '''
    
    def __init__(self, vmDetails, cpv):
        self.vmDetails = vmDetails
        self.cpv = cpv
        self.xml = None
        
    def setDefinition(self, xml):
        self.xml = xml
    
    def getDefinition(self):
        if self.xml is None:
            raise ValueError('Definition XML was not added to this template: ', self.vmDetails.name)
        return self.xml

    def __cmp__(self, other):
        # Sort according to VM details ordering
        return self.vmDetails.__cmp__(other.vmDetails)
    
class VirtualClusterTemplates:
    '''
    Contains all the VMTemplate instances for a virtual cluster.
    @ivar vmTemplateDict: dictionary {vmName : vmTemplate instance}
    @ivar byNode: dictionary {node : vmName tuple}
    '''
    def __init__(self, vmTemplateDict, byNode, allVMDetails):
        self.vmTemplateDict = vmTemplateDict
        self.byNode = byNode
        self.allVMDetails = allVMDetails
        
    def getVMIndex(self, vmName):
        return self.vmTemplateDict[vmName].vmDetails.index
    
    def getVMNumber(self, vmName):
        return self.vmTemplateDict[vmName].vmDetails.index + 1
    
    def getVMSuffix(self, vmName):
        return self.vmTemplateDict[vmName].vmDetails.suffix
    
    def getHostingNode(self, vmName):
        return self.vmTemplateDict[vmName].vmDetails.hostingNode
    
    def getCpv(self, vmName):
        return self.vmTemplateDict[vmName].cpv
    
    def getVMNamesForNode(self, node):
        return self.byNode[node]
    
    def getNames(self):
        return tuple(self.vmTemplateDict.keys())
    
    def setDefinitions(self, definitionDict):
        for vmName in definitionDict.keys():
            self.vmTemplateDict[vmName].setDefinition(definitionDict[vmName])
        
    def getDefinitionOf(self, vmName):
        return self.vmTemplateDict[vmName].getDefinition()

    def definitionsToFile(self, filename):
        '''
        Creates a file with the given filename, contains the paths to the
        XML definitions of the VMs in the cluster template. Each line
        contains one XML path. The definitions are ordered by VM index, 
        then by node name
        @param filename: the filename for the output file
        '''
        # the templates get sorted using the __cmp__ function
        sortedTemplates = sorted(self.vmTemplateDict.values())

        with open(filename, 'w') as definitionFile:
            for vmTemplate in sortedTemplates:
                definitionFile.write(vmTemplate.getDefinition() + '\n')
                
    def namesToFile(self, filename):
        '''
        Creates a file with the given filename, contains the names of the
        VMs in the cluster template. Each line contains one VM name. 
        The names are ordered by VM index, then by node name
        @param filename: the filename for the output file
        '''
        # the templates get sorted using the __cmp__ function
        sortedTemplates = sorted(self.vmTemplateDict.values())

        with open(filename, 'w') as nameFile:
            for vmTemplate in sortedTemplates:
                nameFile.write(vmTemplate.vmDetails.name + '\n')
                
    def createVirtualInventory(self, inventoryFilename, inventoryVars=None):
        self.allVMDetails.createVirtualInventory(inventoryFilename, inventoryVars)
    
class BuildsAllVMDetails:
    '''
    Creates all the possible VM templates as VMDetails instances
    and returns an instance of AllPossibleVMs.
    '''
    def __init__(self, vespaPrefs, hwSpecs, physicalCluster):
        self.vespaPrefs = vespaPrefs
        self.hwSpecs = hwSpecs
        self.physicalCluster = physicalCluster
        
    def build(self):
        vmDict = {}
        byNode = {}
        
        # assume up to 'coresPerNode' VMs, where coresPerNode is
        # the number of physical cores
        vmsPerHost = self.hwSpecs['cores']
        
        # name is built with pattern
        vmNameTemplate = self.vespaPrefs['vm_pattern']
        vmNameTemplate = vmNameTemplate.replace('&PREFIX', self.vespaPrefs['vm_prefix'])
        
        # iterate over physical nodes
        for node in self.physicalCluster:
            vmNameHost = vmNameTemplate.replace('&NODESUFFIX', node.suffix)
            byNodeList = [] 

            # Each node gets vmsPerHost VMs. Index of first VM = 0
            for vmIndex in range(0, vmsPerHost):

                vmNumber = vmIndex + 1
                vmSuffix = '%02d' % vmNumber
                vmName = vmNameHost.replace('&VMSUFFIX', vmSuffix)
                
                # (index, number, suffix, nodeName)
                vmDict[vmName] = VMDetails(vmName, vmIndex, vmSuffix, node)                 
                byNodeList.append(vmName)
            
            byNode[node] = tuple(byNodeList)

        return AllVMDetails(vmDict, byNode)

class VirtualClusterFactory:
    '''
    Builds the VirtualClusterTemplates instance for a given set of
    VM names.
    '''
    def __init__(self, allVMDetails):
        self.allVMDetails = allVMDetails
        
    def create(self, vmNames, cpv):
        '''
        @param vmNames: tuple of VM names, found in allVMDetails instance.
        '''
        vmDict = {}
        byNode = {}
        
        for vmName in vmNames:
            # get the details and create the template object
            vmDetails = self.allVMDetails.vmDict[vmName]
            vmTemplate = VMTemplate(vmDetails, cpv)
            vmDict[vmName] = vmTemplate
            
            node = self.allVMDetails.getHostingNode(vmName)
            if node not in byNode.keys():
                byNode[node] = []
            byNode[node].append(vmName)
        
        for node in byNode.keys():
            byNode[node] = tuple(byNode[node])

        vmDetailsSubset = self.allVMDetails.getSubset(vmNames)
         
        return VirtualClusterTemplates(vmDict, byNode, vmDetailsSubset)
