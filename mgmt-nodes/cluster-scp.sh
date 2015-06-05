#!/bin/bash 
# Copy one or more files from source to each node in the physical cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -ne 2 ]; then
	echo "Copy one or more files from source to each node in the physical cluster."
	echo "Usage: $0 <source> <dist>"
	echo "<source> must be a local file/dir, <dist> is the remote dir"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh

# Call cluster-command
$LOCAL_DIR/cluster-command.sh "scp -r ${1} #:${2}"