'''
Created on Sep 29, 2014

Applications requiring special parameters should be registered here,
by subclassing AppRequestAbstractFactory

@author: giacomo
'''
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