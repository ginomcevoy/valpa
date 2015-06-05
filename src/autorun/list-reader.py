# Reads the experiments in experiments.xml, processes it and produces
# a file for each experiment. The experiments are grouped in directories,
# which represent the experiment groups. Also produces an output file
# for the next script.
# The output file will store the path of each experiment group.

# TODO: time between groups
# TODO: time to wait for application within group
# TODO: application arguments


# FIXME: is this still being used!?

import os
import sys
import shutil
import xml.etree.ElementTree as ET

def run():
	# Arguments:
	# 1: the XML with experiments
	# 2: the main directory for experiment groups
	# 3: the name of the output file for the calling script
	xmlFile = sys.argv[1]
	groupDir = sys.argv[2]
	outputName = sys.argv[3]

	# Create groupDir - will delete it if non-empty!
	if os.path.exists(groupDir):
		shutil.rmtree(groupDir)
	os.makedirs(groupDir)

	# create output
	output = open(outputName, 'w')

	# Parse the file
	tree = ET.parse(xmlFile)
	root = tree.getroot()

	for deployGroup in root.findall('deploy-group'): # findall <-> iter
		
		# make group dir
		groupName = deployGroup.get('name')
		groupPath = groupDir + '/' + groupName
		if not os.path.exists(groupPath):
			os.makedirs(groupPath)

		# work each application
		index = 1
		for deployUnit in deployGroup.findall('deploy-unit'):
			doApplication(deployUnit, groupPath, index)
			index = index + 1

		# save output
		output.write(groupPath+'\n')

	output.close()


def doApplication(deployUnit, groupPath, index):

	# Gather data
	appName = deployUnit.find('app-name').text
	runs = deployUnit.find('runs').text
	
	distNode = deployUnit.find('dist')
	np = distNode.find('np').text
	cpv = distNode.find('cpv').text
	idf = distNode.find('idf').text
	pstrat = distNode.find('pstrat').text

	# create deployment file inside groupDir
	filename = groupPath + '/' + str(index) + '-' + appName
	file = open(filename, 'w')
	file.write('app='+appName+'\n')
	file.write('np='+np+'\n')
	file.write('cpv='+cpv+'\n')
	file.write('idf='+idf+'\n')
	file.write('pstrat='+pstrat+'\n')
	file.write('runs='+runs+'\n')
	file.close()


# Do this when attempting to run module
if __name__ == '__main__':
    run()
