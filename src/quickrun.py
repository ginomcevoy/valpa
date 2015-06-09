'''
Created on Oct 30, 2013

Uses VALPA to run an application on a previously deployed cluster.

@author: giacomo
'''

import sys
from bean.enum import PinningOpt  # @UnusedImport it IS used
from bean.experiment import Application
import quickcluster
from start import bootstrap

def quickRun(appName, nc, cpv, idf, pstrat, forReal, args):
        
    # create clusterRequest based on DIST tuple
    clusterRequest = quickcluster.createClusterRequest(nc, cpv, idf, pstrat)
    
    # create application object
    appRequest = Application(appName, 1, args)
    
    # Bootstrap VALPA
    bootstrap.doBootstrap(forReal)
    bootstrapper = bootstrap.getInstance()
    
    # need to execute application, get corresponding object
    clusterFactory = bootstrapper.getClusterFactory()
    clusterExecutor = clusterFactory.createClusterExecutor()
    
    # define cluster to get deploymentInfo
    clusterDefiner = clusterFactory.createClusterDefiner()
    deploymentInfo = clusterDefiner.defineCluster(clusterRequest, appName, False) # false means don't do anything with the cluster, just get the details 
    
    clusterExecutor.prepareAndExecute(clusterRequest, deploymentInfo, appRequest) 
    
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
