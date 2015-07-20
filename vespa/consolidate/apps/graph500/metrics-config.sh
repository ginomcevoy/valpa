#!/bin/bash

# app-metrics.sh
# Creates metrics-app.csv from times.txt and custom.out 
# for all executions of a single cluster configuration
# Works on the Parpac Benchmark
# Created by: Giacomo Mc Evoy
# LNCC 2013

# Verify arguments
if [ $# -lt 2 ]; then
	echo "Creates metrics-app.csv from times.txt and custom.out"
	echo "Usage #0 <config dir> <output_path> [output_file]"
	exit 1
fi

# Calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Read input
CONFIG_DIR=$1
OUTPUT_PATH=$2

if [ $# -ge 3 ]; then
	OUTPUT_FILE=$3
else
	OUTPUT_FILE='metrics-app.csv'
fi
OUTPUT_FILE=$OUTPUT_PATH/$OUTPUT_FILE

# Get execution folders
EXEC_DIRS=$(ls -d1 $CONFIG_DIR/*/)

# Call python script to generate CSV files
python $LOCAL_DIR/customReader.py $CONFIG_DIR/times.txt $OUTPUT_FILE $EXEC_DIRS
status=$?
if [ $status -ne 0 ]; then
    echo "Faulty data for config $CONFIG_DIR"
fi
