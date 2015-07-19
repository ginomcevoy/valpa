'''
Created on Nov 5, 2014

@author: giacomo
'''
from core import config_hw
from core import config_vespa
from core.physical import PhysicalNodeFactory
from network.address import NetworkAddresses
from create.vm import BuildsVMDefinitionGenerator
from create.pinning import BuildsPinningWriter
from create.runner import ClusterFactory, ExperimentSetRunner
from network.ips import SetsAddressesToPhysicalCluster,\
    SetsAddressesToAllPossibleVMs
from core.vm import BuildsAllVMDetails
from network.create import BuildsNetworkXMLs, CreatesBasicNetworkXML,\
    ArgumentSolverFactory, EnhancesXMLForCreatingBridge
from create.cluster import VespaXMLGenerator

def doBootstrap(forReal=True, templateDir='../templates', masterTemplate='master.xml', vespaFilename='../input/vespa.params', hardwareFilename='../input/hardware.params', inventoryFilename='../input/vespa.nodes'):
    # instantiate Bootstrapper as a Singleton
    
    if VespaBootstrapper.instance is None:
        VespaBootstrapper.instance = VespaBootstrapper(forReal, templateDir, masterTemplate, vespaFilename, hardwareFilename, inventoryFilename)
        VespaBootstrapper.instance.bootstrap()
        
def getInstance():
    # should have been bootstrapped
    _checkBootstrap()
    return VespaBootstrapper.instance

class VespaBootstrapper():   
    
    # Singleton variable
    instance = None
    
    def __init__(self, forReal, templateDir, masterTemplate, vespaFilename, hardwareFilename, inventoryFilename):
        self.forReal = forReal
        self.vespaFilename = vespaFilename 
        self.hardwareFilename= hardwareFilename
        self.inventoryFilename = inventoryFilename
        self.templateDir = templateDir
        self.masterTemplate = masterTemplate
        self.boostrapped = False
        
        # lazy loading of these
        self.networkAddresses = None
        self.buildsVMDefinitionGenerator = None
        self.clusterFactory = None
        self.experimentSetRunner = None
        self.buildsNetworkXMLs = None
        
    def bootstrap(self):
        # Read Vespa configuration file
        self.vespaConfig = config_vespa.readVespaConfig(self.vespaFilename)
        (self.vespaPrefs, self.vespaXMLOpts, self.runOpts, self.networkingOpts, self.repoOpts) = self.vespaConfig.getAll()
               
        # Read hardware specification
        self.hardwareInfo = config_hw.getHardwareInfo(self.hardwareFilename, self.inventoryFilename)
        self.hwSpecs = self.hardwareInfo.getHwSpecs()
        
        # Produce Vespa XML from master template
        vespaXMLGen = VespaXMLGenerator(self.vespaXMLOpts, self.networkingOpts, self.repoOpts, self.templateDir, self.masterTemplate)
        self.vespaXML = vespaXMLGen.produceVespaXML()
        
        # Load physical cluster object
        nodeFactory = PhysicalNodeFactory(self.hardwareInfo)
        self.physicalCluster = nodeFactory.getAllNodes()
        
        # Load details for all possible VMs
        vmFactory = BuildsAllVMDetails(self.vespaPrefs, self.hwSpecs, self.physicalCluster)
        self.allVMDetails = vmFactory.build()
        
        self.boostrapped = True
        
    def getVespaPrefs(self):
        _checkBootstrap()
        return self.vespaPrefs
    
    def getVespaXMLOpts(self):
        _checkBootstrap()
        return self.vespaXMLOPts
        
    def getNetworkingOpts(self):
        _checkBootstrap()
        return self.networkingOpts
    
    def getRunOpts(self):
        _checkBootstrap()
        return self.runOpts
    
    def getRepoOpts(self):
        _checkBootstrap()
        return self.repoOpts
    
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
            pinningBuilder = BuildsPinningWriter(self.hwSpecs, self.vespaPrefs)
            networkAddresses = self.getNetworkAddresses()
            self.buildsVMDefinitionGenerator = BuildsVMDefinitionGenerator(self.vespaPrefs, pinningBuilder.build(), networkAddresses)
        return self.buildsVMDefinitionGenerator
             
    def getClusterFactory(self):
        _checkBootstrap()
        if self.clusterFactory is None:
            vmDefinitionGenerator = self.getBuildsVMDefinitionGenerator().build()
            self.clusterFactory = ClusterFactory(self.forReal, self.vespaConfig, self.hwSpecs, vmDefinitionGenerator, self.physicalCluster, self.getAllVMDetails(), self.vespaXML)
        return self.clusterFactory
    
    def getExperimentSetRunner(self):
        if self.experimentSetRunner is None:
            clusterFactory = self.getClusterFactory()
            self.experimentSetRunner = ExperimentSetRunner(clusterFactory, self.hwSpecs, self.vespaPrefs, self.forReal)
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
            
            ipSetterPhysical = SetsAddressesToPhysicalCluster(self.networkAddresses)
            ipSetterPhysical.setAddresses(self.physicalCluster)
            ipSetterVirtual = SetsAddressesToAllPossibleVMs(self.networkAddresses, self.physicalCluster)
            ipSetterVirtual.setAddresses(self.allVMDetails)
    
def _checkBootstrap():
    if VespaBootstrapper.instance is None or not VespaBootstrapper.instance.boostrapped:
        raise ValueError('Need to bootstrap first!') 
