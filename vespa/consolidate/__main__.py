'''
Created on Dec 4, 2013

Runs all consolidate scripts in order:
0. settings - loads consolidate settings
1. analyzer - creates metrics-app.csv in each config
2. configtree - creates output structure
3. configlist - creates configs.csv in output
4. metricsgen - creates metrics-all.csv output
5. sargen - creates SAR data in output

@author: giacomo
'''
from collections import namedtuple
import sys

from . import settings, analyzer, configtree, configlist, metricsgen,\
    sargen
import bootstrap


def consolidate(appName, configVars, consolidateKey):
    
    # Bootstrap Vespa, get relevant configuration
    bootstrap.doBootstrap(True)
    bootstrapper = bootstrap.getInstance()
    
    consolidateConfig = bootstrapper.getConsolidateConfig(appName)
    
# 
# def analyze(relevantConfig, appName, consolidateKey):
#   
#   appConfig = relevantConfig.appConfig
#   moduleName = consolidatePrefs['']
#   metricsFilename = consolidatePrefs['']
#   
#   for configDir in configDirs:
#     if isMetricFileOutdated(configDir, metricsFilename):
# 
#   with CustomMetricsReader(appConfig, appName, moduleName) as customReader:
#  
    
    # load settings
    settingsInstance = settings.getSettings()
    prefs = settingsInstance.getPrefs()
    
    phycores = prefs['hw.cores']
    baseOutputDir = prefs['generated.dir']
    
    metricsConfig = prefs['metrics.config.name']
    metricsFilename = prefs['metrics.all.name']
    allConfigsFilename = prefs['configs.name']
    
    # load app info
    appSettings = settingsInstance.getInfoForApp(appName)
    appDir = appSettings['app.dir']
    appOutputDir = baseOutputDir + '/' + appName
    
    # call analyzer
    #analyzer.analyzeApplication(appName, appDir, metricsConfig)
    
    # call configtree
    configtree.buildConfigTree(appName, appDir, baseOutputDir)
    
    # call configlist
    configlist.writeConfigsFile(appOutputDir, appDir, configVars, 'config.txt', allConfigsFilename)
    
    # call metricsgen
    metricsOutputFile = appOutputDir + '/' + metricsFilename
    metricsgen.writeMetrics(metricsOutputFile, appDir, metricsConfig)
    
    # call sargen
    sargen.sarAnalyze(appName, appDir, appOutputDir, phycores, 'config.txt'
, metricsConfig)
    
def getConfigVars(varsText):
    return tuple(varsText.split(' ')) # ('nc', 'cpv', ...)

if __name__ == '__main__':
    
    # Validate input
    args = len(sys.argv) - 1
    if args < 2:
        raise ValueError('Usage: runall <appName> <"configVars"> [consolidateKey]')
    
    # Mandatory inputs
    appName = sys.argv[1]
    varsText = sys.argv[2]
    configVars = getConfigVars(varsText)
    
    # consolidateKey is optional value
    consolidateKey = None
    if args > 2:
        consolidateKey = sys.argv[3]
    
    # do the work
    consolidate(appName, configVars, consolidateKey)
