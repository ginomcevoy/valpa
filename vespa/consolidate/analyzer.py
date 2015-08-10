'''
Created on Dec 3, 2013

Creates metrics-app.csv for each configuration, and stores it in the same
config directory. Uses application-specific metrics-config.sh. 
Skips configs that already have a metrics-app.csv that are newer than all
of the execution dirs

@author: giacomo
'''

import csv
import os.path

from . import configutil
from .plugin import CustomReaderLoader
from collections import OrderedDict
import itertools
import warnings

def analyze(consolidateConfig, appName, consolidateKey, override=False):
    
    # filenames: partial output, user-specific module, time output
    metricsFilename = consolidateConfig.consolidatePrefs['consolidate_metrics_same']
    timeFilename = consolidateConfig.runOpts['run_timeoutput']
    
    # get the relevant input directory for request, iterate subfolders
    appInputDir = configutil.appInputDir(consolidateConfig.appParams, consolidateKey)
    configDirs = configutil.listAllConfigDirs(appInputDir)
    
    for configDir in configDirs:
        
        # if metrics file is up-to-date, no need to analyze unless forced
        if override or isMetricFileOutdated(configDir, metricsFilename):
            
            # analyze the file with the data derived from time command
            timeMetrics = getTimeMetrics(configDir, timeFilename)
            
            # analyze with application-specific module
            appMetrics = getAppMetrics(consolidateConfig, configDir)
            
            if appMetrics is None:
                # no module found for application metrics
                allMetrics = timeMetrics
            else:
                # validate consistency of metrics
                if not areConsistent(appMetrics, timeMetrics):
                    raise ValueError("Experiment metrics don't match:", configDir)
                
                # metrics consistent, merge these metrics in order
                allMetrics = OrderedDict(timeMetrics.items() + appMetrics.items())
            
            # save the available metrics
            metricsFile = os.path.join(configDir, metricsFilename)
            metricsToCSV(metricsFile, allMetrics)
                    
def metricsToCSV(metricsFile, allMetrics):
    """ Generates a CSV file with the times data and application data (if any). """

    with open(metricsFile, 'wb') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        # write header: names of metrics
        # if using OrderedDict, column order is preserved 
        csvWriter.writerow(allMetrics.keys())
        
        # write each row: this idiom creates an iterator through all the lists
        # in the allMetrics dictionary, which allows the iteration by row.
        rowIter = itertools.imap(lambda *x: list(x), *allMetrics.itervalues())
        for row in rowIter:
            csvWriter.writerow(row)
        
def getTimeMetrics(configDir, timesFilename):
    """ Return an ordered dictionary with the output from time command.
    
    Current keys: userTime, systemTime, ellapsedTime
    """
    # output format
    items = (('userTime', []), 
             ('systemTime', []),
             ('ellapsedTime', [])
             )
    metrics = OrderedDict(items)
    
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
    
    return OrderedDict(metrics)
    
def getAppMetrics(consolidateConfig, configDir):
    """ Return a dictionary with application-specific metrics.
    
    The dictionary has unspecified keys. For each key, a tuple is expected,
    where the length of the tuple is the number of repeated experiments for
    the configuration. If there is no user module, the output is None.
    
    """
    
    appMetrics = {}
    moduleName = consolidateConfig.consolidatePrefs['consolidate_module']
    customFilename = consolidateConfig.appParams['exec.outputrename']
    
    # load user module for application-specific metrics
    # if there is no user module, the dictionary remains empty
    with CustomReaderLoader(consolidateConfig.appParams, moduleName) as crl:
        
        reader = crl.loadModule()
        
        # iterate experiments within each configuration
        expDirs = configutil.getSubDirs(configDir)
        for expDir in expDirs:
            
            # main output files
            expDir = os.path.join(configDir, expDir)
            stdoutFile = os.path.join(expDir, 'std.out')
            stderrFile = os.path.join(expDir, 'std.err')
            customFile = os.path.join(expDir, customFilename)
            
            # work optional custom file
            cf = open(customFile, 'r') if customFilename.strip() else None
            
            with open(stdoutFile, 'r') as stdout, open(stderrFile, 'r') as stderr:
                # module reads 
                customMetrics = reader.read_metrics(stdout, stderr, expDir, cf)
                
                # convert the customMetrics dictionary to a dictionary of lists
                # each list has one element
                metricsAsList = {}
                for k, v in customMetrics.items():
                    metricsAsList[k] = [v,] 
                
                # aggregate output for each experiment
                if not appMetrics:
                    # handle special case for first experiment
                    appMetrics = metricsAsList
                else: 
                    # this idiom aggregates dictionaries of lists, maintaining structure
                    keys = appMetrics.keys()
                    appMetrics = dict((k, appMetrics.get(k, []) + metricsAsList.get(k, [])) for k in keys)
                    
    # module not found, there are no appMetrics
    if not crl.loaded:
        appName = consolidateConfig.appParams['app.name']
        warnings.warn('User module not loaded for: ' + appName)
        return None                
    else:
        return appMetrics 
            
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

def areConsistent(appMetrics, timeMetrics):
    """ Indicate consistency between appMetrics and timeMetrics.
    
    The verification is done by the size of each metrics, the number of
    experiment tuples should be the same. Returns True iff verification
    succeeds. 
    
    """
    appLen = 0
    timeLen = 0
    
    for metricType in appMetrics.values():
        thisAppLen = len(metricType)
        if appLen == 0:
            appLen = thisAppLen
        elif appLen != thisAppLen: # different length within appMetrics
            return False 
        
    for metricType in timeMetrics.values():
        thisTimeLen = len(metricType)
        if timeLen == 0:
            timeLen = thisTimeLen
        elif timeLen != thisTimeLen: # different length within timeMetrics
            return False
    
    return appLen == timeLen
