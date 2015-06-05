#!/bin/bash 

# Creates the /etc/network/interfaces file for each node
# Not needed if using libvirt bridge
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

# delete output dir
echo "Deleting output!"
OUTPUT_DIR=$VALPA_DIR/data-output/interfaces
rm -rf $OUTPUT_DIR

# create ouptut dir
mkdir -p $OUTPUT_DIR

# iterate over nodes
INDEX=1
while [ `$VALPA_DIR/util/iterator-nodes.sh $INDEX` ]; do
	
	# get name for node
	NODE_NAME=`$VALPA_DIR/util/iterator-node-names.sh $INDEX`

	# create a copy of the master file, filename is the node name
	OUTPUT_FILE=$OUTPUT_DIR/$NODE_NAME
	cp $VALPA_DIR/data-input/interfaces-template.txt $OUTPUT_FILE

	# update ip suffix on file
	NODE_NUMBER=`expr $INDEX + $NODE_FIRST`
	sed "s/\_NODE\_NUMBER/${NODE_NUMBER}/g" ${OUTPUT_FILE} > /tmp/$NODE_NAME
	mv /tmp/$NODE_NAME $OUTPUT_FILE

	INDEX=`expr $INDEX + 1`
done

echo "Interfaces files created at $OUTPUT_DIR"