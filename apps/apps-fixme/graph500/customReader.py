import io, sys, csv

# Reads custom.out file for the ParPac benchmark
# Outputs AppTime, FluidRate, FloatRate
def readCustomFile(customPath):
	'''Reads std.out file for the ParPac benchmark. 
	   Outputs AppTime, FluidRate, FloatRate'''	
	
	# Read whole text
	customText = open(customPath, 'r').read()
	
	# Look for number of searches
	# NBFS:                           64
	nbfsIndex = customText.find('NBFS')
	hasInfo = customText[nbfsIndex:len(customText)]
	splits = hasInfo.split(':')	
	nbfs = splits[1].split('\n')[0]
	nbfs = int(nbfs)

	# graph_generation: line after NBFS
	graph_generation = splits[2].split('\n')[0]
	graph_generation = float(graph_generation)

	# construction_time: 2 lines below graph_generation
	construction_time = splits[4].split('\n')[0]
	construction_time = float(construction_time)

	# Look for line with meanTime (mean time of a search)
	# mean_time:                      0.175195
	meanTimeIndex = customText.find('mean_time')
	hasInfo = customText[meanTimeIndex:len(customText)]
	splits = hasInfo.split(':')	
	meanTime = splits[1].split('\n')[0]#.split(' ')[1]
	meanTime = float(meanTime)
	
	# Look for line with throughput
	# harmonic_mean_TEPS: 
	harmonicMeanIndex = customText.find('harmonic_mean_TEPS')
	hasInfo = customText[harmonicMeanIndex:len(customText)]
	splits = hasInfo.split(':')	
	harmonicMean = splits[1].split('\n')[0]
	harmonicMean = float(harmonicMean)
	
	# Look for line with validationTime (mean time of a validation)
	# mean_validate:                     
	validationTimeIndex = customText.find('mean_validate')
	hasInfo = customText[validationTimeIndex:len(customText)]
	splits = hasInfo.split(':')	
	validationTime = splits[1].split('\n')[0]
	validationTime = float(validationTime)

	# appTime is given by generation + construction + times x (search + validation)
	appTime = graph_generation + construction_time + nbfs * (meanTime + validationTime)
	
	output = {'appTime':appTime, 'throughput':harmonicMean}
	return output

# Reads all custom.out files for the ParPac benchmark
# Generates a dictionary of 
# Outputs AppTime, FluidRate, FloatRate
def gatherCustom(allPaths):
	'''Reads all custom.out files for the ParPac benchmark.
	   Generates a dictionary of vectors AppTime, FluidRate, FloatRate'''
	
	# Build output
	appTime = []
	throughput = []
	
	# Iterate over paths and call customReader
	for path in allPaths:
		customPath = path + '/std.out'
		appMetrics = readCustomFile(customPath)
		appTime.append(appMetrics['appTime'])
		throughput.append(appMetrics['throughput'])
		
	metrics = {'appTime':appTime, 'throughput':throughput}
	return metrics

def analyzeTimes(timePath):
	'''Generates a dictionary of vectors for the times.txt
	   Includes User, System and Ellapsed'''

	# Build output
	userTime = []
	systemTime = []
	ellapsedTime = []

	# Read whole text
	timesText = open(timePath, 'r').read()

	# Split for each experiment
	experiments = timesText.split('mpirun')
	experiments = experiments[1:len(experiments)]

	for exp in experiments:
		splits = exp.split('\n')
		numbers = splits[2]
		numbers = numbers.split('\t')
		userTime.append(numbers[0])
		systemTime.append(numbers[1])
		ellapsedTime.append(numbers[2])

	metrics = {'userTime':userTime, 'systemTime':systemTime, 'ellapsedTime':ellapsedTime}
	return metrics

# Generates a CSV file with the data from custom.out and times.txt
# for the Parpac Benchmark
def metricsToCSV(outputFile, timeMetrics, appMetrics):

	# Verify integrity
	numExp1 = len(timeMetrics['userTime'])
	numExp2 = len(appMetrics['appTime'])

	if numExp1 != numExp2:
		raise ValueError("Experiment numbers don't match:", outputFile)

	userTimes = timeMetrics['userTime']
	systemTimes = timeMetrics['systemTime']
	ellapsedTimes = timeMetrics['ellapsedTime']
	appTimes = appMetrics['appTime']
	throughputs = appMetrics['throughput']
	
	with open(outputFile, 'wb') as csvfile:
		csvWriter = csv.writer(csvfile, delimiter=';',
	                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

		# Write headers
		csvWriter.writerow(['userTime', 'systemTime', 'ellapsedTime', 'appTime', 'throughput'])

		# Write each line, iterate over experiments
		for i in range(0, numExp1):
			csvWriter.writerow([userTimes[i], systemTimes[i], ellapsedTimes[i], appTimes[i], throughputs[i]])

if __name__ == '__main__':

	# Work times.txt file
	timePath = sys.argv[1]
	timeMetrics = analyzeTimes(timePath)

	# Work custom.out files
	allPaths = sys.argv[3:len(sys.argv)]
	appMetrics = gatherCustom(allPaths)

	# Build CSV
	outputFile = sys.argv[2]
	metricsToCSV(outputFile, timeMetrics, appMetrics)

# if __name__ == '__main__':
# 	customPath = sys.argv[1]
# 	readCustomFile(customPath)
