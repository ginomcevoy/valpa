# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# VM XML Generator component

import jinja2
import os
import shutil
import subprocess
from core import uuid

class VMDefinitionGenerator:
	'''
	Produces VM XML for VM domains, based on cluster XML and 
	clusterRequest. Returns the filenames of the XMLs.
	'''

	def __init__(self, basicDefiner, pinningWriter, xmlSaver):
		self.basicDefiner = basicDefiner
		self.pinningWriter = pinningWriter
		self.xmlSaver = xmlSaver
		
	def setDeploymentContext(self, deploymentInfo, forReal = True):
		self.basicDefiner.setDeploymentContext(deploymentInfo, forReal)
		self.pinningWriter.setDeploymentContext(deploymentInfo)

	def createDefinitions(self, clusterXML, clusterRequest, experimentName):
		'''
		Gathers data from cluster and to produces all VM XMLs
		'''
		# modify clusterXML and produce basic VM XMLs
		xmlDict = self.basicDefiner.createDefinitions(clusterXML)
		
		# enhance with pinning strategies
		cpv = clusterRequest.topology.cpv
		pinningOpt = clusterRequest.mapping.pinningOpt
		xmlDict = self.pinningWriter.enhanceXMLs(xmlDict, cpv, pinningOpt)
		
		# save XMLs
		return self.xmlSaver.saveXMLs(xmlDict, experimentName)
	
class VMDefinitionBasicGenerator:
	'''
	Creates a Vm XML with basic characteristics (vm name, UUID, diskFile, MAC)
	'''
	def __init__(self, vespaPrefs, definitionDetails):
		self.vespaPrefs = vespaPrefs
		self.definitionDetails = definitionDetails
		self.clusterXMLFilename = '/tmp/vespa-definition-cluster.xml'
		
		# setup jinja template
		templateLoader = jinja2.FileSystemLoader(searchpath="/")
		self.templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True)
		
	def setDeploymentContext(self, deploymentInfo, forReal = True):
		self.deployedNodes = deploymentInfo[0]
		self.deployedVMs = deploymentInfo[2]
		self.definitionDetails.setDeploymentContext(deploymentInfo, forReal)
				
	def createDefinitions(self, clusterXML):
		'''
		Returns a dictionary <vmName, xml text>
		''' 
		output = {}
		
		# prepare jinja template for VM arguments
		clusterXML = clusterXML.replace('_VM_VAR_', '{')
		with open(self.clusterXMLFilename, 'w') as clusterXMLFile:
			clusterXMLFile.write(clusterXML)
		template = self.templateEnv.get_template(self.clusterXMLFilename)
		
		# iterate all vms
		for nodeName in self.deployedNodes.getNames():
			node = self.deployedNodes.getNode(nodeName)
			for vmName in self.deployedVMs.getVMNamesForNode(node):
				
				# replace VM name, UUID, MAC address and disk path
				uuid = self.definitionDetails.getUUID(vmName)
				mac = self.definitionDetails.getMAC(vmName)
				vmPath = self.definitionDetails.getVmPath(vmName)
				args = {'vm_name' : vmName, 'vm_uuid' : uuid, 'vm_mac' : mac, 'vm_path' : vmPath}
				
				# apply jinja substitution
				vmXML = template.render(args)
				
				# add text to output
				output[vmName] = vmXML
				
		return output
	
class VMXMLSaver:
	'''
	Saves all the VM XMLs into a path specified by vespaPrefs
	'''
	
	def __init__(self, vespaPrefs):
		self.vespaPrefs = vespaPrefs
		
	def saveXMLs(self, xmlDict, experimentName):
		
		# create target dir - will delete it if non-empty!
		outputDir = self.vespaPrefs['vm_xml_output'] + '/' + experimentName
		if os.path.exists(outputDir):
			shutil.rmtree(outputDir)
		os.makedirs(outputDir)
		
		output = {}
		
		# save each xml
		for vmName in xmlDict.keys():
			xmlText = xmlDict[vmName]
			xmlFilename = outputDir + '/' + vmName + '.xml'
			xmlFile = open(xmlFilename, 'w')
			xmlFile.write(xmlText)
			xmlFile.close()
			
			# write filename to output
			output[vmName] = xmlFilename
		
		return output
	
class VMDefinitionDetails:
	'''
	Provides functions to create uuidgen and MAC address.
	'''
	def __init__(self, vespaPrefs, networkAddresses):
		self.vespaPrefs = vespaPrefs
		self.networkAddresses = networkAddresses
		
	def setDeploymentContext(self, deploymentInfo, forReal = True):
		self.deployedNodes = deploymentInfo[0]
		self.deployedVMs = deploymentInfo[2]
		self.forReal = forReal
	
	def getUUID(self, vmName):
		'''
		Generate an UUID
		'''
		return uuid.newUUID(self.forReal)
	
	def getVmPath(self, vmName):
		hostingNode = self.deployedVMs.getHostingNode(vmName)
		return hostingNode.name + '/' + vmName
	
	def getMAC(self, vmName):
		# delegate MAC definition
		node = self.deployedVMs.getHostingNode(vmName)
		nodeIndex = node.index
		vmIndex = self.deployedVMs.getVMIndex(vmName)
		return self.networkAddresses.getVMMAC(nodeIndex, vmIndex)
	
class BuildsVMDefinitionGenerator:
	'''
	Creates an instance of VMDefinitionGenerator 
	'''
	
	def __init__(self, vespaPrefs, pinningWriter, networkAddresses):
		self.vespaPrefs = vespaPrefs
		self.pinningWriter = pinningWriter
		self.networkAddresses = networkAddresses
		
	def build(self):
		definitionDetails = VMDefinitionDetails(self.vespaPrefs, self.networkAddresses)
		basicGenerator = VMDefinitionBasicGenerator(self.vespaPrefs, definitionDetails)
		xmlSaver = VMXMLSaver(self.vespaPrefs)
		return VMDefinitionGenerator(basicGenerator, self.pinningWriter, xmlSaver)