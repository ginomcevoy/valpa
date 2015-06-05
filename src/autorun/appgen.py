'''
Created on Sep 29, 2014

@author: giacomo
'''
from application import appgen
from bean.enum import MPIBindOpt

class AppRequestGenerator():
    '''
    Generates a list of ApplicationRequest objects according to a specification, 
    with a particular clusterRequest instance as context.
    '''
    
    def generateFor(self, appGenerationSpec, clusterRequest):
        appName = appGenerationSpec.name
        requestFactory = appgen.chooseRequestFactory(appName)
        return requestFactory.generateFor(appGenerationSpec, clusterRequest)
        
class ApplicationGenerationSpecification():
    
    def __init__(self, name, runs, defaultProcpinTuple = [MPIBindOpt.NONE, ], defaultKnemTuple = [False, ]):
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
