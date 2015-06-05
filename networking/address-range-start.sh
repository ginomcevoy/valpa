#!/bin/bash

# Returns the start of DHCP range for a node, give its index
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
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

if [ `$VALPA_DIR/util/iterator-nodes.sh $1` ]; then

	# Zero-based index
	NODE_ZERO_INDEX=`expr $NODE_INDEX - 1`

	# Behavior depends on class
	if [ $NET_CLASS == 'C' ]; then
		# First VM of first machine will get $IP_PREFIX.$DHCP_START
		# First VM of second machine will get $IP_PREFIX.($DHCP_START + DHCP_STEP)
		RANGE_START_SUFFIX=$(expr $DHCP_START + $DHCP_STEP \* $NODE_ZERO_INDEX)
		RANGE_START="${IP_PREFIX}.${RANGE_START_SUFFIX}"
 	elif [ $NET_CLASS == 'B' ]; then
 		# e.g. 172.16.82.1
 		NODE_NUMBER=`$VALPA_DIR/util/iterator-node-numbers.sh $1 NONZERO`
 		RANGE_START="${IP_PREFIX_B}.${NODE_NUMBER}.${DHCP_START_B}"
 	fi
 	echo $RANGE_START
fi
