'''
Created on Dec 3, 2013

Deals with the temporal data of an application (SAR)
For this, calls sargen-metrics.R for each configuration

@author: giacomo
'''

import os
import subprocess
import sys

from . import configutil, configtree, configlist

def sarAnalyze(appName, appDir, appOutputDir, phycores, configFilename, metricsFilename, sargenConfig):
    configDirs = configutil.listAllConfigDirs(appDir)
    configNames = configutil.listAllConfigs(appDir)
    configDict = configlist.enumerateConfigs(configNames)
    
    for configDir in configDirs:
        # Usage: sargen-metrics.R configDir phycores configOutputDir
        
        # config is one of cfg001, cfg002, ...
        (basepath, configName) = os.path.split(configDir)  # @UnusedVariable
        configOutputName = configtree.getConfigOutputName(configName, configDict)
        configOutputDir = appOutputDir + '/' + configOutputName
        
        analyzeSingleConfig(configDir, phycores, configOutputDir, sargenConfig)
        
def analyzeSingleConfig(configDir, phycores, configOutputDir, sargenConfig):
    
    # get full path of this Python script, the R script is in the same directory
    pathOfThisScript = os.path.dirname(os.path.abspath(__file__))
    rScript = pathOfThisScript + '/sargen-metrics.R'
    vespaPath = pathOfThisScript + '/../../'
    
    # variables may have $HOME environment variable
    sargenConfig = os.path.expandvars(sargenConfig)
    configOutputDir =  os.path.expandvars(configOutputDir)
    
    # create call list
    sargenArgs = [vespaPath, sargenConfig, configDir, phycores, configOutputDir]
    sargenCall = ['r', rScript]
    sargenCall.extend(sargenArgs)
    
    # make call
    subprocess.call(sargenCall)

if __name__ == '__main__':
    # Validate input
    args = len(sys.argv) - 1
    if args < 3:
        raise ValueError('Usage: sargen <appName> <appDir> <phycores> [appOutputDir=appDir]')
    
    # Mandatory inputs
    appName = sys.argv[1]
    appDir = sys.argv[2]
    phycores = sys.argv[3]
    
    # Optional input
    if args > 3:
        appOutputDir = sys.argv[4]
    else:
        appOutputDir = appDir
        
    if args > 4:
        configFilename = sys.argv[5]
    else:
        configFilename = 'config.txt'
        
    if args > 5:
        metricsFilename = sys.argv[6]
    else:
        metricsFilename = 'metrics-app.csv'
        
    sargenConfig = 'input/sargen-config.R'
        
    # work
    sarAnalyze(appName, appDir, appOutputDir, phycores, configFilename, metricsFilename, sargenConfig)