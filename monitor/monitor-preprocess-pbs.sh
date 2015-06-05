#!/bin/bash

# Converts sysstat output to txt files (less space)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Verify parameters
if [ $# -lt  2 ]; then
	echo "Converts sysstat output to txt files " 
	echo "Usage: $0 <exec_dir> <pbsfile> [Monitor app]"
	exit 1
fi

# Calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Input
EXEC_DIR=$1
PBS_FILE=$2
CONFIG_DIR="$EXEC_DIR/.."

# Work the pbsprocs file
python $LOCAL_DIR/nodenames.py $PBS_FILE $CONFIG_DIR/pbsnodes.txt

# Call all nodes
$LOCAL_DIR/monitor-preprocess-all.sh $EXEC_DIR $CONFIG_DIR/pbsnodes.txt $3