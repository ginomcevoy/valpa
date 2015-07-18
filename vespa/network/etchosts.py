'''
Created on Jun 26, 2015

@author: giacomo
'''

import sys
import socket

import bootstrap

class EtcHostsFileBuilder():
    '''
    Builds a file meant to replace any /etc/hosts file in Vespa. It includes
    an entry for the local node (127.0.0.1 localhost), and entries for each
    Vespa node and each possible VM. It can optionally include entries from an
    input file. 
    '''
    
    def __init__(self, physicalCluster, allVMDetails):
        '''
        @param physicalCluster: NodeCluster instance with IP addresses set
        @param allVMDetails: AllVMDetails instance with IP addresses set
        '''
        self.physicalCluster = physicalCluster
        self.allVMDetails = allVMDetails
        
    def buildFile(self, outputFilename, neighbor, inputFilename=None):
        self.initializeFile(outputFilename)
        if inputFilename is not None:
            self.appendInputLines(inputFilename)
            
        localHostnameAndIp = getLocalHostnameAndIp(neighbor)
        self.appendNodeEntries(localHostnameAndIp)
        self.appendVmEntries()
            
    def initializeFile(self, outputFilename):
        '''
        Creates a new file with a given filename (overwrites content). Adds
        an entry for localhost.
        '''
        self.outputFilename = outputFilename
        with open(self.outputFilename, 'w') as etcHostsFile:
            etcHostsFile.write('127.0.0.1\tlocalhost\n\n')
            
    def appendInputLines(self, inputFilename):
        '''
        When provided, append all lines in inputFile to the output.
        '''
        with open(self.outputFilename, 'a') as etcHostsFile:
            
            # write appropriate header
            etcHostsFile.write('# External input\n\n')
            
            with open(inputFilename, 'r') as inputFile:
                lines = inputFile.read()
                etcHostsFile.write(lines)
            
            etcHostsFile.write('\n')
            
    def appendNodeEntries(self, localHostnameAndIp):
        '''
        Append all lines corresponding to the Vespa physical cluster, 
        including the head node (assuming code is submit in the head node)
        @param localHostnameAndIp: (hostname, ip) tuple returned by
        getLocalHostnameAndIp function
        '''
        with open(self.outputFilename, 'a') as etcHostsFile:
            
            # write appropriate header
            etcHostsFile.write('# Vespa Physical Nodes\n\n')
            
            # write entry for head (local) node
            hostname = localHostnameAndIp[0]
            ipAddress = localHostnameAndIp[1]
            etcHostsFile.write(ipAddress + '\t' + hostname + '\n')
            
            # write each line
            for nodeName in self.physicalCluster.getNames():
                ipAddress = self.physicalCluster.getIpAddressOf(nodeName)
                etcHostsFile.write(ipAddress + '\t' + nodeName + '\n')
                
            etcHostsFile.write('\n')
            
    def appendVmEntries(self):
        '''
        Append all lines corresponding to the Vespa virtual cluster.
        '''
        with open(self.outputFilename, 'a') as etcHostsFile:
            
            # write appropriate header
            etcHostsFile.write('# Vespa VMs\n\n')
            
            # write each line
            vmNames = sorted(self.allVMDetails.getNames())
            for vmName in vmNames:
                ipAddress = self.allVMDetails.getIpAddressOf(vmName)
                etcHostsFile.write(ipAddress + '\t' + vmName + '\n')
            
def getLocalHostnameAndIp(neighbor):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((neighbor, 9))
    ipAddress = s.getsockname()[0]
    hostname = socket.gethostname()
    return (hostname, ipAddress)

if __name__ == '__main__':
    
    # Bootstrap Vespa with default config
    bootstrap.doBootstrap()
    bootstrapper = bootstrap.getInstance()
    physicalCluster = bootstrapper.getPhysicalCluster()
    allVMDetails = bootstrapper.getAllVMDetails()
    
    # verify input
    if len(sys.argv) < 2:
        raise ValueError("call: " + sys.argv[0] + " <outputFilename> [neighbor] [inputFile]")
    outputFilename = sys.argv[1]
    if len(sys.argv) > 2:
        neighbor = sys.argv[2]
    else:
        neighbor = physicalCluster.getNames()[0]
    if len(sys.argv) > 3:
        inputFilename = sys.argv[3]
    else:
        inputFilename = None
        
    # produce /etc/hosts file in indicated output
    builder = EtcHostsFileBuilder(physicalCluster, allVMDetails)
    builder.buildFile(outputFilename, neighbor, inputFilename)
    
