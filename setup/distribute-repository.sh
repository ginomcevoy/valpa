#!/bin/bash

# Synchronizes the VM repositories of all nodes to the master node
# Uses rsync (ansible synchronize) to upload disk images
# Author: Giacomo Mc Evoy
# LNCC Brazil 2015

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Import params
source $VESPA_DIR/params.sh

# Generate inventory for whole cluster
INVENTORY=$($VESPA_DIR/util/nodes-inventory.sh $NODE_L)

# Create repository in nodes if it does not exist
ansible all -f $NODE_L -i $INVENTORY -m command -a "mkdir -p $REPO_ROOT/$REPO_BASE"

# Update VM images using rsync, one node at a time
ansible all -f 1 -i $INVENTORY -m synchronize -a "src=$REPO_ROOT/$REPO_BASE/ dest=$REPO_ROOT/$REPO_BASE/"