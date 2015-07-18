'''
Created on Oct 13, 2013

@author: giacomo
'''
import difflib
import unittest

from core.cluster import Topology, Technology
from core.enum import DiskOpt, NetworkOpt
from define.cluster import ClusterXMLGenerator, VespaXMLGenerator
from unit.test_abstract import VespaAbstractTest

class VespaXMLGeneratorTest(VespaAbstractTest):
    
    def setUp(self):
        super(VespaXMLGeneratorTest, self).setUp()
        self.vespaXMLGen = VespaXMLGenerator(self.vespaXMLOpts, self.networkingOpts, self.repoOpts, 'resources', 'master.xml')
        
    def testMasterXML(self):
        vespaXML = self.vespaXMLGen.produceVespaXML()

        # compare with expected output
        self.assertTextEqualsContent(vespaXML, 'resources/vespa-expected.xml')
        
class ClusterXMLGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.vespaXML = open('resources/vespa-expected.xml', 'r').read()
        self.vespaPrefs = {'vm_prefix' : 'kvm-pbs',
                           'vm_pattern' : '&PREFIX&NODEINDEX-&VMINDEX',
                           'vm_mem_base' : '0',
                           'vm_mem_core' : '1024',
                           'vm_disk' : 'disk.img'}

    def testGenerateVhostScsi(self):
        self.expectedClusterXML = open('resources/cluster-expected-vhost-scsi.xml', 'r').read()
        
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.vhost, DiskOpt.scsi)

        clusterGen = ClusterXMLGenerator(self.vespaXML, self.vespaPrefs)
        clusterXML = clusterGen.produceClusterXML(topology, technology)

        self.assertMultiLineEqual(clusterXML, self.expectedClusterXML)

    def testGenerateVirtioVirtio(self):
        self.expectedClusterXML = open('resources/cluster-expected-virtio-virtio.xml', 'r').read()
        
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.virtio, DiskOpt.virtio)

        clusterGen = ClusterXMLGenerator(self.vespaXML, self.vespaPrefs)
        clusterXML = clusterGen.produceClusterXML(topology, technology)

        self.assertMultiLineEqual(clusterXML, self.expectedClusterXML)
        
    def assertMultiLineEqual(self, first, second, msg=None):
        '''
        Assert that two multi-line strings are equal.
        If they aren't, show a nice diff.
        '''
        isStringFirst = isinstance(first, str) or isinstance(first, unicode)
        isStringSecond = isinstance(second, str) or isinstance(second, unicode)
        self.assertTrue(isStringFirst,
                'First argument is not a string')
        self.assertTrue(isStringSecond,
                'Second argument is not a string')

        if first != second:
            message = ''.join(difflib.ndiff(first.splitlines(True),
                                                second.splitlines(True)))
            if msg:
                message += " : " + msg
            self.fail("Multi-line strings are unequal:\n" + message)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
