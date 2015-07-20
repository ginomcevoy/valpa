#!/bin/bash 
# Creates an Ansible inventory file based on Vespa VMs
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/../

# Import params
source $VESPA_DIR/params.sh

# Validate input
if [ $# -lt 2 ]; then
	>&2 echo "Creates an Ansible inventory file based on Vespa nodes"
	>&2 echo "Prints the filename (default = ${DEFAULT_VM_INVENTORY})"
	>&2 echo "Usage: $0 <hostCount> <vmsPerHost> [filename]"
	exit 1
fi

HOST_COUNT=$1
VMS_PER_HOST=$2

# Output filename
if [[ $# -eq 3 ]]; then
	INVENTORY=$3
else
	INVENTORY=$DEFAULT_VM_INVENTORY
fi
rm -f $INVENTORY

# Call python
PYTHONPATH=$VESPA_DIR/vespa python -m core.inventory_vm $HOST_COUNT $VMS_PER_HOST $INVENTORY

