#!/bin/bash
#---------------------------------------------------------------
# Project         : VM monitoring
# File            : monitor-start-all.sh
# Author          : Giacomo Mc Evoy
# Created On      : Mar 13 09:38:09 2013  
# Modified by	  : Giacomo Mc Evoy (2013)
# Purpose         : Start monitoring of nodes remotely
#---------------------------------------------------------------

# Validate input
if [ $# -lt 1 ]; then
 	echo "Start monitoring of nodes remotely"
        echo "Usage: $0 <File with nodelist> [Monitor app (sysstat default)]"
        exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Files
NODES_FILE=$1

# Monitor app
if [ $# -gt 1 ]; then
	MONITOR=$2
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
  # SSH to node to call monitor script - disable prompt
  MONITOR_START=$LOCAL_DIR/${MONITOR}-start.sh
  ssh -o StrictHostKeyChecking=no $node $MONITOR_START &
done

sleep 0
