#!/bin/bash

# Returns the IP address of a VM given the node and VM indexes
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 2 ]; then
	echo "$0: <node 1based index> <vm 1based index>"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

if [ `$VALPA_DIR/util/iterator-nodes.sh $1` ]; then

	# Behavior depends on class
	if [ $NET_CLASS == 'C' ]; then
		IP_SUFFIX=`expr ${DHCP_START} + \( $1 \* ${DHCP_STEP} \) + $2 - 1`
		VM_ADDRESS="$IP_PREFIX.$IP_SUFFIX"
 	elif [ $NET_CLASS == 'B' ]; then
 		NODE_ADDRESS_PART=`expr $1 + $NODE_FIRST - 1`
 		VM_ADDRESS_PART=`expr $2`
 		VM_ADDRESS=${IP_PREFIX_B}.${NODE_ADDRESS_PART}.${VM_ADDRESS_PART}
 	fi
 
 	echo $VM_ADDRESS
fi



