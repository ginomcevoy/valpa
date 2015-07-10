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
VESPA_DIR=$LOCAL_DIR/..

# Import params
source $VESPA_DIR/params.sh

# Load node inventory 
VESPA_INVENTORY=$($VESPA_DIR/util/nodes-inventory.sh $NODE_L)

# Use ansible copy, use 1 thread
ansible all -f 1 -i $VESPA_INVENTORY -m copy -a "src=${1} dest=${2}" 
