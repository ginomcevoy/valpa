'''
Created on Oct 30, 2013

Uses Vespa to instantiate a cluster based on DIST params
and default values

@author: giacomo
'''

import sys

from core.enum import PinningOpt  # @UnusedImport it IS used

from core.experiment import Application
from . import cluster
import bootstrap
from core.cluster import SetsTechnologyDefaults

def quickCluster(nc, cpv, idf, pstrat, withTorque, forReal):
    
    # create clusterRequest based on DIST tuple
    clusterRequest = cluster.createClusterRequest(nc, cpv, idf, pstrat)
    
    # Bootstrap Vespa
    bootstrap.doBootstrap(forReal)
    bootstrapper = bootstrap.getInstance()
    
    hwSpecs = bootstrapper.getHwSpecs()
    
    # Strategy to set default Technology values
    vespaPrefs = bootstrapper.getVespaPrefs()
    technologySetter = SetsTechnologyDefaults(vespaPrefs)
    
    # update unset technology parameters with defaults
    clusterRequest.technology = technologySetter.setDefaultsOn(clusterRequest.technology)
    
    if not clusterRequest.isConsistentWith(hwSpecs):
        # declared cluster is invalid
        print("ERROR: cluster invalid! ", clusterRequest)        
    else:
        # mock application: if withTorque, then use an application
        # that will configure the Torque server with the VMs as nodes, 
        # else ignore Torque and only instantiate VMs.  
        if withTorque:
            appInfo = Application('torque', 0)
        else:
            appInfo = Application('none', 0)
        
        # cluster managers: define and deploy 
        deploymentFactory = bootstrapper.getDeploymentFactory()
        clusterDefiner = deploymentFactory.createClusterDefiner()
        clusterDeployer = deploymentFactory.createClusterDeployer()
        
        # define and deploy cluster
        deploymentInfo = clusterDefiner.defineCluster(clusterRequest, 'quick', forReal)
        clusterDeployer.deploy(clusterRequest, deploymentInfo, appInfo)
    
if __name__ == "__main__":
    # verify input
    if len(sys.argv) < 5:
        raise ValueError("call: quickcluster <nc> <cpv> <idf> <ps> [withTorque=True] [forReal=True]")
    
    if len(sys.argv) > 5:
        withTorque = sys.argv[5] == "True"
    else:
        withTorque = True
        
    if len(sys.argv) > 6:
        forReal = sys.argv[6] == "True"
    else:
        forReal = True
         
    # read input
    nc = sys.argv[1]
    cpv = sys.argv[2]
    idf = sys.argv[3]
    pstrat = sys.argv[4]
    
    # call logic
    quickCluster(nc, cpv, idf, pstrat, withTorque, forReal)
