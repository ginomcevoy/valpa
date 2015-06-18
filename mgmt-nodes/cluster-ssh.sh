#!/bin/bash

# Execute a remote command for each node in the VALPA physical cluster
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
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

# Load inventory TODO Fix this call
VALPA_INVENTORY=$VALPA_DIR/input/valpa.inventory

ansible all -f $NODE_L -i $VALPA_INVENTORY -m command -a "${1}"
