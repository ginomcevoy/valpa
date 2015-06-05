# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# VM XML Generator component
import subprocess
import os
import shutil
from quik import FileLoader

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
	def __init__(self, valpaPrefs, definitionDetails):
		self.valpaPrefs = valpaPrefs
		self.definitionDetails = definitionDetails
		self.loader = FileLoader('.')
		self.clusterXMLFilename = '/tmp/valpa-definition-cluster.xml'
		
	def setDeploymentContext(self, deploymentInfo, forReal = True):
		self.deployedNodes = deploymentInfo[0]
		self.deployedVMs = deploymentInfo[2]
		self.definitionDetails.setDeploymentContext(deploymentInfo, forReal)
				
	def createDefinitions(self, clusterXML):
		'''
		Returns a dictionary <vmName, xml text>
		''' 
		output = {}
		
		# save clusterXML temporarily
		with open(self.clusterXMLFilename, 'w') as clusterXMLFile:
			clusterXMLFile.write(clusterXML)
		
		# iterate all vms
		for nodeName in self.deployedNodes.getNames():
			for vmName in self.deployedVMs.getVMNamesForNode(nodeName):
				
				# replace VM name, UUID, MAC address and disk path using quik
				uuid = self.definitionDetails.getUUID(vmName)
				mac = self.definitionDetails.getMAC(vmName)
				vmPath = self.definitionDetails.getVmPath(vmName)
				args = {'vm_name' : vmName, 'vm_uuid' : uuid, 'vm_mac' : mac, 'vm_path' : vmPath}
				
				template = self.loader.load_template(self.clusterXMLFilename)
				vmXML = template.render(args, loader=self.loader)
				
				# add text to output
				output[vmName] = vmXML
				
		return output
	
class VMXMLSaver:
	'''
	Saves all the VM XMLs into a path specified by valpaPrefs
	'''
	
	def __init__(self, valpaPrefs):
		self.valpaPrefs = valpaPrefs
		
	def saveXMLs(self, xmlDict, experimentName):
		
		# create target dir - will delete it if non-empty!
		outputDir = self.valpaPrefs['vm_xml_output'] + '/' + experimentName
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
	def __init__(self, valpaPrefs, networkAddresses):
		self.valpaPrefs = valpaPrefs
		self.networkAddresses = networkAddresses
		
	def setDeploymentContext(self, deploymentInfo, forReal = True):
		self.deployedNodes = deploymentInfo[0]
		self.deployedVMs = deploymentInfo[2]
		self.forReal = forReal
	
	def getUUID(self, vmName):
		'''
		Calls the uuidgen system exec to create a UUID.
		'''
		if (self.forReal):
			output = subprocess.check_output(['uuidgen'])
			uuid = output.decode('utf-8')[0:len(output) -1]
		else:
			# mock value for testing
			uuid = '446bf85f-b4ba-459b-8e04-60394fc00d5c'
		return uuid
	
	def getVmPath(self, vmName):
		nodeName = self.deployedVMs.getHostingNode(vmName)
		return nodeName + '/' + vmName
	
	def getMAC(self, vmName):
		# delegate MAC definition
		nodeName = self.deployedVMs.getHostingNode(vmName)
		nodeIndex = self.deployedNodes.getNodeIndex(nodeName)
		vmIndex = self.deployedVMs.getVMIndex(vmName)
		return self.networkAddresses.getVMMAC(nodeIndex, vmIndex)
	
class BuildsVMDefinitionGenerator:
	'''
	Creates an instance of VMDefinitionGenerator 
	'''
	
	def __init__(self, valpaPrefs, pinningWriter, networkAddresses):
		self.valpaPrefs = valpaPrefs
		self.pinningWriter = pinningWriter
		self.networkAddresses = networkAddresses
		
	def build(self):
		definitionDetails = VMDefinitionDetails(self.valpaPrefs, self.networkAddresses)
		basicGenerator = VMDefinitionBasicGenerator(self.valpaPrefs, definitionDetails)
		xmlSaver = VMXMLSaver(self.valpaPrefs)
		return VMDefinitionGenerator(basicGenerator, self.pinningWriter, xmlSaver)