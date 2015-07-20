'''
Created on Nov 30, 2013

Generates a single file with all final execution metrics for all configs
Uses config numbers: <config> <appTime> ... 

@author: giacomo
'''
import os.path
import csv
import sys

from . import configutil, configlist

def writeMetrics(outputFile, appDir, metricsFilename):
    
    # get all config dirs and the config numbers
    configDirs = configutil.listAllConfigDirs(appDir)
    configNames = configutil.listAllConfigs(appDir) 
    configDict = configlist.enumerateConfigs(configNames)
    
    # header with column names
    header = ['config']
    
    # Open first CSV to generate rest of column names
    firstCsvFile = configDirs[0] + '/' + metricsFilename
    with open(firstCsvFile, 'r') as firstCsv:
        csvReader = csv.reader(firstCsv, delimiter=';', quotechar='|')
        first = True
        for row in csvReader:
            if first:
                header.extend(row)
                first = False
        
        firstCsv.close()
    
    # Begin writing output
    with open(outputFile, 'w') as csvOutput:
        csvWriter = csv.writer(csvOutput, delimiter=';',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)

        # Write header
        csvWriter.writerow(header)
    
        # iterate config dirs to add data
        for configDir in configDirs:
            writeMetricsOneConfig(csvWriter, configDir, configDict, metricsFilename)
        
        csvOutput.close()

def writeMetricsOneConfig(csvWriter, configDir, configDict, metricsFilename): #='metrics-app.csv'
    '''
    Writes metrics from a single config into output file
    '''
    # first entry is the config number
    (basepath, configName) = os.path.split(configDir)  # @UnusedVariable
    configNumber = configDict[configName]

    # rest of entries are the data
    # open the metrics-app.csv data file
    csvFile = configDir + '/' + metricsFilename
    #print(csvFile)
    
    with open(csvFile, 'r') as csvHandle:
        csvReader = csv.reader(csvHandle, delimiter=';', quotechar='|')

        first = True
        for row in csvReader:
            
            # skip header
            if first:
                first = False
                continue 

            # add rows to output
            helpRow = [configNumber]
            helpRow.extend(row)
            csvWriter.writerow(helpRow)

if __name__ == '__main__':
    # Validate input
    args = len(sys.argv) - 1
    if args < 1:
        raise ValueError('Usage: metricsgen <appDir> [outputDir=appDir] [outputFilename=all-metrics.csv] [metricsFilename=metrics-app.csv]')
    
    # Mandatory inputs
    appDir = sys.argv[1]
    
    # Optional inputs
    if args > 1:
        outputDir = sys.argv[2]
    else:
        outputDir = appDir
        
    if args > 2:
        outputFilename = sys.argv[3]
    else:
        outputFilename = 'all-metrics.csv'
        
    if args > 3:
        metricsFilename = sys.argv[4]
    else:
        metricsFilename = 'metrics-app.csv'
        
    # work
    outputFile = outputDir + '/' + outputFilename
    writeMetrics(outputFile, appDir, metricsFilename)