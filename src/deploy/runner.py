'''
Created on Oct 15, 2013

@author: giacomo
'''

import ansible.runner
import json
import subprocess

from deploy import parser
from define.cluster import ClusterDefiner, PhysicalClusterDefiner, ClusterXMLGenerator
from run.prepare import PreparesExperiment
from run.config import ConfiguratorFactory
from run.apprunner import RunnerFactory
from run.pbs.updater import PBSUpdater
from deploy.mapping import MappingResolver

class ExperimentSetRunner():
    '''
    Runs all experiments in the experiment XML.
    '''

    def __init__(self, clusterFactory, hwSpecs, vespaPrefs, forReal):
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
        self.vespaPrefs = vespaPrefs
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
        # current implementation uses Ansible using the deployedNodes as inventory
        # TODO: use Ansible Python API and a proper module/playbook
        deployedNodes = deploymentInfo[0]
        nodeFilename = '/tmp/vespa/' + str(clusterRequest) + '-nodes.txt'
        deployedNodes.toFile(nodeFilename)
        hostCount = len(deployedNodes.getNames())

        # call using Ansible API
        ansible_args = '../mgmt/stop-vms-local.sh ' + self.vespaPrefs['vm_prefix']
        runner = ansible.runner.Runner(
            host_list=nodeFilename,
            module_name='script',
            module_args=ansible_args,
            pattern='all',
            forks=hostCount
        )
        
        # call example
        if self.forReal:
            out = runner.run()
            print json.dumps(out, sort_keys=True, indent=4, separators=(',', ': '))            
        else:
            print('ansible: ' + nodeFilename)
            print('ansible: ' + ansible_args)
            
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
    def __init__(self, forReal, vespaConfig, hwSpecs, vmDefinitionGenerator, physicalCluster, allVMDetails, vespaXML):
        # Process Vespa configuration
        (self.vespaPrefs, self.vespaXMLOpts, self.runOpts, self.networkingOpts, self.repoOpts) = vespaConfig.getAll()
       
        self.hwSpecs = hwSpecs
        self.physicalCluster = physicalCluster
        self.allVMDetails = allVMDetails
        
        self.vespaXML = vespaXML
        self.forReal = forReal
        self.vmDefinitionGenerator = vmDefinitionGenerator
        
    def createClusterDefiner(self):
        
        mappingResolver = MappingResolver(self.hwSpecs, self.vespaPrefs, self.physicalCluster, self.allVMDetails)
        clusterXMLGen = ClusterXMLGenerator(self.vespaXML, self.vespaPrefs)
        
        clusterDefiner = ClusterDefiner(mappingResolver, clusterXMLGen, self.vmDefinitionGenerator)
        return clusterDefiner
    
    def createPhysicalClusterDefiner(self):
        clusterDefiner = PhysicalClusterDefiner(self.hwSpecs, self.vespaPrefs, self.runOpts, self.physicalCluster, self.allVMDetails)
        return clusterDefiner
    
    def createClusterDeployer(self):
        return ClusterDeployer(self.forReal, self.hwSpecs, self.runOpts)
        
    def createClusterExecutor(self):
        clusterExecutor = ClusterExecutor(self.forReal, self.vespaPrefs, self.runOpts)
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
        # Create VM given its XML using libvirt call using parallel.
        # Need to create two files: one with the node names, the other
        # with the VM XML definitions. The parallel-based script will 
        # call the create operation using the files.   
        #
        nodeFilename = '/tmp/vespa/' + str(cluster) + '-nodes.txt'
        deployedNodes.toFile(nodeFilename)
        
        definitionFilename = '/tmp/vespa/'+ str(cluster) + '-definitions.txt'
        deployedVMs.definitionsToFile(definitionFilename)
        
        vmFilename = '/tmp/vespa/'+ str(cluster) + '-vms.txt'
        deployedVMs.namesToFile(vmFilename) 
        
        createShellCall = ['/bin/bash', '../mgmt/create-vm-parallel.sh', str(hostCount), nodeFilename, definitionFilename]
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
        # call using Ansible API
        ansible_args = 'mount -a'
        runner = ansible.runner.Runner(
            host_list=vmFilename,
            module_name='command',
            remote_user='root',
            module_args=ansible_args,
            pattern='all',
            forks=vmCount
        )
        if self.forReal:
            out = runner.run()
            print json.dumps(out, sort_keys=True, indent=4, separators=(',', ':'))
        else:
            print('ansible: ' + vmFilename)
            print('ansible: ' + ansible_args)
            
        # Prepare VMs: KNEM
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
    
    def __init__(self, forReal, vespaPrefs, runOpts):
        self.forReal = forReal
        self.runOpts = runOpts

        # need these as strategy
        self.prepsExperiment = PreparesExperiment(forReal, vespaPrefs, runOpts)
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
        executionFile = self.configFactory.createVespaExecutionFile(appRequest, experimentPath)
        
        # apply configuration
        executionFile = appConfigurator.enhanceExecutionFile(executionFile, execConfig)
        executionFile = execConfigurator.enhanceExecutionFile(executionFile, execConfig)
        
        # Run experiments
        appRunner.execute(executionFile, execConfig)

        return (execConfig, executionFile)
