'''
Created on Oct 31, 2013

Configures application (PBS if supported) for execution

@author: giacomo
'''
import shutil
import datetime

class Configurator:
    
    def enhanceExecutionFile(self, executionFile, execConfig):
        pass

class ApplicationConfigurator(Configurator):
    '''
    Adds application information to execution file (generic)
    '''
    
    def enhanceExecutionFile(self, executionFile, execConfig):
        pass
    
class ExecutionConfigurator(Configurator):
    '''
    Adds execution information to execution file (generic)
    '''

    def enhanceExecutionFile(self, executionFile, execConfig):
        return executionFile
    
class VespaConfigurator(Configurator):
    
    def __init__(self, submitParams):
        self.submitParams = submitParams
        
    def enhanceExecutionFile(self, executionFile, execConfig=None):
        # Get values from Vespa submit options
        timeFormat = self.submitParams['run_timeformat']
        timeOutput = self.submitParams['run_timeoutput']
        
        monitorRun = self.submitParams['monitor_run']
        monitorStart = '/'.join((self.submitParams['vespa_home'],
                                self.submitParams['monitor_start']))
        monitorStop = '/'.join((self.submitParams['vespa_home'],
                               self.submitParams['monitor_stop']))
        monitorPreProcess = '/'.join((self.submitParams['vespa_home'],
                                      self.submitParams['monitor_preprocess']))
        monitorDoNodes = self.submitParams['monitor_do_nodes']
        monitorApp = self.submitParams['monitor_app']
        
        # replace in execution file
        with open(executionFile, 'r') as execution:
            executionText = execution.read()
            executionText = executionText.replace('&TIME_FORMAT', timeFormat)
            executionText = executionText.replace('&TIME_OUTPUT', timeOutput)
            executionText = executionText.replace('&MONITOR_RUN', monitorRun)
            executionText = executionText.replace('&MONITOR_START', monitorStart)
            executionText = executionText.replace('&MONITOR_STOP', monitorStop)
            executionText = executionText.replace('&MONITOR_PREPROCESS', monitorPreProcess)
            executionText = executionText.replace('&MONITOR_DO_NODES', monitorDoNodes)
            executionText = executionText.replace('&MONITOR_APP', monitorApp)
        
        with open(executionFile, 'w') as execution:
            execution.write(executionText)
            
        return executionFile

class ApplicationConfiguratorPBS(ApplicationConfigurator):
    '''
    Adds application information to PBS submission file
    '''
    
    def __init__(self, appRequest, experimentPath, appParams, forReal):
        self.appRequest = appRequest
        self.forReal = forReal
        self.experimentPath = experimentPath
        self.appParams = appParams

    def enhanceExecutionFile(self, executionFile, execConfig=None):
        
        # replace in execution file
        with open(executionFile, 'r') as execution:
            executionText = execution.read()
            
            # Provided in request
            executionText = executionText.replace('&EXEC_TIMES', str(self.appRequest.runs))
            executionText = executionText.replace('&EXPERIMENT_PATH', self.experimentPath)
            
            # Application arguments: use the args provided in the configuration, unless
            # overridden in the application request
            if self.appRequest.args is not None:
                appArgs = self.appRequest.args
            else:
                appArgs = self.appParams['app.args']
            
            executionText = executionText.replace('&APP_ARGS', appArgs)

            # OpenMPI 1.8.x has simplified the binding syntax            
            bindToCore = '--bind-to ' + self.appRequest.appTuning.procpin
            executionText = executionText.replace('&MPI_PROC_BIND', bindToCore)
            
            # Inferred from name/date
            if self.forReal:
                now = datetime.datetime.now()
                dateString = now.strftime('%Y-%m-%d-%H:%M')
            else:
                dateString = '2013-04-06-08:55' # for testing
            appExecName = self.appRequest.name + '-' + dateString
            executionText = executionText.replace('&APP_EXEC_NAME', appExecName)
            
            # From registration in Vespa
            executionText = executionText.replace('&APP_HOME', self.appParams['app.home'])
            executionText = executionText.replace('&APP_EXECUTABLE', self.appParams['app.executable'])
            executionText = executionText.replace('&WALLTIME', self.appParams['exec.walltime'])
            
            if 'exec.otheroutput' in self.appParams and self.appParams['exec.otheroutput']:
                # additional output requested
                needsOutputCopy = 'Y'
                otherOutput = self.appParams['exec.otheroutput']
                outputRename = self.appParams['exec.outputrename']
            else:
                # indicate no need for handling additional output
                needsOutputCopy = 'N'
                otherOutput = '/dev/null'
                outputRename = ''
                
            executionText = executionText.replace('&APP_NEEDS_OUTPUT_COPY', needsOutputCopy)
            executionText = executionText.replace('&APP_OTHER_OUTPUT', otherOutput)
            executionText = executionText.replace('&APP_OUTPUT_RENAME', outputRename)
        
        with open(executionFile, 'w') as execution:
            execution.write(executionText)
            
        return executionFile
    

    
