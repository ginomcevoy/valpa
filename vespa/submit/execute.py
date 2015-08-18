
class ApplicationExecutor:
    '''
    Executes an application on a previously deployed cluster.
    '''
    
    def __init__(self, configFactory, preparesExperiment, runnerFactory):
        
        # need these as strategies
        self.prepsExperiment = preparesExperiment 
        self.configFactory = configFactory
        self.runnerFactory = runnerFactory
    
    def execute(self, clusterRequest, deploymentInfo, appRequest, forReal):
        
        # Prepare execution (config file and execution path)
        (execConfig, experimentPath) = self.prepsExperiment.prepare(clusterRequest, deploymentInfo, appRequest, forReal)
        
        # support classes
        appConfigurator = self.configFactory.createApplicationConfigurator(appRequest, experimentPath, forReal)
        execConfigurator = self.configFactory.createExecutionConfigurator(appRequest, clusterRequest, deploymentInfo)
        appRunner = self.runnerFactory.createAppRunner(appRequest, forReal)
        
        # get basic execution file
        executionFile = self.configFactory.createVespaExecutionFile(appRequest, experimentPath)
        
        # apply configuration
        executionFile = appConfigurator.enhanceExecutionFile(executionFile, execConfig)
        executionFile = execConfigurator.enhanceExecutionFile(executionFile, execConfig)
        
        # Run experiments
        appRunner.execute(executionFile, execConfig)

        return (execConfig, executionFile)
    
    def isTorqueBased(self, appRequest):
        return self.configFactory.appConfig.isTorqueBased(appRequest)
