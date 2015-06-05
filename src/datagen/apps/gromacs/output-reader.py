import io, sys, csv

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
def metricsToCSV(outputFile, timeMetrics):

	numExp = len(timeMetrics['userTime'])

	userTimes = timeMetrics['userTime']
	systemTimes = timeMetrics['systemTime']
	ellapsedTimes = timeMetrics['ellapsedTime']

	with open(outputFile, 'wb') as csvfile:
		csvWriter = csv.writer(csvfile, delimiter=';',
	                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

		# Write headers
		csvWriter.writerow(['userTime', 'systemTime', 'ellapsedTime', 'appTime'])

		# Write each line, iterate over experiments
		for i in range(0, numExp):
			csvWriter.writerow([userTimes[i], systemTimes[i], ellapsedTimes[i], ellapsedTimes[i]])

if __name__ == '__main__':

	# Work times.txt file
	timePath = sys.argv[1]
	timeMetrics = analyzeTimes(timePath)

	# Work custom.out files
	#allPaths = sys.argv[3:len(sys.argv)]
	#appMetrics = gatherCustom(allPaths)

	# Build CSV
	outputFile = sys.argv[2]
	metricsToCSV(outputFile, timeMetrics)
