'''
Created on Apr 29, 2014

@author: giacomo
'''
import subprocess

class PBSUpdater:
    '''
    Updates the node list at the PBS head'''
    
    def __init__(self, runOpts, forReal):
        self.tempFile = runOpts['pbs_temp_nodelist']
        self.pbsServer = runOpts['pbs_server']
        self.forReal = forReal
        
    def updatePBS(self, deployedVMs, clusterInfo):
        # create the file to update in a separate location
        filename = self.createFile(deployedVMs, clusterInfo)
        
        # call script that will use administrative privileges for update
        updateCall = ['/bin/bash', 'submit/pbs/update-pbs.sh', filename, self.pbsServer]
        if self.forReal:
            print('updating pbs')
            subprocess.call(updateCall)
        else:
            print(updateCall)
            print(open(filename, 'r').read())
        
    def createFile(self, deployedVMs, clusterInfo):
        '''
        Creates the nodes file for PBS. Temporary location is given by vespa.params,
        default is /tmp/pbs-nodes
        Format:
        node1 np=#
        node2 np=#
        '''
        # data
        cpv = clusterInfo.topology.cpv
        vmNames = sorted(deployedVMs.getNames())
        
        # start clean file
        nodesFile = open(self.tempFile, 'w')

        # write output
        text = ''
        for vm in vmNames:
            text = text + vm + ' np=' + str(cpv) + '\n' 
        nodesFile.write(text)
        nodesFile.close()
        
        return self.tempFile   
