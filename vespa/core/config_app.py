""" This module manages data about applications registered with Vespa.

"""

import os
import ConfigParser
from ConfigParser import ParsingError
import warnings

class ApplicationConfig(object):
    """Reads and holds information about the applications registered with Vespa. 
    
    The list of applications is obtained by scanning the application directory
    for subfolders containing a key file. The application name, as recognized by
    Vespa, is given by the name of the subfolder. This name can be used to define
    experiments.
    """
    
    # Singleton for ApplicationConfig
    instance = None

    def __init__(self, appFolder, paramFile):
        self.registered = [] # names of all applications 
        self.torque = [] # names of Torque-based applications
        self.appInfo = {} # dictionary of application info (dictionaries)
        
        self.appFolder = appFolder
        self.paramFile = paramFile
        
        self.__scanFolder__()
        self.__readApps__()
        
    def __scanFolder__(self):
        possibleApplications = os.listdir(self.appFolder)
        for possibleApp in possibleApplications:
            subFolder = os.path.join(self.appFolder, possibleApp)
            if (not os.path.isdir(subFolder) or 
                not self.paramFile in os.listdir(subFolder)):
                continue
            # here we have a valid application, assuming file has data
            # this assumption gets tested in __readApps__ 
            self.registered.append(possibleApp)
        
    def __readApps__(self):
        # Read each parameter file and build the appInfo dictionary
        for app in self.registered:
            self.__readAppInfo__(app)
            
        # If a registered application did not have a valid config file,
        # it will not be added to appInfo, remove it from registered
        self.registered = [app for app in self.registered if app in self.appInfo.keys()]
        
        # add Torque-based apps to the torque tuple
        self.torque = [app for app in self.registered if self.__isTorque__(app)]
        
    def __readAppInfo__(self, appName):
        # It is expected that the application folder exists
        appFolder = os.path.join(self.appFolder, appName)
        assert self.paramFile in os.listdir(appFolder)
        appFile = os.path.join(appFolder, self.paramFile)
        
        # Parse the config file: [Application] and [Execution] are required
        parser = ConfigParser.RawConfigParser()
        try:
            parser.read(appFile)
        
            application = dict(parser.items('Application'))
            execution = dict(parser.items('Execution'))
            self.appInfo[appName] = application
            self.appInfo[appName].update(execution)
             
            # [Consolidate] is optional but should be present for correct consolidation            
            if 'Consolidate' in parser.sections():
                consolidate = dict(parser.items('Consolidate'))
                self.appInfo[appName].update(consolidate)
                
        except ParsingError:
            # Parser could not read the file, do not consider this app
            warnings.warn('Bad application.config for: ' + appName)
            if appName in self.appInfo.keys():
                del self.appInfo[appName]
    
    def __isTorque__(self, appName):
        return self.appInfo[appName]['exec.manager'] == 'Torque'
            
    
def getAppConfig(appFolder='../apps', paramFile='application.config'):
    """Initializes a Singleton instance for ApplicationConfig."""
    
    if ApplicationConfig.instance is None:
        ApplicationConfig.instance = ApplicationConfig(appFolder, paramFile)
    return ApplicationConfig.instance
    
def isTorqueBased(appRequest):
    """ Return True iff the application is configured for Torque. """
    
    appConfig = getAppConfig() # should have been initialized before
    return appRequest.name in appConfig.torque
    
    