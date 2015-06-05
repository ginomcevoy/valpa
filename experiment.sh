#!/bin/bash

# Verify parameters
if [ $# -lt 1 ]; then
	echo "Execute experiments in an XML"
	echo "Usage: $0 <filename without .xml> [dir for xml]"
	echo ".xml suffix will be appended to name supplied"
	echo "Default dir for experiment definition: $HOME/valpa-exps"
	exit 1
fi

# Read parameters
XML_NAME=$1
if [ $# -gt 1 ]; then
	XML_PATH=$2
else
	XML_PATH=$HOME/valpa-exps
fi

# Experiment file 
XML_FILE=$XML_PATH/$XML_NAME.xml
OUTPUT_LOG=$HOME/valpa-logs/$XML_NAME.log

# Run experiment
cd src
nohup python3 experiments.py True $XML_FILE &> $OUTPUT_LOG &
echo "Output log at $OUTPUT_LOG"
