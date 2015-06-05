#!/bin/bash
#---------------------------------------------------------------
# Project         : VM monitoring with PBS
# File            : monitor-start-pbs.sh
# Author          : Giacomo Mc Evoy
# Created On      : Mar 13 09:38:09 2013  
# Modified by	  : Giacomo Mc Evoy (2013)
# Purpose         : Start monitoring of VMs remotely
#---------------------------------------------------------------

# Validate input
if [ $# -lt 1 ]; then
 	echo "Start monitoring of VMs remotely from PBS file"
        echo "Usage: $0 <PBS node file> [Monitor app]"
        exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Files
PBS_NODEFILE=$1
NODES_FILE='/tmp/valpa-monitor-nodenames.txt'

# Call Python script to find nodes (unique names)
python $LOCAL_DIR/nodenames.py $PBS_NODEFILE $NODES_FILE

# Call remote monitoring
$LOCAL_DIR/monitor-start-all.sh $NODES_FILE $2
