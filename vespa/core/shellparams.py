'''
Created on Aug 24, 2014

Interface between shell and Python for loading shell parameters
from main Vespa configuration. Uses the params.template to 
build a file for shell parameters, e.g. via source in params.sh. 
Outputs the filename of the created instance of the template. 

@author: giacomo
'''

import jinja2
import os

import bootstrap

class ShellParameters:
    
    def __init__(self, bootstrapper):
        
        # Need hwconfig dicts, valpaPrefs, networkingOpts, repoOpts
        # Build a single dictionary of parameters
        self.allParams = dict(bootstrapper.getVespaPrefs())
        self.allParams.update(bootstrapper.getNetworkingOpts())
        self.allParams.update(bootstrapper.getRepoOpts())
        
        hwSpecs = bootstrapper.getHwSpecs()
        self.allParams.update(hwSpecs)
        
        # setup jinja template
        templateLoader = jinja2.FileSystemLoader(searchpath="../templates")
        templateEnv = jinja2.Environment(loader=templateLoader, keep_trailing_newline=True)
        self.template = templateEnv.get_template('params.template')
        
    def createParamsFromTemplate(self, outputFilename='/tmp/vespa-shell-params'):
                
        # apply jinja substitution
        templateText = self.template.render(self.allParams)
        
        # Save to file
        if os.path.exists(outputFilename):
            os.remove(outputFilename)
        with open(outputFilename, 'w') as outputFile: 
            outputFile.write(templateText)
            outputFile.close()    
        
        # Echo the filename for shell script, also return it for test
        print(outputFilename)
        return outputFilename
        
if __name__ == '__main__':
    
    # Bootstrap Vespa with default config
    bootstrap.doBootstrap()
    bootstrapper = bootstrap.getInstance()
    
    shellParams = ShellParameters(bootstrapper)
    shellParams.createParamsFromTemplate()