'''
Created on Oct 14, 2013

@author: giacomo
'''
from bean.enum import PinningOpt
import math

class PinningWriter:
    '''
    Modifies Vm XMLs and adds pinning strategy
    '''
    def __init__(self, valpaPrefs, pinningTextGen):
        '''
        @type pinningTextGen: PinningTextGenerator, strategy to creating pinning text
        '''
        self.valpaPrefs = valpaPrefs
        self.pinningTextGen = pinningTextGen
        
    def setDeploymentContext(self, deploymentInfo):
        self.deployedVMs = deploymentInfo[2]
        
    def enhanceXMLs(self, xmlDict, cpv, pinningOpt):
        
        # NONE case: don't do anything
        if pinningOpt == PinningOpt.NONE:
            return xmlDict
        
        outputDict = {}
        
        # iterate XMLs
        for vmName in xmlDict.keys():
            xml = xmlDict[vmName]
            
            # use pinningTextGen to get text
            vmIndex = self.deployedVMs.getVMIndex(vmName)
            pinningText = self.pinningTextGen.producePinningText(pinningOpt, vmIndex, cpv)
            
            # add it to xml, just below </vcpu>
            vcpuPos = xml.find('</vcpu>\n') + len('</vcpu>\n')
            xmlBefore = xml[0:vcpuPos]
            xmlAfter = xml[vcpuPos:len(xml)]
            
            outputDict[vmName] = xmlBefore + pinningText + xmlAfter
            
        return outputDict


class PinningTextGenerator:
    '''
    Creates the text for pinning strategy, that can be added to XML.
    '''
    
    def __init__(self, hwSpecs, coreMapper):
        self.hwSpecs = hwSpecs
        self.coreMapper = coreMapper
        
    def producePinningText(self, pinningOpt, vmIndex, cpv):
        
        output = '<cputune>\n'
        
        # get pinnings from coreMapper
        allPhyCores = self.coreMapper.getPhysicalCores(pinningOpt, vmIndex, cpv)
        
        for vcore in range(0, cpv):
            phyCores = allPhyCores[vcore] # this is a tuple
            vcpuText = '<vcpupin vcpu="' + str(vcore) + '" cpuset="'
            
            for index in range(0, len(phyCores)):
                phyCore = phyCores[index]
                vcpuText += str(phyCore)
                if index < len(phyCores) -1:
                    vcpuText += ','
                    
            vcpuText += '"/>'
            output += vcpuText + '\n'
        
        output += '</cputune>\n'
        return output
    
class PinningVirshTextGenerator:
    '''
    Creates the text for pinning strategy, that represents a virsh call
    '''
    
    def __init__(self, coreMapper):
        self.coreMapper = coreMapper
        
    def producePinningCalls(self, pinningOpt, vmIndex, cpv):
        
        output = []
        
        # NONE case: return nothing
        if pinningOpt == PinningOpt.NONE:
            return output
        
        # get pinnings from coreMapper
        allPhyCores = self.coreMapper.getPhysicalCores(pinningOpt, vmIndex, cpv)
        
        for vcore in range(0, cpv):
            phyCores = allPhyCores[vcore] # this is a tuple
            oneVirshCall = 'virsh vcpupin ' + str(vcore) + ' '
            
            for index in range(0, len(phyCores)):
                phyCore = phyCores[index]
                oneVirshCall += str(phyCore)
                if index < len(phyCores) -1:
                    oneVirshCall += ','
                    
            output.append(oneVirshCall)
        
        return tuple(output)

