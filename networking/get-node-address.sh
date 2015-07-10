#!/bin/bash

# Returns the IP address of a node given the index
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
	echo "$0: Supply node index"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Import params
source $VESPA_DIR/params.sh

# Behavior depends on class
if [ $NET_CLASS == 'C' ]; then
	NODE_ADDRESS_PART=$(expr $1 + 1)
	ADDRESS=${IP_PREFIX}.${NODE_ADDRESS_PART}
elif [ $NET_CLASS == 'B' ]; then
	NODE_ADDRESS_PART=$($VESPA_DIR/util/iterator-node-numbers.sh $1 NONZERO)
	ADDRESS=${IP_PREFIX_B}.${NODE_ADDRESS_PART}.254
fi

echo $ADDRESS
