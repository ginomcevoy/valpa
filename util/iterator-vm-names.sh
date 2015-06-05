#!/bin/bash
# Returns the name of a VM (e.g. kvm-pbs01-03) given the
# node index (1) and VM index (03)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2014

# Validate input
if [ $# -lt 2 ]; then
	echo "Returns the name of a VM given the node index and VM index (1-based)"
	echo "$0: <node index> <vm index>"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

NODE_INDEX=$1
VM_INDEX=$2

if [ `$LOCAL_DIR/iterator-nodes.sh $1` -a $VM_INDEX -gt 0 -a $VM_INDEX -le $VM_L ]; then
	
	# Valid input, get its number with padding
	NODE_NUMBER=`$LOCAL_DIR/iterator-node-numbers.sh $NODE_INDEX`

	# Build VM name
	VM_NUMBER=$(printf "%02d\n" ${VM_INDEX})
	VM_NAME=$NAME_PREFIX${NODE_NUMBER}-${VM_NUMBER}
	echo $VM_NAME
fi