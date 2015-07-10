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

# Use the Vespa generated inventory, first column has the node names
VESPA_INVENTORY=$($LOCAL_DIR/nodes-inventory.sh $NODE_L)
ZERO_INDEX=$(expr $1 - 1)
if [ $2 -a $2 != 'NONZERO' ]; then
	# use node suffix
	cat $VESPA_INVENTORY | cut -d ' ' -f 2 | cut -d '=' -f 2 | { mapfile -t nodeSuffixes; echo "${nodeSuffixes[$ZERO_INDEX]}"; }
else 
	# use node number
	cat $VESPA_INVENTORY | cut -d ' ' -f 4 | cut -d '=' -f 2 | { mapfile -t nodeNumbers; echo "${nodeNumbers[$ZERO_INDEX]}"; }
fi
