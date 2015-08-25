""" Unit test for the plugin module for the NPB-FT benchmark """

import unittest
from unit.test_abstract import NPB_FT_AbstractTest
from pprint import pprint

class NPB_FT_PluginTest(NPB_FT_AbstractTest):

    def test_read_metrics(self):
        # given
        stdout = open('resources/apps/NPB-FT/ft.B.8.out')
        
        # when
        metrics = self.read_output.read_metrics(stdout, stderr=None, expDir=None)
        
        # then
        self.assertEqual(len(metrics), 4)
        self.assertEqual(metrics['initTime'], 0.834)
        self.assertEqual(metrics['appTime'], 13.57)
        self.assertEqual(metrics['mopsTotal'], 6782.29)
        self.assertEqual(metrics['mopsProc'], 847.79)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()