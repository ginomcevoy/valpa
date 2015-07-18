import io, sys, csv
import xml.etree.ElementTree as ET

# Reads std.out file for the cavity3d benchmark. 
# Outputs [Throughput]
def readStandardFile(stdPath):
	'''Reads std.out file for the cavity3d benchmark. 
	   Outputs [Throughput]'''

	# Read whole text
	stdText = open(stdPath, 'r').read()

 	# Look for line with throughput
 	appTimeIndex = stdText.find('iterations')
 	hasInfo = stdText[appTimeIndex:len(stdText)]
 	splits = hasInfo.split(':')

 	# print (splits)

 	# throughput is in the first line
 	throughput = splits[1].split('Mega')[0].strip()
	throughput = float(throughput)

 	output = {'throughput':throughput}
 	return output

# Reads custom.out file for the cavity3d benchmark.
# Outputs [appTime] 
def readCustomFile(customPath):
	'''Reads custom.out file for the cavity benchmark. 
	   Outputs [appTime]'''

  	# Open as an XML file
 	tree = ET.parse(customPath)
	root = tree.getroot()

	# get iteration (cycle) count
	iterationsNode = root.find('NumIterations')
	iterations = int(iterationsNode.text)

	# get mean time per cycle
	timeCycleNode = root.find('Time_per_cycle')
	meanTimeNode = timeCycleNode.find('Mean')
	meanTime = float(meanTimeNode.text)

	# appTime is mean time * cycles
  	appTime = meanTime * iterations	
	appTime = appTime.__format__('.2f')

 	output = {'appTime':appTime}
 	return output

# Reads all std.out and custom.out files for the cavity3d benchmark
# Generates a dictionary of 
# Outputs appTime, throughput
def gatherCustom(allPaths):
	'''Reads all std.out and custom.out files for the cavity3d benchmark
	   Generates a dictionary of vectors appTime, throughput'''
	
	# Build output
	appTime = []
	throughput = []

	# Iterate over paths and call customReader
	for path in allPaths:
 		# std.out contains the throughput
		stdFilepath = path + '/std.out'
		stdMetrics = readStandardFile(stdFilepath)

		# custom.out contains the appTime
		customFilepath = path + '/custom.out'
		customMetrics = readCustomFile(customFilepath)

		appTime.append(customMetrics['appTime'])
		throughput.append(stdMetrics['throughput'])

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
