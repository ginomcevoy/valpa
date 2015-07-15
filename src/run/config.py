'''
Created on Oct 31, 2013

Configures application (PBS if supported) for execution

@author: giacomo
'''
import shutil
import ConfigParser
import datetime
from bean.enum import MPIBindOpt

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
    
    def __init__(self, runOpts):
        self.runOpts = runOpts
        
    def enhanceExecutionFile(self, executionFile, execConfig=None):
        # Get values from Vespa run options
        timeFormat = self.runOpts['run_timeformat']
        timeOutput = self.runOpts['run_timeoutput']
        
        monitorStart = self.runOpts['monitor_start']
        monitorStop = self.runOpts['monitor_stop']
        monitorPreProcess = self.runOpts['monitor_preprocess']
        monitorDoNodes = self.runOpts['monitor_do_nodes']
        monitorApp = self.runOpts['monitor_app']
        
        # replace in execution file
        with open(executionFile, 'r') as execution:
            executionText = execution.read()
            executionText = executionText.replace('&TIME_FORMAT', timeFormat)
            executionText = executionText.replace('&TIME_OUTPUT', timeOutput)
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
    
    def __init__(self, appInfo, experimentPath, appParams, forReal):
        self.appInfo = appInfo
        self.forReal = forReal
        self.experimentPath = experimentPath
        self.appParams = appParams

    def enhanceExecutionFile(self, executionFile, execConfig=None):
        
        # replace in execution file
        with open(executionFile, 'r') as execution:
            executionText = execution.read()
            
            # Provided in request
            executionText = executionText.replace('&EXEC_TIMES', str(self.appInfo.runs))
            executionText = executionText.replace('&EXPERIMENT_PATH', self.experimentPath)
            executionText = executionText.replace('&APP_ARGS', self.appInfo.args)

            # OpenMPI 1.8.x has simplified the binding syntax            
            bindToCore = '--bind-to ' + self.appInfo.appTuning.procpin
            executionText = executionText.replace('&MPI_PROC_BIND', bindToCore)
            
            # Inferred from name/date
            if self.forReal:
                now = datetime.datetime.now()
                dateString = now.strftime('%Y-%m-%d-%H:%M')
            else:
                dateString = '2013-04-06-08:55' # for testing
            appExecName = self.appInfo.name + '-' + dateString
            executionText = executionText.replace('&APP_EXEC_NAME', appExecName)
            
            # From registration in Vespa
            executionText = executionText.replace('&APP_HOME', self.appParams['app.home'])
            executionText = executionText.replace('&APP_EXECUTABLE', self.appParams['app.executable'])
            executionText = executionText.replace('&WALLTIME', self.appParams['exec.walltime'])
            
            needsOutputCopy = self.appParams['exec.needsoutputcopy']
            executionText = executionText.replace('&APP_NEEDS_OUTPUT_COPY', needsOutputCopy)
            
            if needsOutputCopy == 'Y':
                otherOutput = self.appParams['exec.otheroutput']
                outputRename = self.appParams['exec.outputrename']
            else:
                otherOutput = '/dev/null'
                outputRename = ''
            
            executionText = executionText.replace('&APP_OTHER_OUTPUT', otherOutput)
            executionText = executionText.replace('&APP_OUTPUT_RENAME', outputRename)
        
        with open(executionFile, 'w') as execution:
            execution.write(executionText)
            
        return executionFile
    

    
