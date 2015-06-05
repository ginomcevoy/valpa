#!/bin/bash
#---------------------------------------------------------------
# Project         : VM monitoring
# File            : monitor-stop-pbs.sh
# Author          : Giacomo Mc Evoy
# Created On      : Mar 13 09:38:09 2013  
# Modified by	  : Giacomo Mc Evoy (2013)
# Purpose         : Stop monitoring of VMs after monitor-start-pbs.sh
#---------------------------------------------------------------

# Validate input
if [ $# -lt 2 ]; then
  echo "Stop monitoring of VMs after monitor-start-pbs.sh"
  echo "Usage: $0 <PBS_NODEFILE> <OUTPUT_DIR> [Monitor app]"
  exit 0
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Files
PBS_NODEFILE=$1
NODES_FILE='/tmp/nodenames.txt'
OUTPUT_DIR=$2

# Call Python script to find nodes
python $LOCAL_DIR/nodenames.py $PBS_NODEFILE $NODES_FILE

# Call stop monitoring
$LOCAL_DIR/monitor-stop-all.sh $NODES_FILE $OUTPUT_DIR $3
