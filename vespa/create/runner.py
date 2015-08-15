'''
Created on Oct 15, 2013

@author: giacomo
'''

from ansible.playbook import PlayBook
from ansible import callbacks, utils, runner
import json
import subprocess
from sys import stdout

from . import parser
from create.cluster import ClusterDefiner, PhysicalClusterDefiner, ClusterXMLGenerator
from submit.pbs.updater import PBSUpdater
from .mapping import MappingResolver
from core.cluster import SetsTechnologyDefaults
from submit.execute import ApplicationExecutor
from submit.prepare import ConfigFileGenerator, PreparesExperiment
from submit.apprunner import RunnerFactory

class ExperimentSetRunner():
    '''
    Runs all experiments in the experiment XML.
    '''

    def __init__(self, deploymentFactory, hwSpecs, createParams, forReal):
        '''
        Constructor, deploymentFactory should have been instantiated by bootstrap
        '''

        # Get a clusterDefiner instance ready to process clusters
        self.clusterDefiner = deploymentFactory.createClusterDefiner()
        self.physicalClusterDefiner = deploymentFactory.createPhysicalClusterDefiner()
        
        # Get a clusterDeployer instance ready
        self.clusterDeployer = deploymentFactory.createClusterDeployer()
        
        # Get an applicationExecutor instance ready
        self.applicationExecutor = deploymentFactory.createApplicationExecutor()
        
        # Strategy to set default Technology values
        self.technologySetter = SetsTechnologyDefaults(createParams)
        
        self.createParams = createParams
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
            clusterRequest = experiment.cluster
            appRequest = experiment.app
            
            # update unset technology parameters with defaults
            t = self.technologySetter.setDefaultsOn(clusterRequest.technology)
            clusterRequest.technology = t 
            
            # validate experiment, skip with message if invalid
            if not experiment.isConsistentWith(self.hwSpecs):
                print("ERROR: Experiment", experiment.name, "cannot be deployed on current hardware!")
                continue
            
            # trials in experiment
            for trial in range(0, experiment.trials):  # @UnusedVariable
                    
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
        error = self.clusterDeployer.deploy(clusterRequest, deploymentInfo, appRequest, self.forReal)
        
        if error is None:                        
            # deployment correct, go on to application execution on the virtual cluster
            self.applicationExecutor.execute(clusterRequest, deploymentInfo, appRequest, self.forReal)
                            
            # wait for application execution
            self.awaitExecution(appRequest)

        # stop the cluster VMs (regardless whether cluster was deployed or not)
        # current implementation uses Ansible using the deployedNodes as inventory
        # TODO: use Ansible Python API and a proper module/playbook
        deployedNodes = deploymentInfo[0]
        nodeFilename = '/tmp/vespa/' + str(clusterRequest) + '-nodes.txt'
        deployedNodes.toFile(nodeFilename)
        hostCount = len(deployedNodes)

        # call meant for Ansible API
        ansible_args = '../mgmt/stop-vms-local.sh ' + self.createParams['vm_prefix']
        
        if self.forReal:
            # Call Ansible runner programmatically
            theRunner = runner.Runner(
                                   host_list=nodeFilename,
                                   module_name='script',
                                   module_args=ansible_args,
                                   pattern='all',
                                   forks=hostCount
                                )
            out = theRunner.run()
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
        self.applicationExecutor.execute(clusterRequest, deploymentInfo, appRequest)
        
        # wait for application execution
        self.awaitExecution(appRequest)
    
    def awaitExecution(self, appRequest):
        isTorque = self.applicationExecutor.isTorqueBased(appRequest)
        waitExecCall = ['/bin/bash', 'submit/wait-end-jobs.sh', appRequest.name, str(isTorque)]
        if self.forReal:
            subprocess.call(waitExecCall)
        else:
            print(waitExecCall)
                    
