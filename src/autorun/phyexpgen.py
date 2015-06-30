'''
Created on May 2, 2014

@author: giacomo
'''

import jinja2
import os

from bean.enum import MPIBindOpt

class PhysicalExperimentGenerator(object):
    '''
    Generates experiments on a virtual cluster
    '''

    def __init__(self, allNodes):
        '''
        Constructor
        '''
        self.allNodes = allNodes
        self.nodeCount = len(allNodes.getNames())
        
        # setup jinja template
        templateLoader = jinja2.FileSystemLoader(searchpath="../templates/")
        templateEnv = jinja2.Environment(loader=templateLoader, keep_trailing_newline=True)
        self.template = templateEnv.get_template('builder-physical.template')
        
    def withCPVs(self, cpvs):
        '''
        Indicates tuple with possible cpv values
        '''
        self.cpvs = cpvs
        return self
    
    def withNCs(self, ncs):
        '''
        Indicates tuple with possible nc values
        '''
        self.ncs = ncs
        return self
    
    def withMPIBinds(self, binds = [MPIBindOpt.BIND_CORE, MPIBindOpt.BIND_SOCKET, MPIBindOpt.NONE]):
        '''
        Indicates tuple with possible MPIBindOpt values
        '''
        self.binds = binds
        return self
    
    def generateCombinations(self, inGroups=False):
        '''
        Generates possible combinations given hardware.
        @boolean inGroups: if True, separate for multiple XML files
        '''
        self.combinations = [] # list of tuples
        self.inGroups = inGroups
        
        # iterate all cpv/nc, find possible
        # rule 1: nc must be multiple of cpv
        # rule 2: nc/cpv (number of physical machines) <= # physical nodes
        for cpv in self.cpvs:
            for nc in self.ncs:
                # check conditions
                residue = nc % cpv
                requiredNodes = nc / cpv # inexact will be ignored
                if (residue == 0 and requiredNodes <= self.nodeCount):
                    # add combination
                    self.combinations.append((nc, cpv))
                
        # now all combinations are generated
        if inGroups:
            # create groups, grouping by cpv for balance
            self.groups = {}
            for comb in self.combinations:
                key = str(comb[1])
                if key not in self.groups.keys(): 
                    self.groups[key] = [comb]
                else:
                    self.groups[key].append(comb)
        else:
            # a single group will all combinations
            self.groups = {'all' : self.combinations}
            
    def generateXMLs(self, appInfo, xmlPath):
        '''
        Generates one XML per grouping, with all MPIBindOpt values
        '''
        if not os.path.exists(xmlPath):
            os.makedirs(xmlPath)
        xmlNames = []
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
        
        if self.inGroups:
            # if grouped by cpv, then all experiments in 
            # experimentList have the same cpv 
            cpv = experimentList[0][1]
            nameSuffix = '-cpv' + str(cpv) + '.xml'
        else:
            nameSuffix = '-all.xml'
        xmlName = xmlPath + '/' + appName + nameSuffix
        xmlFile = open(xmlName, 'w')    
        
        # iterate experiment items in group
        for experiment in experimentList:
            
            nc = experiment[0]
            cpv = experiment[1]
            
            # iterate MPIBind options
            for mpiBind in self.binds:
                
                # This is specific to experiment
                expName =  'nc' + str(nc) + '-cpv' + str(cpv) + '-pp' + str(mpiBind)
                    
                # special case for arguments 
                appArgs = self.setSpecialArguments(appName, appArgs, nc, cpv)
                    
                # Use template, with all local variables set
                text = self.template.render(locals())
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
    