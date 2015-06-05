'''
Created on Oct 16, 2013

@author: giacomo
'''
from deploy.mapping import MappingResolver
import subprocess
from run.config import ConfiguratorFactory
from run.pbs.updater import PBSUpdater
from bean.vm import VirtualClusterTemplates
from bean.enum import NetworkOpt
from quik import FileLoader
 
class ClusterDefiner:
    '''
    Defines the VMs in a cluster.
    '''
    def __init__(self, mappingResolver, clusterXMLGen, vmDefinitionGenerator):#valpaPrefs, valpaXML, hwSpecs, allNodes, vmRequestGenerator):
        self.mappingResolver = mappingResolver#MappingResolver(hwSpecs, allNodes, valpaPrefs)
        self.clusterXMLGen = clusterXMLGen #ClusterXMLGenerator(valpaXML, valpaPrefs)
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
    
    def __init__(self, hwSpecs, valpaPrefs, runOpts, allNodes, allVMDetails):
        # reuse some mapping functionality
        self.mapper = MappingResolver(hwSpecs, valpaPrefs, allNodes, allVMDetails) 
        self.allNodes = allNodes
        self.runOpts = runOpts

        # strategy 
        self.configFactory = ConfiguratorFactory(runOpts)

        
    def defineCluster(self, cluster, appInfo, forReal):
        # only needs topology:
        # nc = number of processes
        # cpv = number of processes per host
        # hosts = nc / cpv
        
        # try to read from definition
        deployNodes = None
        if cluster.mapping is not None:
            deployNodes = cluster.mapping.deployNodes
        
        if (deployNodes is None):
            # infer deployNodes
            topology = cluster.topology
            deployNodeCount = int(topology.nc / topology.cpv)
            deployNodeNames = self.allNodes.getNames()[0:deployNodeCount]
        
        deployedNodes = self.allNodes.getSubset(deployNodeNames)
        
        # reuse socket logic
        self.mapper.mapping = cluster.mapping
        deployedSockets = self.mapper.getDeployedSockets()
        
        # here the "VMs" are actually hosts!
        
        # attributes of VirtualClusterTemplates    
        vmDict = {}
        byNode = []
        
        # iterate over nodes
        for nodeName in deployNodes.getNames():
            # build vmDict and byNode using node data
            vmDict[nodeName] = deployedNodes.getNode(nodeName)
            byNode[nodeName] = nodeName
            
        deployedVMs = VirtualClusterTemplates(vmDict, byNode)
        
        # Case for using PBS
        isPBS = self.configFactory.isPBS(appInfo)
        if isPBS:
            #deploymentType = 'PBS'

            # need to update PBS configuration
            pbsUpdater = PBSUpdater(self.runOpts, forReal)
            pbsUpdater.updatePBS(deployedVMs, cluster)

        else:
            #deploymentType = 'NONE'
            pass

        # deployment tuple
        return (deployedNodes, deployedSockets, deployedVMs)
            
class ClusterXMLGenerator:
    '''
    Produces Cluster XML for VM XML generation, based on VALPA XML and 
    cluster info. Returns the text of the xml.
    '''

    def __init__(self, valpaXML, valpaPrefs):
        self.valpaXML = valpaXML
        self.valpaPrefs = valpaPrefs
        self.loader = FileLoader('.')
        self.valpaXMLFilename = '/tmp/valpa-definition.xml'

    def produceClusterXML(self, topology, technology):
        '''
        Produces Cluster XML for VM XML generation, based on VALPA XML and 
        cluster info. Returns the text of the xml.
        '''
        
        # save clusterXML temporarily
        with open(self.valpaXMLFilename, 'w') as valpaXMLFile:
            valpaXMLFile.write(self.valpaXML)

        # need cpv and disk technology
        cpv = topology.cpv
        networkOpt = technology.networkOpt
        diskOpt = technology.diskOpt
        
        # special case for networking
        if (technology.networkOpt == NetworkOpt.virtio):
            networkDriver = 'qemu'     # <driver name="qemu"/>   - virtIO
        elif (technology.networkOpt == NetworkOpt.vhost):
            networkDriver = 'vhost'    # <driver name="vhost"/>  - vhost
        else:
            networkDriver = ''         # SR-IOV has no such line
            
        # memory
        memoryBase = int(self.valpaPrefs['vm_mem_base'])
        memoryPerCore = int(self.valpaPrefs['vm_mem_core'])
        totalMemory = (memoryBase + memoryPerCore * cpv) * 1024
        
        # cluster path
        clusterPath = self.valpaPrefs['xml_cluster_path']
        
        # gather all substitutions
        args = {'cluster_vcpu' : cpv, 'cluster_memory' : totalMemory,
                'network_option' : networkOpt, 'network_driver' : networkDriver,  
                'cluster_disk_bus' : diskOpt, 'cluster_path' : clusterPath}

        # obtain cluster template from VALPA template
        template = self.loader.load_template(self.valpaXMLFilename)
        clusterXML = template.render(args, loader=self.loader)

        # cores
        #clusterXML = self.valpaXML.replace('_CORE', str(cpv))

        
        #clusterXML = clusterXML.replace('_MEMORY', str(totalMemory))

        # technologies
        #clusterXML = clusterXML.replace('_NET_DRIVER', networkOpt)
        #clusterXML = clusterXML.replace('_DISK_BUS', diskOpt)

        
        #clusterXML = clusterXML.replace('_CLUSTER_PATH', clusterPath)
        
        return clusterXML    
