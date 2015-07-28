""" Unit tests for the core.config_app module. """

import unittest

from core import config_app

class ApplicationConfigTest(unittest.TestCase):
    """ Unit tests for ApplicationConfig class. """ 

    def setUp(self):
        self.appFolder = 'resources/apps'
        self.paramFile = 'application.config'
        
    def testAppConfig(self):
        # when
        print ('Expected warning: Bad application.config for: invalid')
        appConfig = config_app.getAppConfig(self.appFolder, self.paramFile)
        
        # then cavity3D and parpac are valid applications
        self.assertTrue('cavity3D' in appConfig.registered)
        self.assertTrue('parpac' in appConfig.registered)
        
        # then empty is not, no config file
        self.assertFalse('empty' in appConfig.registered)
        
        # then invalid is not, config file not adequate
        self.assertFalse('invalid' in appConfig.registered) 
        
        # Parpac is a Torque application, cavity3D is not
        self.assertTrue('parpac' in appConfig.torque)
        self.assertFalse('cavity3D' in appConfig.torque)
        self.assertFalse('invalid' in appConfig.torque)
        self.assertFalse('empty' in appConfig.torque)
        
        # validate content for Parpac - app.executable=PARPACBench
        parpacInfo = appConfig.appInfo['parpac']
        self.assertTrue('app.executable' in parpacInfo.keys())
        self.assertEquals('PARPACBench', parpacInfo['app.executable'])
        
        # validate content for Parpac - exec.outputrename=custom.out
        parpacInfo = appConfig.appInfo['parpac']
        self.assertTrue('exec.outputrename' in parpacInfo.keys())
        self.assertEquals('custom.out', parpacInfo['exec.outputrename'])
        
        # validate content for Parpac 
        # consolidate.default=/home/giacomo2/experiments/arriving/parpac
        parpacInfo = appConfig.appInfo['parpac']
        self.assertTrue('consolidate.default' in parpacInfo.keys())
        self.assertEquals('/home/giacomo2/experiments/arriving/parpac', 
                          parpacInfo['consolidate.default'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testAppConfig']
    unittest.main()