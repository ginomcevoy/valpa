'''
Created on Aug 24, 2014

Interface between shell and Python for loading shell parameters
from main VALPA configuration. Uses the params.template to 
build a file for shell parameters, e.g. via source in params.sh. 
Outputs the filename of the created instance of the template. 

@author: giacomo
'''
from config import valpaconfig, hwconfig
from quik import FileLoader
import os
class ShellParameters:

    def loadValpaParams(self, valpaParamFile='../input/valpa.params', hwParamFile='../input/hardware.params'):
        
        # Read VALPA configuration file
        valpaConfig = valpaconfig.readValpaConfig(valpaParamFile)
        (valpaPrefs, valpaXMLOpts, runOpts, networkingOpts) = valpaConfig.getAll()
       
        # Read hardware specification
        hwInfo = hwconfig.getHardwareInfo(hwParamFile)
        (hwDict, nodeDict) = hwInfo.getHwAndNodeDicts()
                
        # Build a single dictionary of parameters
        self.allParams = dict(valpaPrefs)
        self.allParams.update(valpaXMLOpts)
        self.allParams.update(runOpts)
        self.allParams.update(hwDict)
        self.allParams.update(nodeDict)
        self.allParams.update(networkingOpts)
        
        self.loaded = True
    
    def createParamsFromTemplate(self, outputFilename='/tmp/valpa-shell-params'):
        if not self.loaded:
            # Error: return -1 to alert the calling shell script
            raise ValueError('loadValpaParams not called')
        
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
    shellParams.loadValpaParams() 
    shellParams.createParamsFromTemplate() 