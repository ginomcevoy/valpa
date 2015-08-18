'''
Created on Dec 4, 2013

Runs all consolidate scripts in order:
1. analyzer - creates metrics-app.csv in each config
2. configtree - creates output structure
3. configlist - creates configs.csv in output
4. metricsgen - creates metrics-all.csv output
5. sargen - creates SAR data in output

@author: giacomo
'''
import os
import sys

from . import analyzer, configtree, configlist, metricsgen,\
    sargen
import bootstrap
from consolidate import configutil

def consolidate(consolidateConfig, appName, configVars, consolidateKey):
    
    # TODO: all of these parameters should be hidden within the function calls
    # using consolidateConfig to hold parameters
    
    # relevant input directory for request
    appInputDir = configutil.appInputDir(consolidateConfig.appParams, consolidateKey)
    
    # application-specific directory for experiment consolidation
    # is a sub-directory from base output directory
    baseOutputDir = consolidateConfig.consolidateParams['generated_dir']
    baseOutputDir = os.path.expandvars(baseOutputDir)  # may have $HOME environment variable

    # output dir, use consolidateKey if available
    # TODO: put this in a proper function
    outputName = appName if consolidateKey is None else "-".join((appName, consolidateKey))
    appOutputDir = baseOutputDir + '/' + outputName
    
    # filename for main output: all configurations
    allConfigsFilename = consolidateConfig.consolidateParams['consolidate_configs_all'] 
    
    # filename for main output: all metrics
    metricsFilename = consolidateConfig.consolidateParams['consolidate_metrics_all']
    
    # filename for intermediary output: metrics for each configuration
    metricsConfig = consolidateConfig.consolidateParams['consolidate_metrics_same']  
    
    # physical cores per physical machine...
    phycores = str(consolidateConfig.hwSpecs['cores'])
    
    # call analyzer: analyze each configuration
    analyzer.analyze(consolidateConfig, appName, consolidateKey)
    
    # call configtree: create output tree to hold temporal metrics
    configtree.buildConfigTree(appInputDir, appOutputDir)
    
    # call configlist: write main output - configurations
    # writeConfigsFile(appOutputDir, appDir, configVars, configFilename, allConfigsFilename)
    configlist.writeConfigsFile(appOutputDir, appInputDir, configVars, 'config.txt', allConfigsFilename)
    
    # call metricsgen: write main output - metrics
    metricsOutputFile = appOutputDir + '/' + metricsFilename
    metricsgen.writeMetrics(metricsOutputFile, appInputDir, metricsConfig)
    
    # call sargen: analyze temporal metrics for each configuration
    sargenConfig = consolidateConfig.consolidateParams['consolidate_sargen_config']
    sargen.sarAnalyze(appName, appInputDir, appOutputDir, phycores, 'config.txt',
                      metricsConfig, sargenConfig)
    
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
        
    # Bootstrap Vespa, get relevant configuration
    bootstrap.doBootstrap(True)
    bootstrapper = bootstrap.getInstance()
    consolidateConfig = bootstrapper.getConsolidateConfig(appName)
        
    # do the work
    consolidate(consolidateConfig, appName, configVars, consolidateKey)
