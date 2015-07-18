import io, sys, csv

# Reads std.out file for the NPB-EP benchmark. 
# Outputs AppTime, Throughput, Throughput per Process
def readCustomFile(customPath):
	'''Reads std.out file for the NPB-EP benchmark. 
	   Outputs AppTime, Throughput, Throughput per Process'''

	# Read whole text
	customText = open(customPath, 'r').read()
	#print (customText)

 	# Look for line with AppTime
 	appTimeIndex = customText.find('Time in seconds')
 	hasInfo = customText[appTimeIndex:len(customText)]
 	splits = hasInfo.split('=')

 	#print (splits)

 	# AppTime is in the first line
 	appTime = splits[1].split('\n')[0].strip()
 	appTime = float(appTime)

 	# throughput is in the fourth line (third block)
 	throughput = splits[4].split('\n')[0].strip()
	throughput = float(throughput)

 	# thProc (throughput per processor) is in the fifth line
 	thProc = splits[5].split('\n')[0].strip()
 	thProc = float(thProc)
 	
 	output = {'appTime':appTime, 'throughput':throughput, 'thProc':thProc}
 	return output

# Reads all custom.out files for the ParPac benchmark
# Generates a dictionary of 
# Outputs AppTime, FluidRate, FloatRate
def gatherCustom(allPaths):
	'''Reads all std.out files for the NPB-EP benchmark.
	   Generates a dictionary of vectors AppTime, Throughput, Throughput per Process'''
	
	# Build output
	appTime = []
	throughput = []
	thProc = []

	# Iterate over paths and call customReader
	for path in allPaths:
		customFilepath = path + '/std.out'
		appMetrics = readCustomFile(customFilepath)
		appTime.append(appMetrics['appTime'])
		throughput.append(appMetrics['throughput'])
		thProc.append(appMetrics['thProc'])

	metrics = {'appTime':appTime, 'throughput':throughput, 'thProc':thProc}
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
	thProcs = appMetrics['thProc']

	with open(outputFile, 'wb') as csvfile:
		csvWriter = csv.writer(csvfile, delimiter=';',
	                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

		# Write headers
		csvWriter.writerow(['userTime', 'systemTime', 'ellapsedTime', 'appTime', 'throughput', 'thProc'])

		# Write each line, iterate over experiments
		for i in range(0, numExp1):
			csvWriter.writerow([userTimes[i], systemTimes[i], ellapsedTimes[i], appTimes[i], throughputs[i], thProcs[i]])

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
