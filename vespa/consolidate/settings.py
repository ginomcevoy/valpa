# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013
# Reads datagen.params to obtain data generation preferences

import ConfigParser

class DataGenSettings:
	'''
	Reads datagen.params to produce dictionaries with options. One dictionary is
	the 'prefs' dictionary, with general settings. The other dictionaries represent
	each application, and are stored in a single (second) dictionary
	'''

	# Singleton variable
	settings = None

	def __init__(self, settingsFile):
		config = ConfigParser.RawConfigParser()
		config.read(settingsFile)
		
		self.apps = {} # app-specific sections are stored here
		
		for section in config.sections():
			if section == 'General':
				self.prefs = dict(config.items('General'))
			else:
				self.apps[section] = dict(config.items(section))

	def getPrefs(self):
		return self.prefs

	def getInfoForApp(self, appName):
		return self.apps[appName]
	
def getSettings(filename='../input/datagen.params'):
	'''
	Reads datagen settings file and instantiates DataGenSettings object
	'''
	if DataGenSettings.settings is None:
		DataGenSettings.settings = DataGenSettings(filename)
	return DataGenSettings.settings
