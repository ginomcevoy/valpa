'''
Created on Oct 16, 2013

@author: giacomo
'''

import jinja2
import subprocess

from core import config_vespa
from .mapping import MappingResolver
from submit.pbs.updater import PBSUpdater
from core.virtual import VirtualClusterTemplates
from core.enum import NetworkOpt, PinningOpt # @UnusedImport it IS used
from core.cluster import Topology, Mapping, ClusterRequest, ClusterPlacement

class ClusterDefiner:
    '''
    Defines the VMs in a cluster.
    '''
    def __init__(self, mappingResolver, clusterXMLGen, vmDefinitionGenerator):
        self.mappingResolver = mappingResolver
        self.clusterXMLGen = clusterXMLGen 
        self.vmDefinitionGenerator = vmDefinitionGenerator
    
    def defineCluster(self, cluster, experimentName, forReal):
        '''
        Given a cluster request (Cluster Placement + VMM Technology), translates
        request into a deployment tuple (deployedNodes, deployedSockets, deployedVMs)
        The VirtualClusterTemplates instance includes the XML definitions of the VMs.
        '''
        
        # create cluster XML
        clusterXML = self.clusterXMLGen.produceClusterXML(cluster.topology, cluster.technology)
        
        # produce mappings
        self.mappingResolver.processMappings(cluster)
        deployedNodes = self.mappingResolver.getDeployedNodes()
        deployedVMs = self.mappingResolver.getDeployedVMs()
        deploySockets = self.mappingResolver.getDeployedSockets()
        
        deploymentInfo = (deployedNodes, deploySockets, deployedVMs)
        
        # use VMDefinitionGenerator to create VM XMLs
        self.vmDefinitionGenerator.setDeploymentContext(deploymentInfo, forReal)
        definitionDict = self.vmDefinitionGenerator.createDefinitions(clusterXML, cluster, experimentName)
        
        # add XMLs
        deployedVMs.setDefinitions(definitionDict)
        
        return deploymentInfo
    
def defineVMsLibvirt(deployedVMs, forReal):
    '''
    Uses libvirt to define VMs
    @deprecated: VMs are now created from XML without defining them
    '''
    for vmName in deployedVMs.getAllVms():
        # virsh -c qemu+ssh://$HOST/system define $XML
        host = deployedVMs.getHostname(vmName)
        xml = deployedVMs.getXML(vmName)
        address = 'qemu+ssh://' + host + '/system'
        callList = ['virsh', '-c', address, 'define', xml]
        if forReal:
            subprocess.call(callList)            
        print(callList)
        
class PhysicalClusterDefiner:
    '''
    Used when deploying directly on physical cluster, without VMs.
    No need for creating any XML here, only job is to produce the
    deploymentInfo tuple.
    
    TODO: use patterns to create variations Physical/Virtual + PBS/NoPBS
    '''
    
    def __init__(self, hwSpecs, vespaPrefs, appConfig, runOpts, allNodes, allVMDetails):
        # reuse some mapping functionality
        self.mapper = MappingResolver(hwSpecs, vespaPrefs, allNodes, allVMDetails) 
        self.allNodes = allNodes
        self.runOpts = runOpts
        self.appConfig = appConfig

    def defineCluster(self, clusterRequest, appRequest, forReal):
        # only needs topology:
        # nc = number of processes
        # cpv = number of processes per host
        # hosts = nc / cpv
        
        if clusterRequest.mapping.deployNodes is not None:
            # read from definition
            deployNodeNames = clusterRequest.mapping.deployNodes
            deployedNodes = self.allNodes.getSubset(deployNodeNames)
        else:
            # infer deployNodes
            topology = clusterRequest.topology
            hostCount = int(topology.nc / topology.cpv)
            deployNodeNames = self.allNodes.getSubsetForHostCount(hostCount)
        
        # reuse socket logic
        self.mapper.mapping = clusterRequest.mapping
        deployedSockets = self.mapper.getDeployedSockets()
        
        # here the "VMs" are actually hosts!
        
        # attributes of VirtualClusterTemplates    
        vmDict = {}
        byNode = {}
        
        # iterate over nodes
        for node in deployedNodes:
            # build vmDict and byNode using node data
            vmDict[node.name] = node
            byNode[node.name] = node.name
            
        deployedVMs = VirtualClusterTemplates(vmDict, byNode)
        
        # Case for using PBS
        if self.appConfig.isTorqueBased(appRequest):

            # need to update PBS configuration
            pbsUpdater = PBSUpdater(self.runOpts, forReal)
            pbsUpdater.updatePBS(deployedVMs, clusterRequest)

        else:
            #deploymentType = 'NONE'
            pass

        # deployment tuple
        return (deployedNodes, deployedSockets, deployedVMs)
    
