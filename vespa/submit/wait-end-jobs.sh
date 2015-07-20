#!/bin/bash 

# Waits for the executing jobs to finish in the virtual cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
		echo "Waits for the executing jobs to finish in the virtual cluster"
        echo "Usage: $0 <app-name> <with-pbs>"
        exit 1
fi

APP_NAME=$1
USE_PBS=$2

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Do we use PBS?
if [ $USE_PBS == 'True' ]; then
	# Use PBS wait
	$LOCAL_DIR/pbs/wait-pbs-finish.sh
else 
	# Not implemented
	echo "**TODO** ERROR: Not using PBS, cannot wait reliably!"
	exit 1 
fi
