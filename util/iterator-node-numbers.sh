#!/bin/bash
# Returns the number of a node (e.g. 083 for node083) given the index
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
	echo "$0: Supply node index"
	echo "Optional parameter: 'NONZERO' to avoid padding"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh

if [ `$LOCAL_DIR/iterator-nodes.sh $1` ]; then
	# build node name
	NUMBER=`expr $1 + $NODE_FIRST - 1`
	if [ $2 -a $2 != 'NONZERO' ]; then
		NUMBER=$(printf "%0${NODE_ZEROS}d\n" ${NUMBER})
	fi
	echo "${NUMBER}"
fi


