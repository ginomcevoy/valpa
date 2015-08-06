'''
Created on Nov 5, 2014

@author: giacomo
'''
from core import config_hw, config_app
from core import config_vespa
from core.physical import PhysicalNodeFactory
from network.address import NetworkAddresses
from create.vm import BuildsVMDefinitionGenerator
from create.pinning import BuildsPinningWriter
from create.runner import DeploymentFactory, ExperimentSetRunner
from network.ips import SetsAddressesToPhysicalCluster,\
    SetsAddressesToAllPossibleVMs
from core.virtual import BuildsAllVMDetails
from network.create import BuildsNetworkXMLs, CreatesBasicNetworkXML,\
    ArgumentSolverFactory, EnhancesXMLForCreatingBridge
from create.cluster import VespaXMLGenerator
from submit.config import ConfiguratorFactory
from collections import namedtuple

def doBootstrap(forReal=True, templateDir='../templates', masterTemplate='master.xml', vespaFilename='../input/vespa.params', hardwareFilename='../input/hardware.params', inventoryFilename='../input/vespa.nodes', appFolder='../apps'):
    # instantiate Bootstrapper as a Singleton
    
    if VespaBootstrapper.instance is None:
        VespaBootstrapper.instance = VespaBootstrapper(forReal, templateDir, masterTemplate, vespaFilename, hardwareFilename, inventoryFilename, appFolder)
        VespaBootstrapper.instance.bootstrap()
        
def getInstance():
    # should have been bootstrapped
    _checkBootstrap()
    return VespaBootstrapper.instance

class VespaBootstrapper():   
    
    # Singleton variable
    instance = None
    
    def __init__(self, forReal, templateDir, masterTemplate, vespaFilename, hardwareFilename, inventoryFilename, appFolder):
        self.forReal = forReal
        self.vespaFilename = vespaFilename 
        self.hardwareFilename= hardwareFilename
        self.inventoryFilename = inventoryFilename
        self.templateDir = templateDir
        self.masterTemplate = masterTemplate
        self.appFolder = appFolder
        self.boostrapped = False
        
        # lazy loading of these
        self.networkAddresses = None
        self.buildsVMDefinitionGenerator = None
        self.appConfig = None
        self.configFactory = None
        self.deploymentFactory = None
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
        
    def getAllConfig(self):
        return (self.vespaPrefs, self.vespaXMLOpts, self.runOpts, self.networkingOpts, self.repoOpts)
        
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
    
    def getAppConfig(self):
        _checkBootstrap()
        if self.appConfig is None:
            self.appConfig = config_app.getAppConfig(self.appFolder)
        return self.appConfig
    
    def getConfiguratorFactory(self):
        _checkBootstrap()
        if self.configFactory is None:
            networkAddresses = self.getNetworkAddresses()
            appConfig = self.getAppConfig()
            self.configFactory = ConfiguratorFactory(self.runOpts, appConfig, networkAddresses)
        return self.configFactory
        
    def getDeploymentFactory(self):
        _checkBootstrap()
        if self.deploymentFactory is None:
            vmDefinitionGenerator = self.getBuildsVMDefinitionGenerator().build()
            configFactory = self.getConfiguratorFactory()
            self.deploymentFactory = DeploymentFactory(self.forReal, self.vespaConfig, self.hwSpecs,
                                                  vmDefinitionGenerator, configFactory, 
                                                  self.physicalCluster, self.getAllVMDetails(), 
                                                  self.vespaXML)
        return self.deploymentFactory
    
    def getExperimentSetRunner(self):
        if self.experimentSetRunner is None:
            deploymentFactory = self.getDeploymentFactory()
            self.experimentSetRunner = ExperimentSetRunner(deploymentFactory, self.hwSpecs, self.vespaPrefs, self.forReal)
        return self.experimentSetRunner
    
    def getBuildsNetworkXMLs(self):
        if self.buildsNetworkXMLs is None:
            basicCreator = CreatesBasicNetworkXML()
            physicalCluster = self.getPhysicalCluster()
            argumentSolverFactory = ArgumentSolverFactory(self.networkingOpts, self.getNetworkAddresses())
            enhancerForCreatingBridge = EnhancesXMLForCreatingBridge(physicalCluster, self.getAllVMDetails())
            self.buildsNetworkXMLs = BuildsNetworkXMLs(basicCreator, argumentSolverFactory, enhancerForCreatingBridge, physicalCluster)
        return self.buildsNetworkXMLs
    
    def getConsolidateConfig(self, appName):
        """ Return a named tuple that holds configuration relevant to consolidation.
        
        The tuple holds the names 'appParams', 'consolidatePrefs', 'hwSpecs', 'runOpts'.
        """
        appConfig = self.getAppConfig()
        appParams = appConfig.appConfigs[appName]
    
        # Single variable for relevant configuration
        ConsolidateConfig = namedtuple('ConsolidateConfig', ['appParams', 'consolidatePrefs', 'hwSpecs', 'runOpts'])
        return ConsolidateConfig(appParams, self.vespaConfig.consolidatePrefs, self.hwSpecs, self.runOpts)
    
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