class DeploymentFactory:
    '''
    Instantiates the ClusterDefiner, ClusterDeployer and ApplicationExecutor.
    '''
    def __init__(self, forReal, vespaConfig, hwSpecs, vmDefinitionGenerator, configFactory, physicalCluster, allVMDetails, vespaXML):

        self.vespaConfig = vespaConfig        
        self.hwSpecs = hwSpecs
        self.physicalCluster = physicalCluster
        self.allVMDetails = allVMDetails
        
        self.vespaXML = vespaXML
        self.forReal = forReal
        
        self.vmDefinitionGenerator = vmDefinitionGenerator
        self.configFactory  = configFactory
        self.appConfig = configFactory.appConfig
        
    def createClusterDefiner(self):
        
        mappingResolver = MappingResolver(self.hwSpecs, self.physicalCluster, self.allVMDetails)
        clusterXMLGen = ClusterXMLGenerator(self.vespaXML, self.vespaConfig.createParams, self.hwSpecs)
        clusterDefiner = ClusterDefiner(mappingResolver, clusterXMLGen, self.vmDefinitionGenerator)
        return clusterDefiner
    
    def createPhysicalClusterDefiner(self):
        clusterDefiner = PhysicalClusterDefiner(self.hwSpecs, self.vespaConfig.submitParams, self.appConfig, self.physicalCluster, self.allVMDetails)
        return clusterDefiner
    
    def createClusterDeployer(self):
        pbsUpdater = PBSUpdater(self.vespaConfig.submitParams, self.forReal)
        return ClusterDeployer(self.configFactory.appConfig, pbsUpdater)
        
    def createApplicationExecutor(self):
        generator = ConfigFileGenerator(self.vespaConfig.submitParams, self.vespaConfig.miscParams)        
        preparesExperiment = PreparesExperiment(generator)
        runnerFactory = RunnerFactory(self.configFactory.appConfig)
        applicationExecutor = ApplicationExecutor(self.configFactory, preparesExperiment, runnerFactory)
        return applicationExecutor 
    
class ClusterDeployer:
    '''
    Deploys a previously defined virtual cluster, while preparing it to submit
    the application.
    '''
    def __init__(self, appConfig, pbsUpdater):
        # strategies 
        self.appConfig = appConfig
        self.pbsUpdater = pbsUpdater
    
    def deploy(self, cluster, deploymentInfo, appRequest, forReal):
        
        (deployedNodes, deployedSockets, deployedVMs) = deploymentInfo  # @UnusedVariable
        print(cluster)
        print(appRequest)
        print('\n')
        stdout.flush()
        
        # Get relevant values
        nc = cluster.topology.nc
        cpv = cluster.topology.cpv
        withKnem = appRequest.appTuning.knem
        
        hostCount = len(deployedNodes)
        vmCount = int(nc / cpv)
        
        # Create VM given its XML using libvirt call using parallel.
        # Need to create two files: one with the node names, the other
        # with the VM XML definitions. The parallel-based script will 
        # call the create operation using the files.   
        nodeFilename = '/tmp/vespa/' + str(cluster) + '-nodes.txt'
        deployedNodes.toFile(nodeFilename)
        definitionFilename = '/tmp/vespa/'+ str(cluster) + '-definitions.txt'
        deployedVMs.definitionsToFile(definitionFilename)
        
        createShellCall = ['/bin/bash', '../mgmt/create-vm-parallel.sh', str(hostCount), nodeFilename, definitionFilename]
        if forReal:
            subprocess.call(createShellCall)
        else:
            print(createShellCall)
                        
        # Deployment over Torque requires special treatment
        if self.appConfig.isTorqueBased(appRequest):
            deploymentType = 'Torque'
            
            # need to update Torque configuration
            self.pbsUpdater.updatePBS(deployedVMs, cluster)
            
        else:
            # indicates non-Torque deployment
            deploymentType = 'Simple'
        
        # Preparation of the VMs is made with the Ansible playbook
        # submit/prepare-vms.yml. The steps are:
        # 1) wait for VMs (use Torque if available, wait for SSH otherwise)    
        # 2) mount the NFS
        # 3) activate KNEM module (if withKnem is True) 
        # The variables are passed in the Ansible inventory, represented
        # by the vmFilename variable.
        vmFilename = '/tmp/vespa/'+ str(cluster) + '-vms.txt'
        inventoryVars = { "vmCount" : str(vmCount), 
                          "deploymentType" : deploymentType,
                          "withKnem" : str(withKnem)
                        }
        deployedVMs.createVirtualInventory(vmFilename, inventoryVars) 
        
        playbookName = 'submit/prepare-vms.yml'
        if forReal:
            # Setup the playbook, execute it and analyze return codes
            stats = callbacks.AggregateStats()
            playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
            runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
            pb = PlayBook(
                          playbook = playbookName,
                          stats = stats,
                          callbacks = playbook_cb,
                          runner_callbacks = runner_cb,
                          host_list=vmFilename,
                          forks=vmCount
                          ) 
            results = pb.run()
            for hostname in results.keys():
                if results[hostname]['failures'] != 0:
                    # Found an error during playbook execution, 
                    # report deployment failure to the caller
                    return "ERROR: Deployment of VMs failed: " + hostname
             
            # Playbook succeeded, inform output
            print json.dumps(results, sort_keys=True, indent=4, separators=(',', ':'))
            stdout.flush()
        else:
            print('ansible: ' + vmFilename)
            print('ansible: ' + playbookName)
        
        # no error in deploying cluster
        return None
                
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
