'''
Created on Oct 16, 2013

@author: giacomo
'''
from create.runner import ExperimentSetRunner
import sys
import bootstrap

if __name__ == "__main__":
    # verify input
    if len(sys.argv) < 3:
        raise ValueError("call: main <forReal> <experiment xml>")
    forReal = sys.argv[1] == "True" 
    experimentXML = sys.argv[2]
    
    # Bootstrap Vespa with default config
    bootstrap.doBootstrap(forReal)
    bootstrapper = bootstrap.getInstance()
    
    # execute all experiments in xml
    expSetRunner = bootstrapper.getExperimentSetRunner() 
    expSetRunner.readAndExecute(experimentXML)
