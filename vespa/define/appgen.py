'''
Created on Sep 29, 2014

@author: giacomo
'''
from core.enum import MPIBindOpt
from core.experiment import AppTuning, Application

def chooseRequestFactory(appName):
    # if name == 'myApp':
    # return MyAppFactory()
    
    # by default 
    return AppRequestAbstractFactory()

class AppRequestAbstractFactory():
    '''
    Generates a list of ApplicationRequest objects based on a particular
    application and a specification. By default, produces requests with 
    no arguments.  
    '''

    def generateFor(self, appGenerationSpec, clusterRequest):
        # use spec to create most of the ApplicationRequest objects
        appRequests = []
        
        name = appGenerationSpec.name
        runs = appGenerationSpec.runs
        
        for procpinOption in appGenerationSpec.procpinTuple:
            for knemOption in appGenerationSpec.knemTuple:
                appTuning = AppTuning(procpinOption, knemOption)
                args = self.createArgs(appGenerationSpec, clusterRequest)
                appRequest = Application(name, runs, args, appTuning)
                appRequests.append(appRequest)
        
        return appRequests
        
    def createArgs(self, appGenerationSpec, clusterRequest):
        '''
        Subclasses should implement this method to generate arguments that
        are sensitive to the context.
        '''
        return '' # by default, no arguments

class AppRequestGenerator():
    '''
    Generates a list of ApplicationRequest objects according to a specification, 
    with a particular clusterRequest instance as context.
    '''
    
    def generateFor(self, appGenerationSpec, clusterRequest):
        appName = appGenerationSpec.name
        requestFactory = chooseRequestFactory(appName)
        return requestFactory.generateFor(appGenerationSpec, clusterRequest)
        
class ApplicationGenerationSpecification():
    
    def __init__(self, name, runs, defaultProcpinTuple = [MPIBindOpt.none, ], defaultKnemTuple = [False, ]):
        self.name = name
        self.runs = runs
        
        # default values
        self.procpinTuple = defaultProcpinTuple
        self.knemTuple = defaultKnemTuple
        
    def withProcpinOpts(self, procpinTuple):
        self.procpinTuple = procpinTuple 
        return self
    
    def withKnemOpts(self, knemTuple):
        self.knemTuple = knemTuple
