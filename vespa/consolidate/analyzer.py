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
from consolidate.plugin import CustomMetricsReader


#def analyzeApplication(appName, appDir, metricsFilename):
def analyze(relevantConfig, appName, consolidateKey):
    
    # filenames: partial output, user-specific module and time output
    metricsFilename = relevantConfig.consolidatePrefs['consolidate_metrics_same']
    moduleName = relevantConfig.consolidatePrefs['read_output']
    timeFilename = relevantConfig.runOpts['run_timeoutput']
    
    # get the relevant input directory for request, iterate subfolders
    inputDir = configutil.appInputDir(relevantConfig.appParams, consolidateKey)
    configDirs = configutil.listAllConfigDirs(inputDir)
    
    for configDir in configDirs:
        
        # if metrics file is ok, no need to analyze
        if isMetricFileOutdated(configDir, metricsFilename):
            
            # analyze the file with the data derived from time command
            timeMetrics = getTimeMetrics(configDir, timeFilename)
            
            # analyze with application-specific module
            customMetrics = getCustomMetrics(relevantConfig, moduleName, configDir)
                    
#             # analyze this config: use application-specific shell script
#             script = 'consolidate/apps/' + appName + '/metrics-config.sh'
#             
#             # contingency
#             if not os.path.exists(script):
#                 print('Need application specific script to analyze output: ' + script)
#                 exit(1)
#             
#             # call script
#             analyzeCall = ['/bin/bash', script, configDir, configDir, metricsFilename]
#             subprocess.call(analyzeCall)
            
def getTimeMetrics(configDir, timesFilename):
    """ Return a dictionary with the output from time command.
    
    Current keys: userTime, systemTime, ellapsedTime
    """
    # output format
    metrics = {'userTime' : [], 'systemTime' : [], 'ellapsedTime' : []}
    
    # read file in lines
    timesFile = os.path.join(configDir, timesFilename)
    with open(timesFile, 'r') as times:
        lineCounter = 0
        for line in times:
            # each 3rd line has the metrics
            lineCounter = lineCounter + 1
            if (lineCounter % 3 != 0):
                continue
            
            # assuming order userTime / systemTime / ellapsedTime
            user, system, ellapsed = line.split('\t')
            user, system, ellapsed = float(user), float(system), float(ellapsed)
            metrics['userTime'].append(user)
            metrics['systemTime'].append(system)
            metrics['ellapsedTime'].append(ellapsed)
    
    metrics['userTime'] = tuple(metrics['userTime'])
    metrics['systemTime'] = tuple(metrics['systemTime'])
    metrics['ellapsedTime'] = tuple(metrics['ellapsedTime'])
    
    return metrics
    
def getCustomMetrics(relevantConfig, moduleName, configDir):
    """ Return a dictionary with application-specific metrics.
    
    The dictionary has unspecified keys. For each key, a tuple is expected,
    where the length of the tuple is the number of repeated experiments for
    the configuration. If there is no user module, the output dictionary will
    be empty. 
    
    """
    
    customMetrics = {}
    customFilename = relevantConfig.appParams['exec.outputrename']
    customFile = None
    
    # load user module for application-specific metrics
    # if there is no user module, the dictionary remains empty
    with CustomMetricsReader(relevantConfig.appParams, moduleName) as cr:
        
        # iterate experiments within each configuration
        expDirs = configutil.getSubDirs(configDir)
        for expDir in expDirs:
            
            # main output files
            stdoutFile = os.path.join(expDir, 'std.out')
            stderrFile = os.path.join(expDir, 'std.err')
            
            # work optional custom file
            if customFilename.strip():    
                customFile = open(customFilename, 'r')
                
            # module reads 
            #cr.read_metrics(stdout, stderr, expDir, customFile=None)
                
    return customMetrics 
            
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
