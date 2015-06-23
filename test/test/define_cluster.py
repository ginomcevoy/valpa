'''
Created on Oct 13, 2013

@author: giacomo
'''
import difflib
import unittest

from bean.cluster import Topology, Technology
from bean.enum import DiskOpt, NetworkOpt
from define.cluster import ClusterXMLGenerator, ValpaXMLGenerator
from test.test_abstract import ValpaAbstractTest

class VALPAXMLGeneratorTest(ValpaAbstractTest):
    
    def setUp(self):
        super(VALPAXMLGeneratorTest, self).setUp()
        self.valpaXMLGen = ValpaXMLGenerator(self.valpaXMLOpts, self.networkingOpts, self.repoOpts, 'resources/master.xml')
        
    def testMasterXML(self):
        valpaXML = self.valpaXMLGen.produceValpaXML()

        # compare with expected output
        expectedValpaXML = open('resources/valpa-expected.xml', 'r').read()
        self.assertMultiLineEqual(valpaXML, expectedValpaXML)
        
class ClusterXMLGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.valpaXML = open('resources/valpa-expected.xml', 'r').read()
        self.valpaPrefs = {'vm_prefix' : 'kvm-pbs',
                           'vm_pattern' : '&PREFIX&NODEINDEX-&VMINDEX',
                           'vm_mem_base' : '0',
                           'vm_mem_core' : '1024',
                           'vm_disk' : 'disk.img'}

    def testGenerateVhostScsi(self):
        self.expectedClusterXML = open('resources/cluster-expected-vhost-scsi.xml', 'r').read()
        
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.vhost, DiskOpt.scsi)

        clusterGen = ClusterXMLGenerator(self.valpaXML, self.valpaPrefs)
        clusterXML = clusterGen.produceClusterXML(topology, technology)

        self.assertMultiLineEqual(clusterXML, self.expectedClusterXML)

    def testGenerateVirtioVirtio(self):
        self.expectedClusterXML = open('resources/cluster-expected-virtio-virtio.xml', 'r').read()
        
        topology = Topology(48, 4)
        technology = Technology(NetworkOpt.virtio, DiskOpt.virtio)

        clusterGen = ClusterXMLGenerator(self.valpaXML, self.valpaPrefs)
        clusterXML = clusterGen.produceClusterXML(topology, technology)

        self.assertMultiLineEqual(clusterXML, self.expectedClusterXML)
        
    def assertMultiLineEqual(self, first, second, msg=None):
        '''
        Assert that two multi-line strings are equal.
        If they aren't, show a nice diff.
        '''
        self.assertTrue(isinstance(first, str),
                'First argument is not a string')
        self.assertTrue(isinstance(second, str),
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