class VespaXMLGenerator:
    '''
    Produces Vespa XML for cluster XML generation, based on a master XML and
    configuration parameters.
    '''
    def __init__(self, vespaXMLOpts, networkingOpts, repoOpts, templateDir, masterTemplate):
        self.vespaXMLOpts = vespaXMLOpts
        self.networkingOpts = networkingOpts
        self.repoOpts = repoOpts
        
        # setup jinja template
        templateLoader = jinja2.FileSystemLoader(searchpath=templateDir)
        templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True, keep_trailing_newline=True)
        self.template = templateEnv.get_template(masterTemplate)
        
    def produceVespaXML(self):
        '''
        Produces Vespa XML for cluster XML generation, based on a master XML and
    configuration parameters. Returns the text of the XML.
        '''
        # choose network name from selected type 
        # types: ('sriov', 'use-bridge', 'create-bridge')
        networkType = self.networkingOpts['network_source']
        if not networkType in config_vespa.allowedNetworkTypes():
            print('Allowed values = ' + str(config_vespa.allowedNetworkTypes()))
            raise ValueError('Network type not allowed: ', networkType)
        
        if networkType == 'external-bridge':
            networkName = self.networkingOpts['net_name_bridge_use']
        elif networkType == 'libvirt-bridge':
            networkName = self.networkingOpts['net_name_bridge_create']
        else: #networkType == 'sriov'
            networkName = self.networkingOpts['net_name_sriov']
        
        # Prepare arguments for substitution 
        args = {'network_name' : networkName,
                'xml_disk_drivertype' : self.vespaXMLOpts['xml_disk_drivertype'],
                'repo_root' : self.repoOpts['repo_root'],
                'xml_disk_dev' : self.vespaXMLOpts['xml_disk_dev']
            }
        
        # apply jinja substitution
        vespaXML = self.template.render(args)
        
        return vespaXML
                
class ClusterXMLGenerator:
    '''
    Produces Cluster XML for VM XML generation, based on Vespa XML and 
    cluster info. Returns the text of the xml.
    '''

    def __init__(self, vespaXML, vespaPrefs, hwSpecs):
        self.vespaXML = vespaXML
        self.vespaPrefs = vespaPrefs
        self.hwSpecs = hwSpecs
        
        self.vespaXMLFilename = '/tmp/vespa-definition.xml'
        
        # setup jinja template
        templateLoader = jinja2.FileSystemLoader(searchpath="/")
        self.templateEnv = jinja2.Environment(loader=templateLoader, trim_blocks=True, keep_trailing_newline=True)
                
    def produceClusterXML(self, topology, technology):
        '''
        Produces Cluster XML for VM XML generation, based on Vespa XML and 
        cluster info. Returns the text of the xml.
        '''
        
        # networking works with a two variables:
        # networkOpt is read from technology
        # networkDriver variable is calculated here
        if (technology.networkOpt == NetworkOpt.virtio):
            networkDriver = 'qemu'     # <driver name="qemu"/>   - virtIO
        elif (technology.networkOpt == NetworkOpt.vhost):
            networkDriver = 'vhost'    # <driver name="vhost"/>  - vhost
        else:
            networkDriver = ''         # SR-IOV has no such line
            
        # calculate total memory based on number of cores, libvirt uses KB
        memoryBase = int(self.vespaPrefs['vm_mem_base'])
        memoryPerCore = int(self.vespaPrefs['vm_mem_core'])
        totalMemory = (memoryBase + memoryPerCore * topology.cpv) * 1024
        
        # gather all substitutions
        args = {'cluster_vcpu' : topology.cpv, 
                'cluster_memory' : totalMemory,
                'network_option' : technology.networkOpt, 
                'network_driver' : networkDriver,  
                'cluster_disk_bus' : technology.diskOpt,
                'cluster_disk' : self.vespaPrefs['vm_disk'],
                
                # if Infiniband is unused, last has no effect
                'ib_flag' : technology.infinibandFlag,
                'ib_bus' : self.hwSpecs['ib_bus'],
                }
        
        # prepare jinja template for cluster arguments
        self.vespaXML = self.vespaXML.replace('_CLUSTER_VAR_', '{')
        with open(self.vespaXMLFilename, 'w') as vespaXMLFile:
            vespaXMLFile.write(self.vespaXML)
        template = self.templateEnv.get_template(self.vespaXMLFilename)
        
        # apply jinja substitution
        clusterXML = template.render(args)
        
        return clusterXML
    
def createClusterRequest(nc, cpv, idf, pstrat):
    
    # convert input
    nc = int(nc)
    cpv = int(cpv)
    idf = int(idf)
    pinningOpt = eval('PinningOpt.' + pstrat)
    
    # Create cluster object = topology + mapping + default VMM opts
    topology = Topology(nc, cpv)
    mapping = Mapping(idf, pinningOpt)
    clusterPlacement = ClusterPlacement(topology, mapping) 
    clusterRequest = ClusterRequest(clusterPlacement)
    return clusterRequest
    
