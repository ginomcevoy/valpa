'''
Created on Oct 13, 2013

@author: giacomo
'''
import unittest

from config import vespaconfig

class VespaConfigBase (unittest.TestCase):

    def setUp(self):
        self.expectedVespaPrefs = {'vm_disk' : 'disk.img',
                                   'vm_pernode' : '12', 
                                   'vm_prefix' : 'kvm-pbs',
                                   'vm_pattern' : '&PREFIX&NODESUFFIX-&VMSUFFIX',
                                   'vm_mem_base' : '0', 
                                   'vm_mem_core' : '1024', 
                                   'vm_mac_base' : '00:16:36:ff',
                                   'vm_xml_output' : '/tmp/vespa/xmls',
                                   'exec_config_template' : '../templates/execConfig.template',
                                   'exec_config_output' : '/tmp/vespa/execs',
                                   'general_verbose' : '1',
                                   'out_node_inventory': '/tmp/vespa-node-inventory',
                                   'out_vm_inventory': '/tmp/vespa-vm-inventory'
                                   }

        self.expectedXMLOpts = {'xml_disk_drivertype' : 'raw',
                                'xml_disk_dev' : 'vda'}
        
        self.networkingOpts = {'network_source' : 'external-bridge',
                               'net_name_bridge_use' : 'vespa-external-bridge',
                               'net_name_bridge_create' : 'vespa-libvirt-bridge',
                               'net_name_sriov' : 'vespa-sriov'}

    def testVespaConfig(self):
        vespaFile = 'resources/vespa.params'
        vespaCfg = vespaconfig.readVespaConfig(vespaFile)

        # vespaPrefs
        vespaPrefs = vespaCfg.getVespaPrefs()
        self.failIf(type(vespaPrefs) != type({}))
        self.maxDiff = None
        self.failUnlessEqual(vespaPrefs, self.expectedVespaPrefs)

        # vespaXMLOpts
        vespaXMLOpts = vespaCfg.getVespaXMLOpts()
        self.failIf(type(vespaXMLOpts) != type({}))
        self.failUnlessEqual(vespaXMLOpts, self.expectedXMLOpts)

if __name__ == '__main__':
    unittest.main()
