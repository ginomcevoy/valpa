
from .prepare import PreparesExperiment
from .apprunner import RunnerFactory

class ApplicationExecutor:
    '''
    Executes an application on a previously deployed cluster.
    '''
    
    def __init__(self, configFactory, forReal, vespaPrefs, runOpts):
        self.forReal = forReal
        self.runOpts = runOpts

        # need these as strategy
        self.prepsExperiment = PreparesExperiment(forReal, vespaPrefs, runOpts)
        self.configFactory = configFactory
        self.runnerFactory = RunnerFactory(self.configFactory, forReal)
    
    def execute(self, clusterRequest, deploymentInfo, appRequest):
        
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
