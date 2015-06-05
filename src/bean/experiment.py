from bean.enum import MPIBindOpt

class Application:
	'''
	Describes the application that the user wants to deploy in a virtual cluster in
	order to create an experiment. The 'runs' argument specifies how many times
	the application should be executed in an experiment.
	'''

	def __init__(self, name, runs, args='', appTuning=None):
		self.name = name
		if appTuning is None:
			appTuning = AppTuning()
		self.appTuning = appTuning
		self.runs = runs
		self.options = []
		if args is None:
			args = ''
		self.args = args

	def __str__(self):
		return "name = " + self.name + " runs = " + str(self.runs) + " - " + str(self.appTuning)
		
class AppTuning:
	'''
	Describes parameters that tweak how the application is executed.
	Currently two options: 
	procpin - a MPIBindOpt option to specify process mappings to cores
	knem - True/False, indicates if the KNEM module should be used.   
	'''

	def __init__(self, procpin=False, knem=False):
		# compatibility: now supporting three options
		# True / BIND_CORE means --bind-to-core --bysocket
		# False / NONE means do nothing
		# BIND_SOCKET means --bind-to-socket --bysocket
		if procpin is True:
			procpin = MPIBindOpt.BIND_CORE
		if procpin is False:
			procpin = MPIBindOpt.NONE
		self.procpin = procpin
		self.knem = knem

	def __str__(self):
		return "procpin = " + str(self.procpin)

class Experiment:
	'''
	An experiment represents the instantiation of a virtual cluster, followed by
	one or more application runs. One experiment implies one virtual cluster and
	one application (potentially instantiated several in trials), but 
	multiple experiments may be undertaken concurrently (scenario with 
	concurrent applications). 
	'''

	def __init__(self, name, cluster, app, trials=1):
		self.name = name
		self.cluster = cluster
		self.app = app
		self.trials = trials
		
	def isConsistentWith(self, hwSpecs):
		return self.cluster.isConsistentWith(hwSpecs)

	def __str__(self):
		return "name = " + self.name + " trials = " + self.trials + "\n" + str(self.cluster) + "\n" + str(self.app)

class Scenario:
	'''
	A scenario is the most generic form of virtual cluster instantiation. 
	Represents one experiment, or multiple experiments run concurrently.
	'''
	
	def __init__(self, exps):
		self.exps = exps
		
	def getExperiment(self, i=0):
		return self.exps[i]
