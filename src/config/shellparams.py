'''
Created on Aug 24, 2014

Interface between shell and Python for loading shell parameters
from main VESPA configuration. Uses the params.template to 
build a file for shell parameters, e.g. via source in params.sh. 
Outputs the filename of the created instance of the template. 

@author: giacomo
'''
from config import vespaconfig, hwconfig
from quik import FileLoader
import os
class ShellParameters:

    def loadVespaParams(self, vespaParamFile='../input/vespa.params', hwParamFile='../input/hardware.params'):
        
        # Read VESPA configuration file
        vespaConfig = vespaconfig.readVespaConfig(vespaParamFile)
        (vespaPrefs, vespaXMLOpts, runOpts, networkingOpts) = vespaConfig.getAll()
       
        # Read hardware specification
        hwInfo = hwconfig.getHardwareInfo(hwParamFile)
        (hwDict, nodeDict) = hwInfo.getHwAndNodeDicts()
                
        # Build a single dictionary of parameters
        self.allParams = dict(vespaPrefs)
        self.allParams.update(vespaXMLOpts)
        self.allParams.update(runOpts)
        self.allParams.update(hwDict)
        self.allParams.update(nodeDict)
        self.allParams.update(networkingOpts)
        
        self.loaded = True
    
    def createParamsFromTemplate(self, outputFilename='/tmp/vespa-shell-params'):
        if not self.loaded:
            # Error: return -1 to alert the calling shell script
            raise ValueError('loadVespaParams not called')
        
        # Create instance of the template with parameters
        loader = FileLoader('../templates')
        template = loader.load_template('params.template')
        templateText = template.render(self.allParams, loader=loader)
        
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
    shellParams = ShellParameters()
    
    # call with default values
    shellParams.loadVespaParams() 
    shellParams.createParamsFromTemplate() 