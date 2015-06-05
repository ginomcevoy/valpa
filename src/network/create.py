'''
Created on Oct 21, 2014

@author: giacomo
'''
from quik import FileLoader
import sys
import bootstrap
from config import valpaconfig

class BuildsNetworkXMLs:
    '''
    Creates the network XML(s) for three different implementations:
    -   SRIOV: use the SRIOV capabilities, assumes that Virtual Functions
        are enabled for the given network interface.
        Output at data-output/networks/sriov.xml
    -   Use Bridge: use an existing bridge, assumes external configuration
        of virtual network and DHCP.
        Output at data-output/networks/external-bridge.xml
    -   Create bridge: creates a new bridge from a network interface in each
        physical node, each node will get a network XML with its name. also
        sets up the DHCP servers for the VMs. 
        Output at data-output/networks/libvirt-bridge-[nodeName].xml
    '''
    
    def __init__(self, basicCreator, argumentSolverFactory, enhancerForCreatingBridge, physicalCluster):
        self.basicCreator = basicCreator
        self.enhancerForCreatingBridge = enhancerForCreatingBridge
        self.physicalCluster = physicalCluster
        self.argumentsSRIOV = argumentSolverFactory.createForSRIOV()
        self.argumentsUseBridge = argumentSolverFactory.createForUsingBridge()
        self.argumentsCreateBridge = argumentSolverFactory.createForCreatingBridge()
        
    def createNetworkXMLs(self, networkType, outputDir):
        if not networkType in valpaconfig.allowedNetworkTypes():
            print('Allowed values = ' + str(valpaconfig.allowedNetworkTypes()))
            raise ValueError('Network type not allowed: ', networkType)
        
        if networkType == 'sriov':
            self._createForSRIOV(outputDir) 
        elif networkType == 'external-bridge':
            self._createForUsingBridge(outputDir)
        elif networkType == 'libvirt-bridge':
            self._createForCreatingBridge(outputDir)
        
    def _createForSRIOV(self, outputDir):
        # SRIOV gets a single file
        self.basicCreator.setArgumentSolver(self.argumentsSRIOV)
        xmlText = self.basicCreator.createXML()
        self._writeXMLText(xmlText, outputDir, 'sriov.xml')
        
    def _createForUsingBridge(self, outputDir):
        # Using bridge gets a single file
        self.basicCreator.setArgumentSolver(self.argumentsUseBridge)
        xmlText = self.basicCreator.createXML()
        self._writeXMLText(xmlText, outputDir, 'external-bridge.xml')
        
    def _createForCreatingBridge(self, outputDir):
        self.basicCreator.setArgumentSolver(self.argumentsCreateBridge)
        
        # Creating bridge gets a file per physical node
        for nodeName in self.physicalCluster.getNames():
            nodeIndex = self.physicalCluster.getNodeIndex(nodeName)
            xmlText = self.basicCreator.createXML(nodeIndex)
            
            # add DHCP lines
            xmlText = self.enhancerForCreatingBridge.addDHCPLines(xmlText, nodeName)
            
            outputFilename = 'libvirt-bridge-' + nodeName + '.xml'
            self._writeXMLText(xmlText, outputDir, outputFilename)
        
    def _writeXMLText(self, xmlText, outputDir, outputFilename):
        outputFile = outputDir + '/' + outputFilename
        with open(outputFile, 'w') as xmlFile:
            xmlFile.write(xmlText)

class CreatesBasicNetworkXML:
    '''
    Creates a basic network XML for a given node. In the case
    of creating a bridge, does not include DHCP entries.
    '''
    
    def __init__(self):
        self.loader = FileLoader('.')
        
    def setArgumentSolver(self, argumentSolver):
        '''
        Strategy for finding arguments to replace in a template.
        Also decides which template to use.
        '''
        self.argumentSolver = argumentSolver
    
    def createXML(self, nodeIndex=0):

        # delegate argument solving to strategy
        args = self.argumentSolver.getArguments(nodeIndex)
         
        # Use template with variables from the args dictionary
        # name of the template is in the 'network_template' entry 
        template = self.loader.load_template(args['network_template'])
        networkXML = template.render(args, loader=self.loader)
        
        return networkXML

class NetworkArgumentsForSRIOV:
    '''
    Returns template arguments for SRIOV network.
    '''
    
    def __init__(self, networkingOpts):
        self.networkingOpts = networkingOpts
    
    def getArguments(self, nodeIndex = 0):
        # select template
        args = {'network_template' : '../templates/network-sriov.template'}
        
        #  <network>
        #    <name>@network_name</name>
        #    <forward mode='hostdev' managed='yes'>
        #      <pf dev='@network_interface'/>
        #    </forward>
        #  </network>
        args['network_name'] = self.networkingOpts['net_name_sriov']
        args['network_interface'] = self.networkingOpts['net_dev']
        return args

