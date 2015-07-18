'''
Created on Nov 30, 2013

Creates the required directory structure for application data
<experiments = outputDir>
   <appName>
       <cfg001> 
       <cfg002>
          config.txt
          topology.txt
          ...
       ...

@author: giacomo
'''
import sys
import os
from datagen import configlist, configutil
import subprocess

def buildConfigTree(appName, appDir, outputDir):
    
    # make app output dir 
    appOutputDir = outputDir + '/' + appName
    if not os.path.exists(appOutputDir):
        os.makedirs(appOutputDir)
    
    # get all config dirs and the config numbers
    configDirs = configutil.listAllConfigDirs(appDir)
    configNames = configutil.listAllConfigs(appDir) 
    configDict = configlist.enumerateConfigs(configNames)
    
    # make config output dirs
    buildConfigDirs(configNames, configDict, appOutputDir)
    
    # iterate config dirs
    for configInputDir in configDirs:
        # get value for configOutputDir
        (basepath, configName) = os.path.split(configInputDir)  # @UnusedVariable
        configOutputName = getConfigOutputName(configName, configDict)
        configOutputDir = appOutputDir + '/' + configOutputName
        
        # copy relevant files for this config
        copyFiles(configInputDir, configOutputDir)

def buildConfigDirs(configNames, configDict, appOutputDir):
    for configName in configNames:
        configOutputName = getConfigOutputName(configName, configDict)
        configOutputDir = appOutputDir + '/' + configOutputName
        if not os.path.exists(configOutputDir):
            os.makedirs(configOutputDir)

def copyFiles(configInputDir, configOutputDir):
    # use shell script for this
    copyCall = ['/bin/bash', 'datagen/copyConfigFiles.sh', configInputDir, configOutputDir]
    subprocess.call(copyCall)

    # create a file named 'identifier.txt' with the dist + config name
    (basePath, configName) = os.path.split(configInputDir)
    (otherBasePath, distName) = os.path.split(basePath)  # @UnusedVariable
    outputFilename = configOutputDir + '/identifier.txt'
    with open(outputFilename, 'w') as output:
        output.write(distName + '/' + configName + '\n')
        output.close()

def getConfigOutputName(configName, configDict):
    configNumber = configDict[configName]
    configOutputName = 'cfg' + configNumber
    return configOutputName

if __name__ == '__main__':
    # Validate input
    args = len(sys.argv) - 1
    if args < 3:
        raise ValueError('Usage: configtree <appName> <appDir> <outputDir>')
    
    # Mandatory inputs
    appName = sys.argv[1]
    appDir = sys.argv[2]
    outputDir = sys.argv[3]
    
    # work
    buildConfigTree(appName, appDir, outputDir)