class ExecutionConfiguratorPBS(ExecutionConfigurator):
    '''
    Adds execution information to PBS submission file
    '''
    
    def __init__(self, clusterRequest, deploymentInfo, networkAddresses):
        self.clusterRequest = clusterRequest
        self.deploymentInfo = deploymentInfo        
        self.networkAddresses = networkAddresses

    def enhanceExecutionFile(self, executionFile, execConfig=None):
        
        # replace in execution file
        with open(executionFile, 'r') as execution:
            executionText = execution.read()
            
            # Replace #processes (= #cores in cluster)
            nc = self.clusterRequest.topology.nc
            executionText = executionText.replace('&NC', str(nc))
            
            # Replace VM list (for specifying PBS nodes and their ppn)
            topologyString = self.createTopologyString()
            executionText = executionText.replace('&PBS_TOPOLOGY', topologyString)
            
            # Replace node list (for monitoring nodes)
            nodeList = self.deploymentInfo[0].nodeNames
            nodeText = ''
            for node in nodeList:
                nodeText += node + '\\n'
            executionText = executionText.replace('&PHYSICAL_NODE_LIST', nodeText)
            
            # Replace networking string for OpenMPI call
            networkingString = self.createNetworkingString()
            executionText = executionText.replace('&MPI_BTL', networkingString)
            
        with open(executionFile, 'w') as execution:
            execution.write(executionText)
        
        return executionFile
    
    def createTopologyString(self):
        '''
        Returns a string appropriate for the #PBS -l nodes= statement.
        Example of a string:
        kvm-pbs082-01:ppn=4+kvm-pbs082-02:ppn=4+kvm-pbs083-01:ppn=4+kvm-pbs083-02:ppn=4
        '''
        deployedVMs = self.deploymentInfo[2]
        cpv = self.clusterRequest.topology.cpv
        topologyString = ''
         
        for vm in deployedVMs:
            topologyString = topologyString + vm.name + ':ppn=' + str(cpv) + '+'
        topologyString = topologyString[0 : len(topologyString)-1]
        return topologyString
    
    def createNetworkingString(self):
        """Return a string appropriate for the BTL inter-process communication
        of OpenMPI. The following values are needed:
        
        For non-Infiniband, class B network:
        --mca btl_tcp_if_include 172.16.0.0/16 --mca btl self,sm,tcp
        
        For non-Infiniband, class C network:
        --mca btl_tcp_if_include 192.168.3.0/24 --mca btl self,sm,tcp

        For Infiniband:
        --mca btl self,sm,openib
        
        The calculation of network CIDR is delegated to networkAddresses. 
        """
        withInfiniband = self.clusterRequest.technology.infinibandFlag
        if withInfiniband:
            networkingString = '--mca btl self,sm,openib'
        else:
            cidr = self.networkAddresses.networkCIDR()
            networkingString = '--mca btl_tcp_if_include ' + cidr + ' --mca btl self,sm,tcp'
        return networkingString
    
class ConfiguratorFactory:
    """ Creates instances for configuration of application execution,
    also creates a copy of the master execution file. 
    
    """
    def __init__(self, submitParams, appConfig, networkAddresses):
        self.submitParams = submitParams
        self.masterPbs = submitParams['pbs_master'] 
        self.networkAddresses = networkAddresses
        self.appConfig = appConfig
    
    def createBasicExecutionFile(self, appRequest, experimentPath):
        """
        If using Torque, returns a copy of the Vespa Torque file 
        (master version) in the provided experimentPath 
        """
        if self.appConfig.isTorqueBased(appRequest):
            # copy the master Torque file to experiment path
            pbsFile = experimentPath + '/submit.pbs'
            shutil.copyfile(self.masterPbs, pbsFile)
            
        else:
            # only supporting PBS
            raise ValueError("Application not supported: " + appRequest.name)
        
        return pbsFile
    
    def createVespaExecutionFile(self, appRequest, experimentPath):
        """
        If using Torque, returns a copy of the Vespa Torque file
        (adapted version) in the provided experimentPath 
        """
        executionFile = self.createBasicExecutionFile(appRequest, experimentPath)
        vespaConfigurator = VespaConfigurator(self.submitParams)
        return vespaConfigurator.enhanceExecutionFile(executionFile)
        
    def createApplicationConfigurator(self, appRequest, experimentPath, forReal=True):
        """ Return ApplicationConfigurator instance, with PBS if supported.
        """
        if self.appConfig.isTorqueBased(appRequest):
            appParams = self.appConfig.getConfigFor(appRequest)
            return ApplicationConfiguratorPBS(appRequest, experimentPath, appParams, forReal)
        else:
            raise ValueError("Application not supported: " + appRequest.name)
    
    def createExecutionConfigurator(self, appRequest, clusterRequest, deploymentInfo):
        '''
        Returns ExecutionConfigurator instance, with PBS if supported.
        '''
        if self.appConfig.isTorqueBased(appRequest):
            return ExecutionConfiguratorPBS(clusterRequest, deploymentInfo, self.networkAddresses)
        else:
            raise ValueError("Application not supported: " + appRequest.name)
    