class NetworkArgumentsForUsingBridge:
    '''
    Returns template arguments for bridged network, uses existing bridge
    '''
    
    def __init__(self, networkingOpts):
        self.networkingOpts = networkingOpts
    
    def getArguments(self, nodeIndex = 0):
        # select template
        args = {'network_template' : '../templates/network-external.template'}
        
        # <network>
        #     <name>@network_name</name>
        #     <forward mode="bridge"/>
        #     <bridge name="@network_bridge"/>
        # </network>

        args['network_name'] = self.networkingOpts['net_name_bridge_use']
        args['network_bridge'] = self.networkingOpts['net_bridge']
        return args

class NetworkArgumentsForCreatingBridge:
    '''
    Returns template arguments for bridged network, creates new bridge
    '''
    
    def __init__(self, networkingOpts, networkAddresses):
        self.networkingOpts = networkingOpts
        #self.physicalCluster = physicalCluster
        #self.hwSpecs = hwSpecs
        self.networkAddresses = networkAddresses

    def getArguments(self, nodeIndex):
        # select template
        args = {'network_template' : '../templates/network-libvirt.template'}
        
        # <network>
        #   <name>@network_name</name>
        #   <forward mode='route' dev='@network_interface'/>
        #   <bridge name='@network_bridge' stp='off' delay='0' />
        #   <ip address='@node-address' netmask='@network_netmask'>
        #     <dhcp>
        #       <range start='@dhcp-range-start' end='@dhcp-range-end' />
        #     </dhcp>
        #   </ip>
        # </network>

        # parameters for all nodes
        args['network_name'] = self.networkingOpts['net_name_bridge_create']
        args['network_interface'] = self.networkingOpts['net_dev']
        args['network_bridge'] = self.networkingOpts['net_bridge']
        args['network_netmask'] = self.networkAddresses.networkNetmask()
        
        # parameters specific to node
        args['node_address'] = self.networkAddresses.getNodeAddress(nodeIndex) 
        args['dhcp_range_start'] = self.networkAddresses.addressRangeStart(nodeIndex)
        args['dhcp_range_end'] = self.networkAddresses.addressRangeEnd(nodeIndex)
        
        return args
    
class ArgumentSolverFactory:
    '''
    Provides instances to the three strategies for network arguments.
    '''
    def __init__(self, networkingOpts, networkAddresses):
        self.networkingOpts = networkingOpts 
        self.networkAddresses = networkAddresses
        
    def createForSRIOV(self):
        return NetworkArgumentsForSRIOV(self.networkingOpts)
    
    def createForUsingBridge(self):
        return NetworkArgumentsForUsingBridge(self.networkingOpts)
    
    def createForCreatingBridge(self):
        return NetworkArgumentsForCreatingBridge(self.networkingOpts, self.networkAddresses)
    

class EnhancesXMLForCreatingBridge:
    '''
    Takes the text of the network XML for creating a bridge, 
    and adds the DHCP offers for all necessary VMs.
    '''
    def __init__(self, physicalCluster, allVMDetails):
        self.physicalCluster = physicalCluster
        self.allVMDetails = allVMDetails
    
    def addDHCPLines(self, networkXML, nodeName):
        '''
        @param networkXML: text of the network XML
        '''
        # find the line above the DHCP lines that has "<range" in it,
        # then find the end of this line
        rangeIndex = networkXML.find('range')
        textAfterRange = networkXML[rangeIndex:len(networkXML)]
        endOfRangeLine = textAfterRange.find('\n')
        endOfRangeLine = rangeIndex + endOfRangeLine + 1
        
        # get the lines and format into single paragraph with indent
        lines = self._buildLinesForNode(nodeName)
        paragraph = '\t' + '\t'.join(lines)
        
        # append DHCP lines after end of range line
        textBeforePoint = networkXML[0:endOfRangeLine]
        textAfterPoint = networkXML[endOfRangeLine :len(networkXML)]
        ammendedNetworkXML = textBeforePoint + paragraph + textAfterPoint 
        return ammendedNetworkXML
    
    def _buildLinesForNode(self, nodeName):
        
        lines = []
        
        # get all possible VMs for this node
        for vmName in self.allVMDetails.getVMNamesForNode(nodeName):
            # get each line
            line = self._buildLineForVM(vmName)
            lines.append(line)
            
        return lines
    
    def _buildLineForVM(self, vmName):
        vmMAC = self.allVMDetails.getMacAddressOf(vmName)
        vmAddress = self.allVMDetails.getIpAddressOf(vmName)
        line='<host mac="' + vmMAC + '" name="' + vmName + '" ip="' + vmAddress +'" />\n'
        return line


if __name__ == '__main__':
    # verify input
    if len(sys.argv) < 2:
        raise ValueError("call: " + sys.argv[0] + " <networkType> [outputDir]")
    networkType = sys.argv[1]
    
    if len(sys.argv) > 2:
        outputDir = sys.argv[2]
    else:
        outputDir = '../data-output/networks' # default location
    
    # Bootstrap VALPA with default config
    bootstrap.bootstrap()
    bootstrapper = bootstrap.getInstance()
    
    # produce networkXML
    buildsXMLs = bootstrapper.getBuildsNetworkXMLs()
    buildsXMLs.createNetworkXMLs(networkType, outputDir)
    
    print('Output at ' + outputDir)