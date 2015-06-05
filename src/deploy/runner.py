'''
Created on Oct 15, 2013

@author: giacomo
'''
from deploy import parser
from define.cluster import ClusterDefiner, PhysicalClusterDefiner, ClusterXMLGenerator
import subprocess
from run.prepare import PreparesExperiment
from run.config import ConfiguratorFactory
from run.apprunner import RunnerFactory
from run.pbs.updater import PBSUpdater
from deploy.mapping import MappingResolver

class ExperimentSetRunner():
    '''
    Runs all experiments in the experiment XML.
    '''

    def __init__(self, clusterFactory, hwSpecs, forReal):
        '''
        Constructor, clusterFactory should have been instantiated by bootstrap
        '''

        # Get a clusterDefiner instance ready to process clusters
        self.clusterDefiner = clusterFactory.createClusterDefiner()
        self.physicalClusterDefiner = clusterFactory.createPhysicalClusterDefiner()
        
        # Get a clusterDeployer instance ready
        self.clusterDeployer = clusterFactory.createClusterDeployer()
        
        # Get an clusterExecutor instance ready
        self.clusterExecutor = clusterFactory.createClusterExecutor()
        
        self.hwSpecs = hwSpecs
        self.forReal = forReal
        
    def readAndExecute(self, scenarioXML):
        '''
        Parses the scenario XML and runs all scenarios.
        Executes all experiments provided in the scenarios. 
        For each clusterRequest, defines and instantiates the VMs,
        and executes the application.
        
        TODO: separate cluster deployment from application execution? Want to
        start two applications at the same time...
        '''
        # Parse the XML and get the scenarios
        scenarios = parser.parseScenarios(scenarioXML)
        
        for scenario in scenarios:
            
            # assuming single experiment for each scenario
            experiment = scenario.getExperiment()
            
            # validate experiment, skip with message if invalid
            if not experiment.isConsistentWith(self.hwSpecs):
                print("ERROR: Experiment", experiment.name, "cannot be deployed on current hardware!")
                continue
            
            # trials in experiment
            for trial in experiment.trials:  # @UnusedVariable
                    
                # get the request objects
                clusterRequest = experiment.cluster
                appRequest = experiment.app
                    
                if clusterRequest.physicalMachinesOnly:
                    # deploy application on physical hosts
                    self.usePhysicalCluster(experiment, clusterRequest, appRequest)
                    
                else:
                    # deploy application on virtual cluster 
                    self.useVirtualCluster(experiment, clusterRequest, appRequest)
                    
    def useVirtualCluster(self, experiment, clusterRequest, appRequest):
        '''Executes a single application in a virtual cluster'''
        
        # define the actual VMs for the virtual cluster
        # (does not call define funtion of libvirt)
        deploymentInfo = self.clusterDefiner.defineCluster(clusterRequest, experiment.name, self.forReal) 
                        
        # instantiate cluster, may result in error 
        error = self.clusterDeployer.deploy(clusterRequest, deploymentInfo, appRequest)
        
        if error is None:                        
            # deployment correct, go on to application execution on the virtual cluster
            self.clusterExecutor.prepareAndExecute(clusterRequest, deploymentInfo, appRequest)
                            
            # wait for application execution
            self.awaitExecution(appRequest)
                        
        # stop the cluster VMs (regardless whether cluster was deployed or not)
        deployNodeCount = len(deploymentInfo[0].getNames())
        stopVMsCall = ['/bin/bash', '../mgmt/stop-vms-all.sh', str(deployNodeCount)]
        if self.forReal:
            subprocess.call(stopVMsCall)
        else:
            print(stopVMsCall)
            
        # no need to undefine VMs, were not defined
                        
    def usePhysicalCluster(self, experiment, clusterRequest, appRequest):
        '''
        Executes a single application in the physical cluster.
        '''
        # mask PMs as VMs
        deploymentInfo = self.physicalClusterDefiner.defineCluster(clusterRequest, appRequest, self.forReal) 

        # go on to application execution on the cluster
        self.clusterExecutor.prepareAndExecute(clusterRequest, deploymentInfo, appRequest)
        
        # wait for application execution
        self.awaitExecution(appRequest)
    
    def awaitExecution(self, appRequest):
        isPBS = self.clusterDeployer.isPBS(appRequest)
        waitExecCall = ['/bin/bash', 'run/wait-end-jobs.sh', appRequest.name, str(isPBS)]
        if self.forReal:
            subprocess.call(waitExecCall)
        else:
            print(waitExecCall)
                    
