#!/bin/bash
# Returns the node name given its 1-based index
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2014

# Validate input
if [ $# -lt 1 ]; then
	echo "Returns node name if index is within node count (1 based)"
	echo "Usage: $0 <node index>"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh

if [ `$LOCAL_DIR/iterator-nodes.sh $1` ]; then
	# build node name
	NUMBER=`expr $1 + $NODE_FIRST - 1`
	NUMBER=$(printf "%0${NODE_ZEROS}d\n" ${NUMBER})
	echo "${NODE_PREFIX}${NUMBER}"
fi


