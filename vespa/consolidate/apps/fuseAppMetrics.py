# Fuses different CSV for application metrics into a single one

import sys, csv

def fuseCSVs(csvOutput, columnNames, csvFiles):

	# Get first file, read header and writer
	firstRow = ['config']
	with open(csvFiles[0], 'rb') as firstCSV:
		csvReader = csv.reader(firstCSV, delimiter=';', quotechar='|')
		header = csvReader.next()
		firstRow.extend(header)
		
	with open(csvOutput, 'wb') as csvfile:
		csvWriter = csv.writer(csvfile, delimiter=';',
	                            quotechar='|', quoting=csv.QUOTE_MINIMAL)

		# Write headers, add the CSV name
		csvWriter.writerow(firstRow)

		# Add each of the CSV files
		for csvFilename in csvFiles:
			with open(csvFilename, 'rb') as csvFile:
				csvReader = csv.reader(csvFile, delimiter=';', quotechar='|')

				# skip the header
				header = csvReader.next()

				# Name of the first entry
				paths = csvFilename.split('/')
				if columnNames == 'Config':
					title = paths[len(paths)-2]
				else:
					title = paths[len(paths)-3]
				for row in csvReader:
					rowValues = [title] # only the first here
					rowValues.extend(row)
					csvWriter.writerow(rowValues)


if __name__ == '__main__':

	# Output
	csvOutput = sys.argv[1]

	# Use config or dist name? (Config / Dist)
	columnNames = sys.argv[2]
	
	# Get csv files
	csvFiles = sys.argv[3:len(sys.argv)]
	fuseCSVs(csvOutput, columnNames, csvFiles)