class ClusterFactory:
    '''
    Instantiates the ClusterDefiner, ClusterDeployer and ClusterExecutor.
    '''
    def __init__(self, forReal, valpaConfig, hwSpecs, vmDefinitionGenerator, physicalCluster, allVMDetails, valpaXML):
        # Process VALPA configuration
        (self.valpaPrefs, self.valpaXMLOpts, self.runOpts, self.networkingOpts) = valpaConfig.getAll()
       
        self.hwSpecs = hwSpecs
        self.physicalCluster = physicalCluster
        self.allVMDetails = allVMDetails
        
        self.valpaXML = valpaXML
        self.forReal = forReal
        self.vmDefinitionGenerator = vmDefinitionGenerator
        
    def createClusterDefiner(self):
        
        mappingResolver = MappingResolver(self.hwSpecs, self.valpaPrefs, self.physicalCluster, self.allVMDetails)
        clusterXMLGen = ClusterXMLGenerator(self.valpaXML, self.valpaPrefs)
        
        clusterDefiner = ClusterDefiner(mappingResolver, clusterXMLGen, self.vmDefinitionGenerator)
        return clusterDefiner
    
    def createPhysicalClusterDefiner(self):
        clusterDefiner = PhysicalClusterDefiner(self.hwSpecs, self.valpaPrefs, self.runOpts, self.physicalCluster, self.allVMDetails)
        return clusterDefiner
    
    def createClusterDeployer(self):
        return ClusterDeployer(self.forReal, self.hwSpecs, self.runOpts)
        
    def createClusterExecutor(self):
        clusterExecutor = ClusterExecutor(self.forReal, self.valpaPrefs, self.runOpts)
        return clusterExecutor 
                    
