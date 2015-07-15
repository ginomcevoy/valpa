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

# Use the Vespa generated inventory, first column has the node names
VESPA_INVENTORY=$($LOCAL_DIR/nodes-inventory.sh $NODE_L)
ZERO_INDEX=$(expr $1 - 1)
cat $VESPA_INVENTORY | cut -d ' ' -f 1 | { mapfile -t nodeNames; echo "${nodeNames[$ZERO_INDEX]}"; }
