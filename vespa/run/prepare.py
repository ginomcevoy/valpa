'''
Created on Oct 31, 2013

Prepares application execution

@author: giacomo
'''

import io
import hashlib
import jinja2
import os
from util import uuid

class PreparesExperiment:
    
    def __init__(self, forReal, vespaPrefs, runOpts):
        self.generator = ConfigFileGenerator(forReal, vespaPrefs, runOpts) 
    
    def prepare(self, clusterInfo, deploymentInfo, appInfo):
        (execConfig, distPath) = self.generator.createExecConfig(clusterInfo, deploymentInfo, appInfo)
        
        # create experimentPath using distPath/<config hash>
        theHash = self.configHash(execConfig)
        experimentPath = distPath + os.path.sep + theHash
        if not os.path.exists(experimentPath):
            os.makedirs(experimentPath)
        
        # save config.txt in experimentPath
        self.generator.saveTrimmedExecConfig(execConfig, experimentPath)
        
        # save topology.txt in distPath
        self.saveTopology(clusterInfo, distPath)
        
        return (execConfig, experimentPath)

    def configHash(self, execConfigFile):
        with io.open(execConfigFile, 'r', encoding='utf-8') as execConfig:
            text = execConfig.read()
            return hashlib.sha256(text.encode('utf-8')).hexdigest()
        
    def saveTopology(self, clusterInfo, distPath):
        #Example output:
        #C=16
        #V=4
        #H=2
        c = clusterInfo.topology.nc
        v = int(c / clusterInfo.topology.cpv)
        h = 1 # if df = 0
        idf = clusterInfo.mapping.idf
        if idf > 0:
            h = int(c / clusterInfo.mapping.idf)
            
        outputFile = distPath + os.path.sep + 'topology.txt'
        with open(outputFile, 'w') as output:
            output.write('C=' + str(c) + '\n')
            output.write('V=' + str(v) + '\n')
            output.write('H=' + str(h))
            
        return outputFile
        
class ConfigFileGenerator:
    
    def __init__(self, forReal, vespaPrefs, runOpts):
        self.forReal = forReal
        self.vespaPrefs = vespaPrefs
        self.runOpts = runOpts
        
        # setup jinja template
        templateLoader = jinja2.FileSystemLoader(searchpath="../templates")
        templateEnv = jinja2.Environment(loader=templateLoader, keep_trailing_newline=True)
        self.template = templateEnv.get_template(self.vespaPrefs['exec_config_template'])
        
    def createExecConfig(self, clusterInfo, deploymentInfo, appInfo):
        '''
        Creates an execution config file based on a template. Template and output are
        specified in vespaPrefs
        '''
        (deployedNodes, deployedSockets, deployedVMs) = deploymentInfo
        
        # fix deployed
        deployedNodesText= self.__tupleToText__(deployedNodes.getNames())
        deployedSocketsText= self.__tupleToText__(deployedSockets)
        
        # add vmCount, hostCount 
        vmCount = len(deployedVMs.getNames())
        hostCount = len(deployedNodes.getNames())
        
        # calculate deployment dir
        expDir = self.runOpts['exp_dir']
        
        distDir = self.runOpts['deploy_subdir_pattern']
        distDir = distDir.replace('&NC', str(clusterInfo.topology.nc))
        distDir = distDir.replace('&CPV', str(clusterInfo.topology.cpv))
        distDir = distDir.replace('&IDF', str(clusterInfo.mapping.idf))
        distDir = distDir.replace('&PSTRAT', str(clusterInfo.mapping.pinningOpt))
        
        distPath = self.runOpts['deploy_dir_pattern']
        distPath = distPath.replace('&EXPDIR', expDir)
        distPath = distPath.replace('&APP', appInfo.name)
        distPath = distPath.replace('&DEPLOYSUBDIR', distDir) 
        
        # add verbose
        verbose = self.vespaPrefs['general_verbose']
        
        # output file = <exec.config.output>/<uuid>
        execConfigName = uuid.newUUID(self.forReal)
        execConfigDir = self.vespaPrefs['exec_config_output']
        execConfigFilename = execConfigDir + '/' + execConfigName
        print(execConfigFilename)
        if not os.path.exists(execConfigDir):
            os.makedirs(execConfigDir)
        
        execConfigFile = open(execConfigFilename, 'w')
        
        # write output using template
        text = self.template.render(locals())
    
        execConfigFile.write(text)
        execConfigFile.close()
        
        # return filename and distPath
        return (execConfigFilename, distPath)
        
    def saveTrimmedExecConfig(self, configFile, outputPath):
        
        # open file and read text
        with open(configFile, 'r') as config:
            configText = config.read()
            pieces = configText.split('#!#')
            
            outputFilename = outputPath + os.path.sep + 'config.txt'
            with open(outputFilename, 'w') as output:
                output.write(pieces[0]) 
            
        return outputFilename
    
    def __tupleToText__(self, aTuple):
        output = ''
        for item in aTuple:
            output += str(item) + ','
        return output[0:len(output)-1]
        
        