class PinningCoreMapper:
    '''
    Provides functions that determine the virtual cores mappings.
    '''

    def __init__(self, hwSpecs):
        '''
        Constructor, takes HW specs given by HardwareInfo.getSpecs.
        '''
        self.cores = hwSpecs['cores']
        self.sockets = hwSpecs['sockets']
        self.coresPerSocket = int(self.cores / self.sockets)
        
    def getPhysicalCores(self, pinningOpt, vmIndex, cpv):
        '''
        @type pinningOpt: PinningOpt, values in
         ["BAL_ONE", "BAL_SET", "GREEDY", "SPLIT"] (not NONE)
        @return: tuple (tuple phyCores for core0, tuple phyCores for core1, ...) 
        '''
        if pinningOpt == PinningOpt.BAL_ONE:
            return self.getBalOneCores(vmIndex, cpv) 
        
        if pinningOpt == PinningOpt.BAL_SET:
            return self.getBalSetCores(vmIndex, cpv)
        
        if pinningOpt == PinningOpt.GREEDY:
            return self.getGreedyCores(vmIndex, cpv)
        
        if pinningOpt == PinningOpt.SPLIT:
            return self.getSplitCores(vmIndex, cpv)
        
    def getBalOneCores(self, vmIndex, cpv):
        '''
        Returns pinnings for BAL_ONE strategy
        '''
        
        # special case
        if (cpv == 4 and vmIndex == 2 and self.coresPerSocket == 6):
            output = ((4,), (5,), (10,), (11,))
            return output
        
        # general case
        output = []
        first = (vmIndex % self.sockets) * self.coresPerSocket + int(vmIndex / self.sockets) * cpv
        first = int(first)
        
        for i in range(0, cpv):
            phyProc = first + i
            output.append((phyProc,))
            
        return tuple(output) 
        
    def getBalSetCores(self, vmIndex, cpv):    
        '''
        Returns pinnings for BAL_SET strategy, similar to BAL_ONE but 
        each vcore is mapped to all physical sockets that appear in the VM for BAL_SET 
        '''

        # special case        
        if (cpv == 4 and vmIndex == 2 and self.coresPerSocket == 6):
            output = ((4,5), (4,5), (10,11), (10,11))
            return output
        
        # reuse BAL_ONE logic
        balPhyCores = self.getBalOneCores(vmIndex, cpv)
        
        # Determine number of required blocks
        blocks = math.ceil(float(cpv)/self.coresPerSocket)
        blocks = int(blocks)

        output = [] 

        # iterate blocks
        for b in range(0, blocks):

            # take the corresponding subset of cores 
            start = b * self.coresPerSocket
            end = start + self.coresPerSocket
            if end > (cpv):
                end = cpv

            # get relevant cores    
            phyCores = []
            for entry in balPhyCores:
                phyCore = entry[0] # entry is a one-item tuple!
                phyCores.append(phyCore)
    
            coresBlock = phyCores[start:end]
  
            # now use all cores in the block
            group=[]
            for core in coresBlock:
                group.append(core)
  
            # we now have the pinning of all v cores in the block, repeat it v times
            for core in coresBlock:
                output.append(tuple(group))
            
        return tuple(output)
    
    def getGreedyCores(self, vmIndex, cpv):
        output = []
        first = vmIndex * cpv
        
        for i in range(0, cpv):
            phyProc = first + i
            output.append((phyProc,))
            
        return tuple(output)
    
    def getSplitCores(self, vmIndex, cpv):
        
        # special case, reduces to balanced
        if cpv == 1:
            return self.getBalOneCores(vmIndex, cpv)
        
        output = []
        vcoresPerSocket = int(cpv / self.sockets)
        
        for socketIndex in range(0, self.sockets):
            first = vmIndex * vcoresPerSocket + socketIndex * self.coresPerSocket
            
            for vcoreIndex in range(0, vcoresPerSocket):
                # index = socketIndex * vcoresPerSocket + vcoreIndex
                phyProc = first + vcoreIndex
                output.append((phyProc,))
        
        return tuple(output)
    
class BuildsPinningWriter:
    '''
    Creates an instance of EnhancesXMLWithPinnings   
    '''
    
    def __init__(self, hwSpecs, valpaPrefs):
        self.valpaPrefs = valpaPrefs
        self.coreMapper = PinningCoreMapper(hwSpecs)
        self.pinningTextGen = PinningTextGenerator(hwSpecs, self.coreMapper)
        
    def build(self):
        return PinningWriter(self.valpaPrefs, self.pinningTextGen)
    
class PinningVirshTextGenFactory:
    '''
    Creates an instance of PinningVirshTextGenerator
    '''
    def __init__(self, hwSpecs):
        self.coreMapper = PinningCoreMapper(hwSpecs)
        
    def create(self):
        return PinningVirshTextGenerator(self.coreMapper)