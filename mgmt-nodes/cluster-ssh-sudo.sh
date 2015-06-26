#!/bin/bash

# Execute a remote command for each node in the Vespa physical cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

# Validate input
if [ $# -ne 1 ]; then
	>&2 echo -e 'Usage: cluster-ssh.sh "<command>"'
	>&2 echo "<command> will execute remotely on all physical nodes"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Import params
source $VESPA_DIR/params.sh

# Load node inventory
VESPA_INVENTORY=$($VESPA_DIR/util/nodes-inventory.sh $NODE_L)

ansible all -f $NODE_L -i $VESPA_INVENTORY -m shell --sudo --ask-sudo-pass -a "${1}"
