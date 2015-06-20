#!/bin/bash

# Stops the execution of all VALPA VMs in the VALPA cluster
# This is meant to be executed from the head of the cluster
# Remote virsh access is needed (with password-less SSH)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

# Validate input
if [ $# -lt 1 ]; then
		echo "Stops the execution of all VMs matching the pattern of generate.sh"
        echo "Usage: $0 <#hosts> ['NOW']"
        echo "If 'NOW' is provided, kill VMs immediately without halting them via SSH"
        exit 1
fi

# Read input
HOSTS=$1

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/../

# Load parameters
source $VALPA_DIR/params.sh

# Generate inventory for requested nodes
INVENTORY=$($VALPA_DIR/util/nodes-inventory.sh $HOSTS)

# Make ansible call
ansible all -f $HOSTS -i $INVENTORY -m script -a "$LOCAL_DIR/stop-vms-local.sh $VM_PREFIX"
