import imp

class CustomReaderLoader(object):
    """ Loads a user-defined module that processes application-specific output.
    
    With this API, users of Vespa can add application metrics such as throughput
    and application time to the list of metrics captured during experiments.
    In order to be used, the user requires a read_output.py module in the 
    relevant application folder. For each experiment output, Vespa will call
     
    read_output.read_metrics(stdout, stderr, expDir, customFile=None)
    
    The output should be a dictionary of numbers. An OrderedDict can be used
    to maintain the order of the metrics.

    """ 
    
    def __init__(self, appParams, moduleName='read_output'):
        self.appConfigPath = appParams['app.config']
        self.moduleName = moduleName
        self.fp = None
        
    def __enter__(self):
        return self
    
    def loadModule(self):
        # find the module at the application path
        self.fp, pathname, description = imp.find_module(self.moduleName, [self.appConfigPath,])
        
        # load the module, the function can be called on it
        module = imp.load_module(self.moduleName, self.fp, pathname, description)
        self.loaded = True
        return module
    
    def __exit__(self, exctype, excinst, exctb):
        if exctype == ImportError:
            self.loaded = False
        if self.fp is not None and self.fp:
            self.fp.close()
            
        return True
