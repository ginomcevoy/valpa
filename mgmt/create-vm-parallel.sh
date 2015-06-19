#!/bin/bash
# Creates all VMs for a cluster, using XML definitions
# Works in parallel using GNU parallel
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

# Validate input
if [ $# -lt 3 ]; then
	echo "Creates all VMs for a cluster, using XML definitions"
	echo "Usage: $0 <hostcount> <nodeFile> <definitionsFile>"
	exit 1
fi

# Params
HOST_COUNT=$1
NODE_FILE=$2
DEFINITIONS_FILE=$3

# Call GNU parallel
parallel -j $HOST_COUNT --xapply virsh -c qemu+ssh://{1}/system create {2} :::: $NODE_FILE :::: $DEFINITIONS_FILE
