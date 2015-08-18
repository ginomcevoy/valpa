'''
Created on Nov 7, 2014

@author: giacomow
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
        
    @property
    def number(self):
        return self.index + 1
        
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
    """An aggregation of VMs (VMDetails instances) that 
    represent a virtual cluster
    
    This class is iterable on its VMs (for vm in allVMDetails).
    
    @ivar vmDict: dictionary {vmName : vmDetails instance}
    @ivar byNode: dictionary {node obj : vmName tuple}
    """

    def __init__(self, vmDict, byNode):
        self.vmDict = vmDict
        self.byNode = byNode
        self.orderedVMs = []      # keep an ordered list too 
        for vmName in self.vmDict.keys():
            self.orderedVMs.append(vmDict[vmName])  
        self.orderedVMs = tuple(self.orderedVMs)
        
    def __len__(self):
        return len(self.orderedVMs)
    
    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError
        return self.orderedVMs[index]
    
    def getVM(self, vmName):
        return self.vmDict[vmName]
        
    def getVMNamesForNode(self, node):
        return self.byNode[node]
    
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
                if vmDetails.hostingNode == node:
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
        # this orders VMs by index, so operations with Ansible on VMs 
        # can be parallelized over the nodes 
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
    
    @property
    def name(self):
        return self.vmDetails.name
    
    @property
    def index(self):
        return self.vmDetails.index
    
    @property
    def number(self):
        return self.vmDetails.number
    
    @property
    def suffix(self):
        return self.vmDetails.suffix
    
    @property
    def hostingNode(self):
        return self.vmDetails.hostingNode
    
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
        self.orderedVMTemplates = []
        for vmName in vmTemplateDict.keys():
            self.orderedVMTemplates.append(vmTemplateDict[vmName])  
        self.orderedVMTemplates = tuple(self.orderedVMTemplates)
        
    def __len__(self):
        return len(self.orderedVMTemplates)
    
    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError
        return self.orderedVMTemplates[index]
    
    def getVM(self, vmName):
        return self.vmTemplateDict[vmName]
    
    def getVMNamesForNode(self, node):
        return self.byNode[node]
    
    def setDefinitions(self, definitionDict):
        for vmName in definitionDict.keys():
            self.vmTemplateDict[vmName].setDefinition(definitionDict[vmName])
        
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
                nameFile.write(vmTemplate.name + '\n')
                
    def createVirtualInventory(self, inventoryFilename, inventoryVars=None):
        self.allVMDetails.createVirtualInventory(inventoryFilename, inventoryVars)
    
class BuildsAllVMDetails:
    '''
    Creates all the possible VM templates as VMDetails instances
    and returns an instance of AllPossibleVMs.
    '''
    def __init__(self, createParams, hwSpecs, physicalCluster):
        self.createParams = createParams
        self.hwSpecs = hwSpecs
        self.physicalCluster = physicalCluster
        
    def build(self):
        vmDict = {}
        byNode = {}
        
        # assume up to 'coresPerNode' VMs, where coresPerNode is
        # the number of physical cores
        vmsPerHost = self.hwSpecs['cores']
        
        # name is built with pattern
        vmNameTemplate = self.createParams['vm_pattern']
        vmNameTemplate = vmNameTemplate.replace('&PREFIX', self.createParams['vm_prefix'])
        
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
            
            node = vmDetails.hostingNode
            if node not in byNode.keys():
                byNode[node] = []
            byNode[node].append(vmName)
        
        for node in byNode.keys():
            byNode[node] = tuple(byNode[node])

        vmDetailsSubset = self.allVMDetails.getSubset(vmNames)
         
        return VirtualClusterTemplates(vmDict, byNode, vmDetailsSubset)
