#!/bin/bash +x

# Creates network configuration for the cluster nodes
# Output in data-output/networks
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
	echo "Creates network configuration in libvirt for each physical node"
	echo "Usage: $0 <libvirt-bridge | external-bridge | sriov>"
	echo "libvirt-bridge:  creates a network bridge in each node with DHCP"
	echo "external-bridge: defines network with external (existing) bridge"
	echo "sriov:           defines network with valid SR-IOV Virtual Functions"
	exit 1
fi

# Validate input
TYPE=$1
if [ $TYPE != 'libvirt-bridge' -a $TYPE != 'external-bridge' -a $TYPE != 'sriov' ]; then
  echo "Usage: $0 <libvirt-bridge | external-bridge | sriov>"
  exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Read parameters
source $VESPA_DIR/params.sh

# Output dir
OUTPUT_DIR=$VESPA_DIR/data-output/networks
mkdir -p $OUTPUT_DIR

# call script for creating XMLs
cd $VESPA_DIR/src
python -m network.create $TYPE $OUTPUT_DIR

# Iterate nodes
INDEX=1
while [ `$VESPA_DIR/util/iterator-nodes.sh $INDEX` ]; do

  if [ $TYPE == 'libvirt-bridge' ]; then
    # each node gets a different XML with DHCP information
    # example output file: libvirt-bridge-node082.xml
    NODE_NAME=`$VESPA_DIR/util/iterator-node-names.sh $INDEX`
    XML_NAME=libvirt-bridge-${NODE_NAME}.xml
  elif [ $TYPE == 'external-bridge' ]; then
    # each node gets the same XML with the same bridge name (vespa.params)
    # bridge should already exist in each node
    XML_NAME=external-bridge.xml
  elif [ $TYPE == 'sriov' ]; then
    # each node gets the same XML with the same network interface (vespa.params)
    # SR-IOV should already be configured for that interface
    XML_NAME=sriov.xml
  fi

  OUTPUT_FILE=$OUTPUT_DIR/$XML_NAME

  # create virtual bridge in the node
  virsh -c qemu+ssh://$NODE_NAME/system net-create $OUTPUT_FILE

  INDEX=$(expr $INDEX + 1)
done

echo "Created network file(s) in $OUTPUT_DIR"
