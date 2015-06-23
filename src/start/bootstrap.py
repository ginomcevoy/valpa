'''
Created on Nov 5, 2014

@author: giacomo
'''
from config import valpaconfig, hwconfig
from bean.node import PhysicalNodeFactory
from network.address import NetworkAddresses
from define.vm import BuildsVMDefinitionGenerator
from deploy.pinning import BuildsPinningWriter
from deploy.runner import ClusterFactory, ExperimentSetRunner
from network.ips import SetsIpAddressesToPhysicalCluster,\
    SetsAddressesToAllPossibleVMs
from bean.vm import BuildsAllVMDetails
from network.create import BuildsNetworkXMLs, CreatesBasicNetworkXML,\
    ArgumentSolverFactory, EnhancesXMLForCreatingBridge
from define.cluster import ValpaXMLGenerator

def doBootstrap(forReal=True, masterXML='../templates/master.xml', valpaFilename='../input/valpa.params', hardwareFilename='../input/hardware.params'):
    # instantiate Bootstrapper as a Singleton
    
    if ValpaBoostrapper.instance is None:
        ValpaBoostrapper.instance = ValpaBoostrapper(forReal, masterXML, valpaFilename, hardwareFilename)
        ValpaBoostrapper.instance.bootstrap()
        
def getInstance():
    # should have been bootstrapped
    _checkBootstrap()
    return ValpaBoostrapper.instance

class ValpaBoostrapper():
    
    # Singleton variable
    instance = None
    
    def __init__(self, forReal, masterXML, valpaFilename, hardwareFilename):
        self.forReal = forReal
        self.valpaFilename = valpaFilename 
        self.hardwareFilename= hardwareFilename
        self.masterXML = masterXML
        self.boostrapped = False
        
        # lazy loading of these
        self.networkAddresses = None
        self.buildsVMDefinitionGenerator = None
        self.clusterFactory = None
        self.experimentSetRunner = None
        self.buildsNetworkXMLs = None
        
    def bootstrap(self):
        # Read VALPA configuration file
        self.valpaConfig = valpaconfig.readValpaConfig(self.valpaFilename)
        (self.valpaPrefs, self.valpaXMLOpts, self.runOpts, self.networkingOpts, self.repoOpts) = self.valpaConfig.getAll()
               
        # Read hardware specification
        self.hardwareInfo = hwconfig.getHardwareInfo(self.hardwareFilename)
        self.hwSpecs = self.hardwareInfo.getHwSpecs()
        
        # Produce VALPA XML from master template
        valpaXMLGen = ValpaXMLGenerator(self.valpaXMLOpts, self.networkingOpts, self.repoOpts, self.masterXML)
        self.valpaXML = valpaXMLGen.produceValpaXML()
        
        # Load physical cluster object
        nodeFactory = PhysicalNodeFactory(self.hardwareInfo)
        self.physicalCluster = nodeFactory.getAllNodes()
        
        # Load details for all possible VMs
        vmFactory = BuildsAllVMDetails(self.valpaPrefs, self.hwSpecs, self.physicalCluster)
        self.allVMDetails = vmFactory.build()
        
        self.boostrapped = True
        
    def getValpaPrefs(self):
        _checkBootstrap()
        return self.valpaPrefs
    
    def getValpaXMLOpts(self):
        _checkBootstrap()
        return self.valpaXMLOPts
        
    def getNetworkingOpts(self):
        _checkBootstrap()
        return self.networkingOpts
    
    def getRunOpts(self):
        _checkBootstrap()
        return self.runOpts
    
    def getHwSpecs(self):
        _checkBootstrap()
        return self.hwSpecs
    
    def getPhysicalCluster(self):
        _checkBootstrap()
        self.__loadNetworkAddresses__()
        return self.physicalCluster
    
    def getAllVMDetails(self):
        _checkBootstrap()
        self.__loadNetworkAddresses__()
        return self.allVMDetails
    
    def getNetworkAddresses(self):
        _checkBootstrap()
        self.__loadNetworkAddresses__()
        return self.networkAddresses
    
    def getBuildsVMDefinitionGenerator(self):
        _checkBootstrap()
        if self.buildsVMDefinitionGenerator is None:
            pinningBuilder = BuildsPinningWriter(self.hwSpecs, self.valpaPrefs)
            networkAddresses = self.getNetworkAddresses()
            self.buildsVMDefinitionGenerator = BuildsVMDefinitionGenerator(self.valpaPrefs, pinningBuilder.build(), networkAddresses)
        return self.buildsVMDefinitionGenerator
             
    def getClusterFactory(self):
        _checkBootstrap()
        if self.clusterFactory is None:
            vmDefinitionGenerator = self.getBuildsVMDefinitionGenerator().build()
            self.clusterFactory = ClusterFactory(self.forReal, self.valpaConfig, self.hwSpecs, vmDefinitionGenerator, self.physicalCluster, self.getAllVMDetails(), self.valpaXML)
        return self.clusterFactory
    
    def getExperimentSetRunner(self):
        if self.experimentSetRunner is None:
            clusterFactory = self.getClusterFactory()
            self.experimentSetRunner = ExperimentSetRunner(clusterFactory, self.hwSpecs, self.valpaPrefs, self.forReal)
        return self.experimentSetRunner
    
    def getBuildsNetworkXMLs(self):
        if self.buildsNetworkXMLs is None:
            basicCreator = CreatesBasicNetworkXML()
            physicalCluster = self.getPhysicalCluster()
            argumentSolverFactory = ArgumentSolverFactory(self.networkingOpts, self.getNetworkAddresses())
            enhancerForCreatingBridge = EnhancesXMLForCreatingBridge(physicalCluster, self.getAllVMDetails())
            self.buildsNetworkXMLs = BuildsNetworkXMLs(basicCreator, argumentSolverFactory, enhancerForCreatingBridge, physicalCluster)
        return self.buildsNetworkXMLs
    
    def __loadNetworkAddresses__(self):
        '''
        Loads IP addresses of physical and virtual clusters
        '''
        if self.networkAddresses is None:
            # Load networking and IP addresses to physical nodes and VMs
            self.networkAddresses = NetworkAddresses(self.networkingOpts, self.physicalCluster, self.hwSpecs)
            
            ipSetter = SetsIpAddressesToPhysicalCluster(self.networkAddresses)
            ipSetter.setIpAddresses(self.physicalCluster)
            vmAddressing = SetsAddressesToAllPossibleVMs(self.networkAddresses, self.physicalCluster)
            vmAddressing.setAddresses(self.allVMDetails)
    
def _checkBootstrap():
    if ValpaBoostrapper.instance is None or not ValpaBoostrapper.instance.boostrapped:
        raise ValueError('Need to bootstrap first!') 