class ExecutionConfiguratorPBS(ExecutionConfigurator):
    '''
    Adds execution information to PBS submission file
    '''
    
    def __init__(self, clusterInfo, deploymentInfo):
        self.clusterInfo = clusterInfo
        self.deploymentInfo = deploymentInfo        

    def enhanceExecutionFile(self, executionFile, execConfig=None):
        
        # replace in execution file
        with open(executionFile, 'r') as execution:
            executionText = execution.read()
            
            # Replace #processes (= #cores in cluster)
            nc = self.clusterInfo.topology.nc
            executionText = executionText.replace('&NC', str(nc))
            
            # Replace VM list (for specifying PBS nodes and their ppn)
            topologyString = self.createTopologyString()
            executionText = executionText.replace('&PBS_TOPOLOGY', topologyString)
            
            # Replace node list (for monitoring nodes)
            nodeList = self.deploymentInfo[0].getNames()
            nodeText = ''
            for node in nodeList:
                nodeText += node + '\\n'
            executionText = executionText.replace('&PHYSICAL_NODE_LIST', nodeText)
            
        with open(executionFile, 'w') as execution:
            execution.write(executionText)
        
        return executionFile
    
    def createTopologyString(self):
        '''
        Returns a string appropriate for the #PBS -l nodes= statement.
        Example of a string:
        kvm-pbs082-01:ppn=4+kvm-pbs082-02:ppn=4+kvm-pbs083-01:ppn=4+kvm-pbs083-02:ppn=4
        '''
        vmList = self.deploymentInfo[2].getNames()
        cpv = self.clusterInfo.topology.cpv
        topologyString = ''
         
        for vmName in vmList:
            topologyString = topologyString + vmName + ':ppn=' + str(cpv) + '+'
        topologyString = topologyString[0 : len(topologyString)-1]
        return topologyString
    
class ConfiguratorFactory:
    '''
    Creates instances for configuration of application execution,
    also creates a copy of the master execution file. 
    
    TODO: rethink this class using patterns, is PBS optional here?
    '''
    def __init__(self, runOpts):
        self.runOpts = runOpts
        self.masterPbs = runOpts['pbs_master'] 
        self.pbsApps = runOpts['pbs_supported_apps'].split(',')
    
    def createBasicExecutionFile(self, appInfo, experimentPath):
        '''
        If using PBS, returns a copy of the Vespa PBS file (master version)
        in the provided experimentPath 
        '''
        if self.isPBS(appInfo):
            # is PBS
            # copy the master PBS file to experiment path
            pbsFile = experimentPath + '/submit.pbs'
            shutil.copyfile(self.masterPbs, pbsFile)
            
        else:
            # only supporting PBS
            raise ValueError("Application not supported: " + appInfo.name)
        
        return pbsFile
    
    def createVespaExecutionFile(self, appInfo, experimentPath):
        '''
        If using PBS, returns a copy of the Vespa PBS file (adapted version)
        in the provided experimentPath 
        '''
        executionFile = self.createBasicExecutionFile(appInfo, experimentPath)
        vespaConfigurator = VespaConfigurator(self.runOpts)
        return vespaConfigurator.enhanceExecutionFile(executionFile)
        
    def createApplicationConfigurator(self, appInfo, experimentPath, appParams, forReal=True):
        '''
        Returns ApplicationConfigurator instance, with PBS if supported.
        '''
        if self.isPBS(appInfo):
            return ApplicationConfiguratorPBS(appInfo, experimentPath, appParams, forReal)
        else:
            raise ValueError("Application not supported: " + appInfo.name)
    
    def createExecutionConfigurator(self, appInfo, clusterInfo, deploymentInfo):
        '''
        Returns ExecutionConfigurator instance, with PBS if supported.
        '''
        if self.isPBS(appInfo):
            return ExecutionConfiguratorPBS(clusterInfo, deploymentInfo)
        else:
            raise ValueError("Application not supported: " + appInfo.name)
    
    def isPBS(self, appInfo):
        return appInfo.name in self.pbsApps
    
    def readAppParams(self, appInfo):
        '''
        Reads application params that are registered with Vespa
        (not provided in the request), returns dict
        '''
        appParamsFile = '../apps/' + appInfo.name + '.params'
        config = ConfigParser.RawConfigParser()
        config.read(appParamsFile)
        return dict(config.items('Application'))