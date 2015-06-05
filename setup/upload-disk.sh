#!/bin/bash

# Uses scp to upload VM disk.img to nodes
# User needs to select which image to use
# Author: Giacomo Mc Evoy
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

# Get input
if [ $# -lt 1 ]; then
  echo "Need to specify disk for VMs, available options:"
  echo "ubuntu14.04-node"
  exit 1
fi

# Shutdown all VMs
$VALPA_DIR/mgmt/stop-vms-all.sh $NODE_L

# DIsk image
DISK_TYPE=$1
VM_IMAGE_PATH_FULL=~/$VM_IMAGE_PATH/$DISK_TYPE
DISK_FILE=$VM_IMAGE_PATH_FULL/$DISK_FILENAME

if [ ! -f $DISK_FILE ]; then
  echo "Master disk $DISK_FILE does not exist!"
  exit 1
fi

$VALPA_DIR/mgmt-nodes/cluster-ssh.sh "mkdir -p $VM_IMAGE_PATH_FULL"
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $DISK_FILE $VM_IMAGE_PATH_FULL
