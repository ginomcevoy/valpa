#!/bin/bash 
# Replicates Vespa VM images from repository base to each VM folder
# This process is performed on Vespa nodes, need to distribute repository first
# Requires sudo pass on Vespa nodes (libvirt changes image ownership to root)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/../

# Import params
source $VESPA_DIR/params.sh

# Generate inventory for whole cluster
INVENTORY=$($VESPA_DIR/util/nodes-inventory.sh $NODE_L)

# Execute replicate-vm playbook, will perform required actions
ansible-playbook replicate-vms.yml --inventory=$INVENTORY --forks=$NODE_L --ask-sudo-pass --extra-vars="repo_root=$REPO_ROOT repo_base=$REPO_BASE_DIR" 
