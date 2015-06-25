#!/bin/bash 
# Creates an Ansible inventory file based on Vespa nodes
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

DEFAULT_INVENTORY="/tmp/vespa-node-inventory.txt"

# Validate input
if [ $# -lt 1 ]; then
	>&2 echo "Creates an Ansible inventory file based on Vespa nodes"
	>&2 echo "Prints the filename (default = ${DEFAULT_INVENTORY})"
	>&2 echo "Usage: $0 <hostCount> [filename]"
	exit 1
fi

HOST_COUNT=$1

# Output filename
if [[ $# -eq 2 ]]; then
	INVENTORY=$2
else
	INVENTORY=$DEFAULT_INVENTORY
fi
rm -f $INVENTORY

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/../

# Import params
source $VESPA_DIR/params.sh

# Node loop
INDEX=1
while [ $($VESPA_DIR/util/iterator-nodes.sh $INDEX) ]; do
	if [[ $INDEX -le $HOST_COUNT ]]; then
		NODE_NAME=$($VESPA_DIR/util/iterator-node-names.sh $INDEX)
		echo $NODE_NAME >> $INVENTORY
	fi
	INDEX=`expr $INDEX + 1`
done
echo $INVENTORY
