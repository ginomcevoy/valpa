#!/bin/bash 
# Creates an Ansible inventory file based on Vespa nodes
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/../

# Import params
source $VESPA_DIR/params.sh

# Validate input
if [ $# -lt 1 ]; then
	>&2 echo "Creates an Ansible inventory file based on Vespa nodes"
	>&2 echo "Prints the filename (default = ${DEFAULT_NODE_INVENTORY})"
	>&2 echo "Usage: $0 <hostCount> [filename]"
	exit 1
fi

HOST_COUNT=$1

# Output filename
if [[ $# -eq 2 ]]; then
	INVENTORY=$2
else
	INVENTORY=$DEFAULT_NODE_INVENTORY
fi
rm -f $INVENTORY

# Call python
PYTHONPATH=$VESPA_DIR/vespa python -m core.inventory_node $HOST_COUNT $INVENTORY

