'''
Created on Nov 30, 2013

Writes a configs.csv containing a frame with the info
<num> <sha> <nc> <cpv> ....
 1    sha1  ...
 2    sha2  ...

@author: giacomo
'''

import math
import csv
import sys

from datagen.configutil import listAllConfigDirs
from datagen import configutil
from os import path

def enumerateConfigs(configNames):
    '''
    Returns a dictionary in the form {sha1 : 0001, sha2 : 0002}
    The amount of zeros is the minimum required for all the data
    '''
    output = {}
    configCount = len(configNames)
    padding = int(math.log10(configCount) + 1) # number width
    
    for i in range(configCount):
        config = configNames[i]
        numberString = "{number:0{width}d}".format(width=padding, number=i+1)
        output[config]  = numberString
        
    return output

def writeConfigsFile(appOutputDir, appDir, configVars, configFilename, allConfigsFilename): # ='configs.csv'
    '''
    Writes the configs.csv file
    '''
    configNames = configutil.listAllConfigs(appDir)
    configDict = enumerateConfigs(configNames)
    
    # open with csv writer
    with open(appOutputDir + '/' + allConfigsFilename, 'w') as output:
        
        csvWriter = csv.writer(output, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # Write headers
        header = ['num', 'config']
        header.extend(configVars)
        csvWriter.writerow(header)
        
        # Iterate configs and write data
        configDirs = listAllConfigDirs(appDir)
        for configDir in configDirs:
            writeConfigEntry(csvWriter, configDir, configVars, configDict, configFilename)

    
def writeConfigEntry(csvWriter, configDir, configVars, configDict, configFilename):
    
    # get values for the variables
    configParams = configutil.getConfigParams(configDir, configVars, configFilename)
    
    # get config info for this config
    (useless, configName) = path.split(configDir)  # @UnusedVariable
    configNumber = configDict[configName]
    
    # build row
    row = [configNumber, configName]
    for configVar in configVars:
        row.append(configParams[configVar])
    
    # write row as CSV
    csvWriter.writerow(row)
    
def getConfigVars(varsText):
    return tuple(varsText.split(' ')) # ('nc', 'cpv', ...)

if __name__ == '__main__':
    
    # Validate input
    args = len(sys.argv) - 1
    if args < 2:
        raise ValueError('Usage: configlist <appDir> <"configVars"> [outputDir=appDir] [configFilename=config.txt] [outputFile=configs.csv]')
    
    # Mandatory inputs
    appDir = sys.argv[1]
    varsText = sys.argv[2]
    configVars = getConfigVars(varsText)
    
    # Optional inputs
    if args > 2:
        outputDir = sys.argv[3]
    else:
        outputDir = appDir
        
    if args > 3:
        configFilename = sys.argv[4]
    else:
        configFilename = 'config.txt'
        
    if args > 4:
        outputFile = sys.argv[5]
    else:
        outputFile = 'configs.csv'
    
    # do the work
    writeConfigsFile(outputDir, appDir, configVars, configFilename, outputFile)
