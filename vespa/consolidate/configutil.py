'''
Created on Nov 30, 2013

####Gathers different CSV for application metrics (made with fuseAppMetrics.py) into a single one
Utility functions for working with data from configurations
Extracts information about DIST variables

@author: giacomo
'''

import os

def appInputDir(appParams, consolidateKey):
	"""Return the full path for the consolidation input of a request.
	
	By default, the application has a single input folder, given by
	consolidate.default parameter in the application params. This can
	be overridden by using a key. If key is present, the path is retrieved
	from the consolidate.<key> parameter in the config. 
	
	An exception is raised if the key is not present in the config.
	  
	"""
	if consolidateKey is None:
		return appParams['consolidate.default']
	else:
		key = 'consolidate.' + consolidateKey
		return appParams[key]

def getSubDirs(baseDir, orderByModification=True):
	'''
	Returns a tuple of all subdirs within baseDir (non-recursive). The list is
	ordered by modification date (oldest first)
	'''
	output = {}
	
	# get subdirs only, use modification date as value for a dictionary
	# subdirs must have different names, hence used as keys
	for entry in os.listdir(baseDir):
		entryPath = os.path.join(baseDir, entry)
		if os.path.isdir(entryPath):
			
			# get modification date of this subdir, and add to dictionary
			modifDate = os.path.getmtime(entryPath)
			output[entry] = modifDate
			
	# remove '.svn' subdir, not interesting
	if '.svn' in output.keys():
		output.pop('.svn')
			
	# sort by modification date (value of the dict), returns list of keys
	if orderByModification:
		return sorted(output, key=output.get)
	else:
		# just order by the subdir names
		names = output.keys()
		return sorted(names)
	
def getConfigParams(configDir, configVars, configFilename='config.txt'):
	'''
	Returns the value of the config parameters (configVars tuple) 
	in the file configDir/config.txt 
	'''
	output = {}
	configFilename = configDir + '/' + configFilename
	with open(configFilename, 'r') as configFile:
		# read each parameter
		configContents = configFile.read()
		for configVar in configVars:
			output[configVar] = readValue(configContents, configVar)
	return output

def listAllConfigDirs(appDir):
	'''
	Returns a tuple with all the config directories (full path)
	within an application dir. 
	'''
	output = []
	
	# get all dist dirs, and all configs within each dist
	distDirs = getSubDirs(appDir)
	for distDir in distDirs:
		configDirs = getSubDirs(appDir + '/' + distDir)
		for configDir in configDirs:
			output.append(appDir + '/' + distDir + '/' + configDir)
			
	return (output)

def listAllConfigs(appDir):
	'''
	Returns a tuple with all the config names within an application dir. 
	'''
	output = []
	
	# get all config dirs
	configDirs = listAllConfigDirs(appDir)
	for configDir in configDirs:
		(path, configName) = os.path.split(configDir)  # @UnusedVariable
		output.append(configName)

	return (output)

	
def readValue(configContents, configVar):		
	# words is <name>=, look for it and read value
	word = configVar + '='
	varIndex = configContents.find(word)
	endLine = configContents.find('\n', varIndex)
	return configContents[varIndex + len(word) : endLine]
# 	
# def getDataRows(configDir, csvFilename='metrics-app.csv'):
# 	csvFile = configDir + '/' + csvFilename
# 	return open(csvFile, 'r').read()
# 
# def writeMetrics(appDir, configVars, configFilename='config.txt', csvFilename='metrics-app.csv', outputCsv='dataset.csv'):
# 	
# 	configDirs = listAllConfigDirs(appDir)
# 	first = True
# 	
# 	with open(appDir + '/' + outputCsv, 'w') as outputHandle:
# 	
# 		for configDir in configDirs: 
# 			configParams = getConfigParams(configDir, configVars, configFilename)
# 			configDataRows = getDataRows(configDir, csvFilename)
# 				
# 			# special case for first entry: write columns
# 			if first:
# 				writeColumns(outputHandle, configParams, configDataRows)
# 				first = False
# 					
# 			# write rows for each config set
# 			writeMetricsConfig(outputHandle, configParams, configDataRows)
# 			
# 		outputHandle.close()
# 
# def writeColumns(outputHandle, configParams, configDataRows):
# 	pass
# 
# def writeMetricsConfig(outputHandle, configParams, configDataRows):
# 	pass




def getDistName(configDir):
	'''Extracts distDir from the full path of the configDir'''
	
	# manipulate string
	# example: /home/giacomo/Development/Systems/kvmgen/analysis/pstrat/cn12-cpv1-idf1-psBALANCED/073fedcfa814067a42d99dae0a3a0cd9/
	splits = configDir.split('/')
	distName = splits[len(splits) - 3]	
	return distName


def extractDist(distName):
	'''Extracts CN, CPV, IDF, PSTRAT from distribution name, returns them 
	as a dictionary'''
	
	# manipulate string
	# example: cn12-cpv1-idf1-psBALANCED/
	print (distName)
	splits = distName.split("-")

	hasCN = splits[0]
	cn = hasCN[2:len(hasCN)]

	hasCPV = splits[1]
	cpv = hasCPV[3:len(hasCPV)]

	hasIDF = splits[2]
	idf = hasIDF[3:len(hasIDF)]

	hasPSTRAT = splits[3].split("/")[0]
	pstrat = hasPSTRAT[2:len(hasPSTRAT)]

	# build output
	output = {'cn' : cn, 'cpv' : cpv, 'idf' : idf, 'pstrat' : pstrat}
	return output
