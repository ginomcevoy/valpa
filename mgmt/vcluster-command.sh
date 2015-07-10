#!/bin/bash
# Remotely execute a command over VMs in virtual cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
	echo "Remotely execute a command via SSH on VMs in virtual cluster"
	echo "Usage: $0 \"<command>\" [hostCount (default is NODE_L)] [#vms/node (default is VM_L)]"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Import params
source $VESPA_DIR/params.sh

# Input variables
COMMAND=$1
if [ $# -ge 2 ]; then
	HOST_COUNT=$2
else
	HOST_COUNT=$NODE_L
fi

if [ $# -eq 3 ]; then
	VMS_PER_HOST=$3
else
	VMS_PER_HOST=$VM_L
fi

# Get VM inventory
VM_INVENTORY=$($VESPA_DIR/util/vms-inventory.sh $HOST_COUNT $VMS_PER_HOST)

# Use ansible for call
ansible all -f $NODE_L -i $VM_INVENTORY -m shell -a "${1}"
