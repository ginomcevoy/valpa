'''
Created on Oct 13, 2013

@author: giacomo
'''
import unittest
from bean.cluster import Topology, Technology
from bean.enum import DiskOpt, NetworkOpt
from define.cluster import ClusterXMLGenerator

class ClusterXMLGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.valpaXML = open('resources/valpa-expected.xml', 'r').read()
        self.valpaPrefs = {'xml_master' : 'master.xml', 
                           'vm_prefix' : 'kvm-pbs',
                           'vm_pattern' : '&PREFIX&NODEINDEX-&VMINDEX',
                           'vm_mem_base' : '0',
                           'vm_mem_core' : '1024',
                           'xml_cluster_path' : 'vms'}

    def testGenerateVhostScsi(self):
        self.expectedClusterXML = open('resources/cluster-expected-vhost-scsi.xml', 'r').read()
        
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.vhost, DiskOpt.scsi)

        clusterGen = ClusterXMLGenerator(self.valpaXML, self.valpaPrefs)
        clusterXML = clusterGen.produceClusterXML(topology, technology)

        self.maxDiff = None
        self.failUnlessEqual(clusterXML, self.expectedClusterXML)

    def testGenerateVirtioVirtio(self):
        self.expectedClusterXML = open('resources/cluster-expected-virtio-virtio.xml', 'r').read()
        
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.virtio, DiskOpt.virtio)

        clusterGen = ClusterXMLGenerator(self.valpaXML, self.valpaPrefs)
        clusterXML = clusterGen.produceClusterXML(topology, technology)

        self.maxDiff = None
        self.failUnlessEqual(clusterXML, self.expectedClusterXML)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()