class ClusterDeployer:
    '''
    Deploys a previously defined virtual cluster, while preparing it to run
    the application.
    '''
    def __init__(self, forReal, hwSpecs, runOpts):
        self.forReal = forReal
        self.hwSpecs = hwSpecs
        self.runOpts = runOpts
        
        # strategy 
        self.configFactory = ConfiguratorFactory(runOpts)
        
    
    def deploy(self, cluster, deploymentInfo, appRequest):
        
        (deployedNodes, deployedSockets, deployedVMs) = deploymentInfo  # @UnusedVariable
        
        print(cluster)
        #print(deployedVMs.getXMLDict())
        print(appRequest)
        print('\n')
        
        # Get relevant values
        nc = cluster.topology.nc
        cpv = cluster.topology.cpv
        idf = cluster.mapping.idf
        #pinningOpt = cluster.mapping.pinningOpt
        #appName = appRequest.name
        withKnem = appRequest.appTuning.knem
        
        hosts = deployedNodes.getNames()
        hostCount = len(hosts)
        vmCount = int(nc / cpv)
        vmsPerHost = vmCount # if idf == 0
        if idf > 0:
            vmsPerHost = int(idf / cpv)
        
        #
        # Create VM given its XML using libvirt call
        #
        for vmName in deployedVMs.getNames():
            # get defintion and host
            definition = deployedVMs.getDefinitionOf(vmName)
            node = deployedVMs.getHostingNode(vmName)
            createShellCall = ['/bin/bash', '../mgmt/create-vm.sh', node, definition]
            if self.forReal:
                subprocess.call(createShellCall)
            else:
                print(createShellCall)
        
        # Case for using PBS
        isPBS = self.configFactory.isPBS(appRequest)
        if isPBS:
            deploymentType = 'PBS'
            
            # need to update PBS configuration
            pbsUpdater = PBSUpdater(self.runOpts, self.forReal)
            pbsUpdater.updatePBS(deployedVMs, cluster)
            
        else:
            deploymentType = 'NONE'
            
        # Wait for VMs to load
        # "Usage: $0 <deploymentType> <#vms>"
        waitShellCall = ['/bin/bash', 'run/wait-start-vms.sh', deploymentType, str(vmCount)]
        if self.forReal:
            # Waiting for VMs may timeout due to bad instantiation
            waitReturnValue = subprocess.call(waitShellCall)
        else:
            print(waitShellCall)
            waitReturnValue = 0
        
        if waitReturnValue != 0:
            # report deployment failure
            return "ERROR: Waiting for VMs timeout!"
        
        # Prepare VMs: NFS (does nothing if not using NFS)
        #"Usage: $0 <#vms/host> <ACTIVE_NODES>"
        nfsCall = ['/bin/bash', '../mgmt/vcluster-command.sh', 'ssh root@# mount -a', str(vmsPerHost), str(hostCount)]
        if self.forReal:
            subprocess.call(nfsCall)
        else:
            print(nfsCall)
            
        # Prepare VMS: KNEM
        if withKnem:
            knemCall = ['/bin/bash', '../mgmt/vcluster-command.sh', 'ssh root@# modprobe knem', str(vmsPerHost), str(hostCount)]
            if self.forReal:
                subprocess.call(knemCall)
            else:
                print(knemCall)
                
        # no error in deploying cluster
        return None
                
    def isPBS(self, appRequest):
        return self.configFactory.isPBS(appRequest)
            
    def preparePinningCall(self, pinningVirshGen, deployedVMs, vmName, pinningOpt, cpv):
        
        # iterate vms and get pinnings
        host = deployedVMs.getHostname(vmName)
        vmIndex = deployedVMs.getVmIndex(vmName)
        virshCalls = pinningVirshGen.producePinningCalls(pinningOpt, vmIndex, cpv)
            
        # for this vm, join all pinning calls into one 
        virshCall = ''
        for item in virshCalls:
            virshCall += item + '; ' 
        
        # produce ssh call to the host
        pinningCall = ['ssh', host, virshCall]
        return pinningCall

class ClusterExecutor:
    '''
    Executes an application on a previously deployed cluster.
    '''
    
    def __init__(self, forReal, valpaPrefs, runOpts):
        self.forReal = forReal
        self.runOpts = runOpts

        # need these as strategy
        self.prepsExperiment = PreparesExperiment(forReal, valpaPrefs, runOpts)
        self.configFactory = ConfiguratorFactory(runOpts)
        self.runnerFactory = RunnerFactory(self.configFactory, forReal)
    
    def prepareAndExecute(self, clusterRequest, deploymentInfo, appRequest):
        
        # Prepare execution (config file and execution path)
        (execConfig, experimentPath) = self.prepsExperiment.prepare(clusterRequest, deploymentInfo, appRequest)
        
        # Application-specific params
        appParams = self.configFactory.readAppParams(appRequest)
        
        # support classes
        appConfigurator = self.configFactory.createApplicationConfigurator(appRequest, experimentPath, appParams, self.forReal)
        execConfigurator = self.configFactory.createExecutionConfigurator(appRequest, clusterRequest, deploymentInfo)
        appRunner = self.runnerFactory.createAppRunner(appRequest)
        
        # get basic execution file
        executionFile = self.configFactory.createValpaExecutionFile(appRequest, experimentPath)
        
        # apply configuration
        executionFile = appConfigurator.enhanceExecutionFile(executionFile, execConfig)
        executionFile = execConfigurator.enhanceExecutionFile(executionFile, execConfig)
        
        # Run experiments
        appRunner.execute(executionFile, execConfig)

        return (execConfig, executionFile)
