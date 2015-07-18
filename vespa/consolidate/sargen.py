'''
Created on Dec 3, 2013

Deals with the temporal data of an application (SAR)
For this, calls sargen-metrics.R for each configuration

@author: giacomo
'''
from consolidate import configutil, configtree, configlist
import os
import subprocess
import sys

def sarAnalyze(appName, appDir, appOutputDir, phycores, configFilename, metricsFilename):
    configDirs = configutil.listAllConfigDirs(appDir)
    configNames = configutil.listAllConfigs(appDir)
    configDict = configlist.enumerateConfigs(configNames)
    
    for configDir in configDirs:
        # Usage: sargen-metrics.R configDir phycores configOutputDir
        
        # config is one of cfg001, cfg002, ...
        (basepath, configName) = os.path.split(configDir)  # @UnusedVariable
        configOutputName = configtree.getConfigOutputName(configName, configDict)
        configOutputDir = appOutputDir + '/' + configOutputName
        
        analyzeSingleConfig(configDir, phycores, configOutputDir)
        
def analyzeSingleConfig(configDir, phycores, configOutputDir):
    
    # get full path of this Python script, the R script is in the same directory
    pathOfThisScript = os.path.dirname(os.path.abspath(__file__))
    rScript = pathOfThisScript + '/sargen-metrics.R'
    vespaPath = pathOfThisScript + '/../../'
    
    # create call list
    sargenArgs = [vespaPath, configDir, phycores, configOutputDir]
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
        
    # work
    sarAnalyze(appName, appDir, appOutputDir, phycores, configFilename, metricsFilename)