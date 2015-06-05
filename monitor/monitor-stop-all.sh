#!/bin/bash
#---------------------------------------------------------------
# Project         : VM monitoring
# File            : monitor-stop-all.sh
# Author          : Giacomo Mc Evoy
# Created On      : Mar 13 09:38:09 2013  
# Modified by	  : Giacomo Mc Evoy (2013)
# Purpose         : Stop monitoring of nodes after monitor-start-all.sh
#---------------------------------------------------------------

# Validate input
if [ $# -lt 2 ]; then
  echo "Stop monitoring of nodes after monitor-start-all.sh"
  echo "Usage: $0 <NODE_LIST_FILE> <OUTPUT_DIR> [Monitor app (sysstat default)]"
  exit 0 
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Files
NODES_FILE=$1
OUTPUT_DIR=$2

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

# Iterate over nodes
for node in $(cat $NODES_FILE); do
  # SSH to node to call monitor script
  MONITOR_STOP=$LOCAL_DIR/${MONITOR}-stop.sh
  ssh -o StrictHostKeyChecking=no $node $MONITOR_STOP $OUTPUT_DIR
done
