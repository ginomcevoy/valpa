'''
Created on Nov 4, 2013

@author: giacomo
'''
import subprocess

class AppRunnerAbstract(object):
    '''
    Runs an application on a virtual cluster, using an executionFile and configuration options
    '''

    def __init__(self, appInfo, forReal):
        self.appInfo = appInfo
        self.forReal = forReal
        
    def execute(self, executionFile, execConfig=None):
        pass

class AppRunnerPBS(AppRunnerAbstract):
    '''
    Runs an application on a virtual cluster using PBS.
    '''

    def __init__(self, appInfo, forReal):
        super(AppRunnerPBS, self).__init__(appInfo, forReal)
        
    def execute(self, executionFile, execConfig=None):
        # Just submit the file, it has all the information needed for PBS.
        submissionCall = ['qsub', executionFile]
        
        if self.forReal:
            subprocess.call(submissionCall)
        else:
            print(submissionCall)

class RunnerFactory:
    
    def __init__(self, configFactory, forReal):
        self.configFactory = configFactory
        self.forReal = forReal
    
    def createAppRunner(self, appInfo):
        if self.configFactory.isPBS(appInfo):
            return AppRunnerPBS(appInfo, self.forReal)
        else:
            # only PBS for now
            raise ValueError('Only PBS...')