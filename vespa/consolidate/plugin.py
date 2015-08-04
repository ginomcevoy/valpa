import imp
import logging

class CustomMetricsReader(object):
    """ Loads a user-defined module that processes application-specific output.
    
    With this API, users of Vespa can add application metrics such as throughput
    and application time to the list of metrics captured during experiments.
    In order to be used, the user requires a read_output.py module in the 
    relevant application folder. For each experiment output, Vespa will call
     
    read_output.read_metrics(stdout, stderr, expDir, customFile=None)

    """ 
    
    def __init__(self, appParams, moduleName='read_output'):
        
        # find the module at the application path
        appConfigPath = appParams['app.config']
        fp, pathname, description = imp.find_module(moduleName, [appConfigPath,])
        
        # load the module, the function can be called on it
        return imp.load_module(moduleName, fp, pathname, description)
        
    def __enter__(self):
        return self
    
    def __exit__(self, exctype, excinst, exctb):
        if exctype == ImportError:
            logging.warn('User module not found for: ' + self.appName)
        if self.fp is not None and self.fp:
            self.fp.close()
