'''
Created on Oct 30, 2013

Uses Vespa to submit an application on a previously deployed cluster.

@author: giacomo
'''

import sys

from core.experiment import Application
from create import cluster
import bootstrap
from core.cluster import SetsTechnologyDefaults

def quickRun(appName, nc, cpv, idf, pstrat, forReal, args):
        
    # create clusterRequest based on DIST tuple
    # TODO push createCluster functionality to the core  
    clusterRequest = cluster.createClusterRequest(nc, cpv, idf, pstrat)
    
    # create application object
    appRequest = Application(appName, 1, args)
    
    # Bootstrap Vespa
    bootstrap.doBootstrap(forReal)
    bootstrapper = bootstrap.getInstance()
    
    # Strategy to set default Technology values
    vespaPrefs = bootstrapper.getVespaPrefs()
    technologySetter = SetsTechnologyDefaults(vespaPrefs)
    
    # update unset technology parameters with defaults
    clusterRequest.technology = technologySetter.setDefaultsOn(clusterRequest.technology)
    
    # need to execute application, get corresponding object
    deploymentFactory = bootstrapper.getDeploymentFactory()
    applicationExecutor = deploymentFactory.createApplicationExecutor()
    
    # define cluster to get deploymentInfo
    clusterDefiner = deploymentFactory.createClusterDefiner()
    deploymentInfo = clusterDefiner.defineCluster(clusterRequest, appName, False) # false means don't do anything with the cluster, just get the details 
    
    applicationExecutor.execute(clusterRequest, deploymentInfo, appRequest) 
    
if __name__ == "__main__":
    # verify input
    if len(sys.argv) < 6:
        raise ValueError("call: quickrun <appName> <nc> <cpv> <idf> <ps> [forReal=True] [app args...]")
    
    # app arguments
    args = ''
    if len(sys.argv) > 7:
        argsList = sys.argv[7:]
        for arg in argsList:
            args += arg + ' '
    
    # forReal    
    if len(sys.argv) > 6:
        forReal = sys.argv[6] == "True"
    else:
        forReal = True

    # read other input
    appName = sys.argv[1]
    nc = sys.argv[2]
    cpv = sys.argv[3]
    idf = sys.argv[4]
    pstrat = sys.argv[5]
    
    # call logic
    quickRun(appName, nc, cpv, idf, pstrat, forReal, args)
