#!/bin/bash

# Verify parameters
if [ $# -lt 2 ]; then
	echo "Execute experiments in an XML"
	echo "Usage: $0 <filename without .xml> <sleep time> [dir for xml]"
	echo ".xml suffix will be appended to name supplied"
	echo "Sleep time in seconds"
	echo "Default dir for experiment definition: $HOME/valpa-exps"
	exit 1
fi

# Read parameters
XML_NAME=$1
SLEEP_TIME=$2
if [ $# -gt 2 ]; then
	XML_PATH=$3
else
	XML_PATH=$HOME/valpa-exps

# Sleep, then call experiment script
sleep $SLEEP_TIME
./experiment.sh $XML_NAME $XML_PATH