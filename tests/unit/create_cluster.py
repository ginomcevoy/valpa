'''
Created on Oct 13, 2013

@author: giacomo
'''
import unittest

from core.cluster import Topology, Technology
from core.enum import DiskOpt, NetworkOpt
from create.cluster import ClusterXMLGenerator, VespaXMLGenerator
from unit.test_abstract import VespaAbstractTest

class VespaXMLGeneratorTest(VespaAbstractTest):
    
    def setUp(self):
        VespaAbstractTest.setUp(self)
        self.vespaXMLGen = VespaXMLGenerator(self.vespaXMLOpts, self.networkingOpts, self.repoOpts, 'resources', 'master.xml')
        
    def testMasterXML(self):
        vespaXML = self.vespaXMLGen.produceVespaXML()

        # compare with expected output
        self.assertTextEqualsContent(vespaXML, 'resources/vespa-expected.xml')
        
class ClusterXMLGeneratorTest(VespaAbstractTest):

    def setUp(self):
        super(ClusterXMLGeneratorTest, self).setUp()
        vespaXML = open('resources/vespa-expected.xml', 'r').read()
        self.clusterGen = ClusterXMLGenerator(vespaXML, self.vespaPrefs, self.hwSpecs)

    def testGenerateVhostScsi(self):
        # given
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.vhost, DiskOpt.scsi)

        # when 
        clusterXML = self.clusterGen.produceClusterXML(topology, technology)

        # then
        expectedClusterXML = 'resources/cluster-expected-vhost-scsi.xml'
        self.assertTextEqualsContent(clusterXML, expectedClusterXML)

    def testGenerateVirtioVirtio(self):
        # given        
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.virtio, DiskOpt.virtio)

        # when 
        clusterXML = self.clusterGen.produceClusterXML(topology, technology)

        # then
        expectedClusterXML = 'resources/cluster-expected-virtio-virtio.xml'
        self.assertTextEqualsContent(clusterXML, expectedClusterXML)
        
    def testGenerateInfiniband(self):
        # given
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.virtio, DiskOpt.virtio, infinibandFlag=True)
         
        # when
        clusterXML = self.clusterGen.produceClusterXML(topology, technology)
        
        # then
        expectedClusterXML = 'resources/cluster-expected-infiniband.xml'
        self.assertTextEqualsContent(clusterXML, expectedClusterXML)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
