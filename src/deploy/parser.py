# Reads the scenarios in an XML file, processes it and produces
# an Scenario list for each scenario, as well as an output file.
# The scenarios are grouped in directories (single experiment),
# which represent the experiment groups. Also produces an output file
# for the next script.
# The output file will store the path of each experiment group.

# TODO: time between groups
# TODO: time to wait for application within group

import jinja2
import os
import shutil
import sys
import xml.etree.ElementTree as ET

from bean.experiment import *  # @UnusedWildImport
from bean.cluster import Cluster, Topology, Mapping, Technology ,\
	ClusterPlacement
from bean.enum import CpuTopoOpt, DiskOpt, NetworkOpt, PinningOpt  # @UnusedImport they ARE used

def parseScenarios(xmlFile):

	# Parse the file
	tree = ET.parse(xmlFile)
	root = tree.getroot()

	scenarios = []
	for scenarioNode in root.findall('scenario'):
		scenario = parseScenario(scenarioNode)
		scenarios.append(scenario)

	return scenarios

def parseScenario(scenarioNode):
	
	# parse all concurrent experiments in this scenario
	# one experiment = stand-alone, no concurrency
	exps = []
	for experimentNode in scenarioNode.findall('experiment'):
		exp = parseExperiment(experimentNode)
		exps.append(exp)
	scenario = Scenario(exps)
	return scenario

def parseExperiment(experimentNode):    

	# parse experiment info
	name = experimentNode.get('name')
	trials = experimentNode.get('trials')   
	
	# parse single cluster
	clusterNode = experimentNode.find('cluster')
	cluster = parseCluster(clusterNode)
	
	# application section, may be empty
	appNode = experimentNode.find('app')
	if appNode is not None:
		app = parseApplication(appNode)
	else:
		# mock application, only cluster matters
		app = Application('none', 0) 
	
	return Experiment(name, cluster, app, trials)  

def parseCluster(clusterNode):
		
	# Check if asking for physical cluster
	virtualValue = clusterNode.get('virtual')
	if virtualValue == 'False':
		physicalMachinesOnly = True
	else:
		physicalMachinesOnly = False
		
	# topology section
	topoNode = clusterNode.find('topology')
	topology = parseTopology(topoNode)

	# mappings section, may be empty (physical cluster)
	mappingNode = clusterNode.find('mapping')
	if mappingNode is not None:
		mapping = parseMapping(mappingNode)
	else:
		# physical cluster
		mapping = None

	# technology section, may be empty	
	technologyNode = clusterNode.find('technology')
	if technologyNode is not None:
		technology = parseTechnology(technologyNode)
	else:
		technology = None

	# TODO: tuning section

	# cluster object
	clusterPlacement = ClusterPlacement(topology, mapping) 
	cluster = Cluster(clusterPlacement, technology, None, physicalMachinesOnly)

	return cluster

def parseApplication(appNode):

	# parse app details
	name = appNode.get('name')
	runs = int(appNode.get('runs'))
	
	# parse space separated arguments
	argNode = appNode.find('args')
	if argNode is not None:
		args = argNode.text
	else:
		args = ''

	# parse app tuning details
	tuningNode = appNode.find('tuning')
	procpin = tuningNode.find('procpin').text
	appTuning = AppTuning(procpin)

	app = Application(name, runs, args, appTuning)
	return app

def parseTopology(topoNode):
	nc = int(topoNode.get('nc'))
	cpv = int(topoNode.get('cpv'))
	return Topology(nc, cpv)

def parseMapping(mappingNode):
	idf = int(mappingNode.get('idf'))
	pstratValue = mappingNode.get('pstrat')
	pinningOpt = eval('PinningOpt.' + pstratValue)
	return Mapping(idf, pinningOpt)
	
def parseTechnology(technologyNode):
	networkValue = technologyNode.get('network')
	networkOpt = eval('NetworkOpt.' + networkValue)
	diskValue = technologyNode.get('disk')
	diskOpt = eval('DiskOpt.' + diskValue)
	return Technology(networkOpt, diskOpt)

def writeScenarios(scenarios, baseDir, helperFilename):

	# Create baseDir - will delete it if non-empty!
	if os.path.exists(baseDir):
		shutil.rmtree(baseDir)
	os.makedirs(baseDir)

	# create output
	output = open(baseDir + '/' + helperFilename, 'w')

	for scenario in scenarios:
		
		# assume single experiment
		exp = scenario.getExperiment()

		# make experiment dir
		expPath = baseDir + '/' + exp.name

		if not os.path.exists(expPath):
			os.makedirs(expPath)

		# write each experiment to a file in experiment dir
		cluster = exp.cluster
		app = exp.app
		writeExperiment(cluster, app, expPath)
		
		# write experiment name in helper file
		output.write(exp.name + "\n")

	output.close()

def writeExperiment(cluster, app, expDir):

	# create experiment file inside expDir
	filename = expDir + '/' + app.name
	experimentFile = open(filename, 'w')

	# write output using template
	text = createExperimentText(cluster, app)
	experimentFile.write(text)
	experimentFile.close()
	
def createExperimentText(cluster, app):
	
	# setup jinja template
	templateLoader = jinja2.FileSystemLoader(searchpath="../templates")
	templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True)
	template = templateEnv.get_template('experiment.template')

	# apply jinja substitution
	text = template.render(locals())
	return text

# Do this when attempting to run module
# Arguments:
# 1: the XML with experiments
# 2: the main directory for experiment groups
# 3: the name of the output file for the calling script
if __name__ == '__main__':
	
	# check input
	if len(sys.argv) < 3:
		raise ValueError("call: parser <xmlFile> <outputBaseDir> <helperFilename>")

	# parse XML to get experiments
	xmlFile = sys.argv[1]
	scenarios = parseScenarios(xmlFile)

	# output experiments to files
	baseDir = sys.argv[2]
	helperFilename = sys.argv[3]
	writeScenarios(scenarios, baseDir, helperFilename)