#!/bin/bash 

# Returns the end of DHCP range for a node, give its index
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
	echo "$0: <node index>"
	exit 1
fi

NODE_INDEX=$1

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Import params
source $LOCAL_DIR/../params.sh

if [ `$LOCAL_DIR/../util/iterator-nodes.sh $1` ]; then

	# Zero-based index
	NODE_ZERO_INDEX=`expr $NODE_INDEX - 1`

	# Behavior depends on class
	if [ $NET_CLASS == 'C' ]; then
		RANGE_END_SUFFIX=$(expr $DHCP_START + $DHCP_STEP \* $NODE_ZERO_INDEX + $VM_L - 1)
		RANGE_END="${IP_PREFIX}.${RANGE_END_SUFFIX}"
 	elif [ $NET_CLASS == 'B' ]; then
 		NODE_NUMBER=`$VESPA_DIR/util/iterator-node-numbers.sh $NODE_INDEX NONZERO`
 		RANGE_END_SUFFIX=$(expr $DHCP_START_B + $VM_L - 1)
 		RANGE_END="${IP_PREFIX_B}.${NODE_NUMBER}.${RANGE_END_SUFFIX}"
 	fi
 	echo $RANGE_END
fi

