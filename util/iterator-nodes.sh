#!/bin/bash
# Returns 'Y' if index is within node count (1 based)
# E.g. if nodes are 1,2,3  returns Y for 1, 2 or 3, but not for 4
# Useful for iterating names and numbers

# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2014

# Validate input
if [ $# -lt 1 ]; then
	echo "Returns 'Y' if index is within node count (1 based)"
	echo "Usage: $0 <node index>"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh

# params
INDEX=$1

# check available nodes
if [ $INDEX -gt 0 -a $INDEX -le $NODE_L ]; then
	echo "Y"
fi