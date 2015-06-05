#!/bin/bash

# Executes a PBS script, adds some execution information
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Verify parameters
if [ $# -lt 2 ]; then
	echo "Executes a PBS script, adds some execution information"
	echo "Usage: $0 <file for execution configuration> <execution number>"
	exit 1
fi

# Read parameters
RUN_CONFIG=$1
EXEC_TIMES=$2

# Load execution configiration
source $RUN_CONFIG

# Replace execution parameters in PBS script
RUN_CONFIG=$(echo $RUN_CONFIG | sed -e "s/\\//\\\\\//g")
sed -i -e "s/RUN_CONFIG/$RUN_CONFIG/g"\
 -e "s/EXEC_TIMES/$EXEC_TIMES/g" ${PBS_FILE}

 # Call PBS
qsub $PBS_FILE
#bash $PBS_FILE
