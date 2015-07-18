'''
Created on Dec 3, 2013

Creates metrics-app.csv for each configuration, and stores it in the same
config directory. Uses application-specific metrics-config.sh. 
Skips configs that already have a metrics-app.csv that are newer than all
of the execution dirs

@author: giacomo
'''

import os.path
import subprocess
import sys

from . import configutil


def analyzeApplication(appName, appDir, metricsFilename):
    
    # iterate all configs
    configDirs = configutil.listAllConfigDirs(appDir)
    
    for configDir in configDirs:
        
        # if metrics file is ok, no need to analyze
        if isMetricFileOutdated(configDir, metricsFilename):
                    
            # analyze this config: use application-specific shell script
            script = 'datagen/apps/' + appName + '/metrics-config.sh'
            
            # contingency
            if not os.path.exists(script):
                print('Need application specific script to analyze output: ' + script)
                exit(1)
            
            # call script
            analyzeCall = ['/bin/bash', script, configDir, configDir, metricsFilename]
            subprocess.call(analyzeCall)
            

def isMetricFileOutdated(configDir, metricsFilename):
    
    metricsFile = os.path.join(configDir, metricsFilename)
    
    # trivial case: no metrics file, then answer with outdated
    if not os.path.exists(metricsFile):
        return True
    
    # reference time
    metricTime = os.path.getmtime(metricsFile)
    
    execDirs = configutil.getSubDirs(configDir) 
    for execDir in execDirs:
        # if any of these is newer (larger), then metric is outdated
        execTime = os.path.getmtime(os.path.join(configDir, execDir))
        if execTime > metricTime:
            print('metricsFilename in ' + configDir + ' is outdated')
            return True
    
    # execDirs are older, metrics file is ok
    return False

if __name__ == '__main__':
    # Validate input
    args = len(sys.argv) - 1
    if args < 2:
        raise ValueError('Usage: configtree <appName> <appDir> [metricsFilename=metrics-app.csv]')
    
    # Mandatory inputs
    appName = sys.argv[1]
    appDir = sys.argv[2]
    
    # Optional input
    if args > 2:
        metricsFilename = sys.argv[3]
    else:
        metricsFilename = 'metrics-app.csv'
        
    # work
    analyzeApplication(appName, appDir, metricsFilename)
