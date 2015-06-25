#!/bin/bash
# Copy disk.img from master image (in each node)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2014

# Directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Load global params
source $VESPA_DIR/params.sh

# Validate input
if [ $# -lt 1 ]; then
	echo "Copy disk.img from master image (in each node)"
	echo "Usage: $0 <node_index>"
	exit 1
fi


# Input = node index
NODE_INDEX=$1

# Node name
NODE_NAME=`$VESPA_DIR/util/iterator-node-names.sh $NODE_INDEX`

# Master image location in nodes
MASTER_IMAGE=$VM_IMAGE_PATH/$VM_IMAGE_MASTER/$DISK_FILENAME

# Output
OUTPUT_LOG=/tmp/vespa-replicate-image.log
rm -f $OUTPUT_LOG
echo "Log at $OUTPUT_LOG"

#VM loop
for (( i=1; i<=VM_L; i++ )); do
  VM_NAME=$($VESPA_DIR/util/iterator-vm-names.sh $NODE_INDEX $i)
 
  # destination dir
  DEST_DIR=$VM_IMAGE_PATH/$NODE_NAME/$VM_NAME
  mkdir -p $DEST_DIR

  # copy sequentially
  echo "Copying to $DEST_DIR ..."
  cp $MASTER_IMAGE $DEST_DIR &>> $OUTPUT_LOG
done
