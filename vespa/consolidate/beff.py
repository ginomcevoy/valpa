'''
Created on Oct 10, 2014

Creates a CSV file from a set of b_eff output files,
to build a multi-experiment graph.

@author: giacomo
'''

import sys

def allowedTypes():
    '''
    List of data identifiers allowed by the script.
    '''
    return ('compareRingRandom',)

def processExperiments(experimentNames, beffFilenames, outputFilename, dataType='compareRingRandom'):
    'Processes several b_eff.plot outuput files. Assumes same number of data columns in files.'

    if dataType not in allowedTypes():
        raise ValueError('data type not allowed: ', dataType)
    
    columnCount = findDataColumnCount(beffFilenames, dataType)
    
    # write header
    with open(outputFilename, 'w') as outputFile:
        line = 'name,messageSize'
        for i in range(1, columnCount + 1):
            line = line + ',v' + str(i)
        line = line + '\n'
        outputFile.write(line)
    
    # work each experiment
    index = 0
    for experimentName in experimentNames:
        beffFilename = beffFilenames[index]
        appendExperimentData(experimentName, beffFilename, outputFilename, dataType)        
        index = index + 1
        
def findDataColumnCount(beffFilenames, dataType):
    
    # find the number of data columns: read the first file
    firstExpData = readSingleExperiment(beffFilenames[0], dataType)
    
    # data = messageSize v1, v2, .. vn
    dataColumns = len(firstExpData[0]) - 1
    return dataColumns

def appendExperimentData(experimentName, beffFilename, outputFilename, dataType):
    '''
    Reads a b_eff experiment and appends relevant data to output file.
    Output format:
    <experimentName>,<messageSize>,<v1>,<v2>,...,<v9> 
    '''
    # open file
    with open(outputFilename, 'a') as outputFile:
        
        # read the experiment to get data
        beffData = readSingleExperiment(beffFilename, dataType)
        
        # iterate rows and append data
        for beffRow in beffData:
            line = experimentName
            column = 0
            for value in beffRow:
                # first value is the messageSize, should be integer
                if column == 0:
                    value = str(int(value))
                else:
                    value = '%.3f' % value
                line = line + ',' + value
                column = column + 1 
            line = line + '\n'
            outputFile.write(line) 
         
def readSingleExperiment(beffFilename, dataType):
    '''
    Reads the contents of the ouptut of a single experiment
    @return: numerical matrix of the data,
        row = entry, col = [messageSize, v1, v2 ,.. v9] 
    '''
    # open file
    with open(beffFilename, 'r') as beffFile:
        # Read whole text
        beffText = beffFile.read()
    
        # look for the correct data in the file
        if dataType == 'compareRingRandom':
            beffLines = selectCompareRingRandomLines(beffText)
        
        beffMatrix = beffLinesToMatrix(beffLines)
    
    return beffMatrix

def beffLinesToMatrix(beffLines):
    beffRows = []
    for line in beffLines:
        numbers = line.split()
        row = []
        for number in numbers:
            number = float(number)
            row.append(number)
        if len(row) > 0:
            beffRows.append(row)
    return beffRows
            
def selectCompareRingRandomLines(beffText):
    textStartIndex = beffText.find('compare ring & random')
    textEndIndex = len(beffText)
    
    # skip the text line
    beffText = beffText[textStartIndex:textEndIndex]
    beffLines = beffText.split('\n')
    return beffLines[1:len(beffLines)]

if __name__ == '__main__':
    # 
    
    # verify input
    if len(sys.argv) < 4:
        raise ValueError("call: <expCount> {expName1, [expName2, ...]} {beff.plot1, [beff.plot2, ...]} <outputFilename> [compareRingRandom]")
    
    # get count
    expCount = int(sys.argv[1])
    
    # get variables that depend on count
    experimentNames = sys.argv[2:(expCount+2)]
    beffFilenames = sys.argv[(expCount+2):(expCount*2+2)]
    
    outputFilename = sys.argv[(expCount*2+2)]
    if len(sys.argv) > (expCount*2+3):
        dataType = sys.argv[expCount*2+3]
    else:
        dataType = 'compareRingRandom'
        
    processExperiments(experimentNames, beffFilenames, outputFilename, dataType)
    