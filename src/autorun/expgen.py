'''
Created on Nov 10, 2013

@author: giacomo
'''
from bean.enum import PinningOpt, MPIBindOpt
from quik import FileLoader
import os

class ExperimentGenerator(object):
    '''    
    Follows the Builder pattern, generates XML based on desired variations.
    @deprecated: use ExperimentGenerator from placementgen instead
    '''

    def __init__(self, hwSpecs):
        '''
        Constructor
        '''
        self.hwSpecs = hwSpecs
        self.groups = {}
        
    def withCpvValues(self, cpvs):
        '''
        Indicates tuple with possible cpv values, generates possible idf values
        based on hardware specs
        '''
        self.cpvs = cpvs
        self.idfs = {}
        
        # idf is either 0 or a multiple of cpv that does not exceed the number 
        # of physical cores (assuming all sockets)hwSpecs
        # organize these values in a map: each key corresponds to a cpv, the
        # 0 value is omitted.
        for cpv in cpvs:
            idfsForCpv = [] # always 0 (one machine) is omitted
            
            # add multiples of cpv
            multiples = findCpvMultiples(cpv, self.hwSpecs['cores'])
            idfsForCpv.extend(multiples)
            self.idfs[str(cpv)] = tuple(idfsForCpv)
            
        return self
    
    def withMachines(self, machineTuple):
        '''
        Indicates tuple with possible number of physical machines, generates possible
        nc values based on idf/cpv values and returns a list of tuples (nc, cpv, idf)
        '''
        self.combinations = [] # list of tuples
        
        for machineCount in machineTuple:
            if machineCount == 1:
                # special case, only use idf = 0, then nc = k * cpv, nc <= pcores
                for cpv in self.cpvs:
                    ncs = findCpvMultiples(cpv, self.hwSpecs['cores'])
                    for nc in ncs:
                        self.combinations.append((nc, cpv, 0))
            else:
                # idf > 0, then nc = machineCount * idf (vms/vmsPerHost) = (nc/cpv)/(idf/cpv)
                for cpv in self.cpvs:
                    # get all idf > 0
                    idfs = self.idfs[str(cpv)]
                    
                    # iterate to get nc values
                    for idf in idfs:
                        nc = machineCount * idf
                        self.combinations.append((nc, cpv, idf))
                        
        self.groupCombinations()
        return self
    
    def groupCombinations(self):
        
        # group the combinations according to cpv + idf
        
        for comb in self.combinations:
            key = str(comb[1]) + '-' + str(comb[2])
            if key not in self.groups.keys(): 
                self.groups[key] = [comb]
            else:
                self.groups[key].append(comb)
    
    def withPstratValues(self, pstratTuple=(PinningOpt.BAL_ONE, PinningOpt.BAL_SET, PinningOpt.GREEDY, PinningOpt.SPLIT, PinningOpt.NONE)):
        '''
        All the included pstrat values (default = all 5 values)
        '''
        self.pstratTuple = pstratTuple
        return self
    
    def withPinCores(self, pinCoreTuple=(MPIBindOpt.BIND_CORE, MPIBindOpt.BIND_SOCKET, MPIBindOpt.NONE)):
        '''
        Bind-to-core options (default = (BIND_CORE, BIND_SOCKET, NONE) tuple)
        '''
        self.pinCoreTuple = pinCoreTuple
        return self
    
    def generateXMLs(self, appInfo, xmlPath):
        '''
        Generates one XML per grouping, with all NC, PinningOpts and PinCores values
        (default = size(NC) * 15 for each group).
        If groupCombinations() was not called, then a single XML is generated.  
        '''
        if not os.path.exists(xmlPath):
            os.makedirs(xmlPath)
        xmlNames = []
        
        # if groupCombinations() was not called, do one XML
        if len(self.groups) == 0:
            self.groups = {'all' : self.combinations}
        
        for experimentList in self.groups.values():
            #print(experimentList)
            xmlName = self.generateXML(experimentList, appInfo, xmlPath)
            xmlNames.append(xmlName)
        return tuple(xmlNames)
        
    def generateXML(self, experimentList, appInfo, xmlPath):
        '''
        Generates one XML for a group of experiments.
        '''
        # text base for template building
        xmlText = '<?xml version="1.0"?>\n<experiments>\n'
        
        # use these variables for all experiments
        #expNameBase = 'nc' + str(groupTuple[0]) + '-cpv' + str(groupTuple[1]) + '-idf' + str(groupTuple[2])
        appName = appInfo.name
        appRuns = appInfo.runs
        appArgs = appInfo.args
        
        # experiments are grouped by cpv + idf
        cpv = experimentList[0][1]
        idf = experimentList[0][2] 
        xmlName = xmlPath + '/' + appName + '-cpv' + str(cpv) + '-idf' + str(idf) + '.xml'
        xmlFile = open(xmlName, 'w') 
        
        # iterate experiment groups (different nc values)
        for experimentGroup in experimentList:
            
            # Common to group
            nc = experimentGroup[0]
            
            # iterate pinning options
            for pstrat in self.pstratTuple:
                
                # iterate procPin options
                for procPin in self.pinCoreTuple: 
            
                    # This is specific to experiment
                    expName =  'nc' + str(nc) + '-cpv' + str(cpv) + '-idf' + str(idf) + '-ps' + str(pstrat) + '-pp' + str(procPin)
                    
                    # special case for arguments 
                    appArgs = self.setSpecialArguments(appName, appArgs, nc, cpv)
                    
                    # Use template, with all local variables set
                    loader = FileLoader('.')
                    template = loader.load_template('../templates/builder-exponly.template')
                    text = template.render(locals(), loader=loader)#.decode('utf-8')
                    xmlText += text
                    
        # close XML file now
        xmlText += '</experiments>\n'
        xmlFile.write(xmlText)
        xmlFile.close()
        return xmlName
    
    def setSpecialArguments(self, appName, appArgs, nc, cpv):
        '''
        Handle special applications here (bad indirection...)
        '''
        if appName == 'npb-ep':
            return str(nc) + ' C'
        else:
            return appArgs
        
class NPBExecutableGenerator():
    '''
    Creates a file to be read by the NPB suite generator
    '''
    
    def __init__(self, hwSpecs):
        self.hwSpecs = hwSpecs
        
        # use as strategy
        self.expGen = ExperimentGenerator(hwSpecs)
                
    def produceCoreSet(self, cpvs, maxMachines):
        '''
        Creates a set of all the required NC values
        '''
        
        self.expGen.withCpvValues(cpvs) # creates idfs
        self.expGen.withMachines(range(1, maxMachines + 1)) # creates ncs and combinations
        
        # get nc combinations
        ncs = []
        for comb in self.expGen.combinations:
            ncs.append(comb[0])
        
        # sort and don't repeat values
        ncs = set(sorted(ncs))
        return ncs
    
    def writeSuiteFile(self, coreSet, outputFile, expType = 'ep', expClass = 'D'):
        
        # start writing
        with open(outputFile, 'w') as output:
            for coreCount in coreSet:
                output.write(expType + '\t' + expClass + '\t' + str(coreCount) + '\n')
    
def findCpvMultiples(cpv, maxAllowed):
    '''
    Finds CPV multiples that do not exceed the number of physical cores.
    '''
    multiples = []
    multiple = cpv
    multiplier = 1
    while multiple <= maxAllowed:
        multiples.append(multiple)
        multiplier += 1
        multiple = cpv * multiplier
        
    return multiples
