#!/bin/bash 

# Processes monitoring output to txt files
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Verify parameters
if [ $# -lt 2 ]; then
	echo "Converts sysstat output of an execution to txt files " 
	echo "Usage: $0 <exec_dir> <nodes_file> [Monitor app (sysstat default)]"
	exit 1
fi

# Calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Input
EXEC_DIR=$1
NODES_FILE=$2

# Monitor app
if [ $# -gt 2 ]; then
  MONITOR=$3
else
  MONITOR='sysstat'
fi

# Monitor options
if [ $MONITOR != 'sysstat' -a $MONITOR != 'vmstat' ]; then
  >&2 echo "Monitor app: either 'sysstat' or 'vmstat'" 
  exit 1
fi

# Generate performance metrics - monitoring
for NODE in $(cat $NODES_FILE); do
  MONITOR_PROCESS=$LOCAL_DIR/$MONITOR-preprocess.sh
  $MONITOR_PROCESS $EXEC_DIR $NODE
done
