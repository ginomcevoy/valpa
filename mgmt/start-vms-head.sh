#!/bin/bash

# Starts VMs in a libvirt node that match the pattern of generate.sh
# This is meant to be executed from the head of the cluster
# Remote virsh access is needed (with password-less SSH)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

#echo "Vars calling script:"
#echo $@

# Validate input
if [ $# -lt 1 ]; then
		echo "Starts VMs that match the pattern of generate.sh"
        echo "Usage: $0 <#vms> [hostname] [node_number]"
        echo "If node number is not provided, it will be inferred from provided hostname"
        echo "If no hostname is provided, assume local hostname"
        exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Load parameters
source $LOCAL_DIR/../params.sh

# Read input
VMS=$1

# Validate hostname
if [ $# -gt 1 ]; then
	HOST=$2
else
	#HOST="localhost"
	HOST=$(hostname)
fi

# May have argument for node number
if [ $# -gt 2 ]; then
    # Use node name
	NODE_NUMBER=$3
else
	# Infer from hostname
	NODE_NUMBER=$(echo $HOST | sed "s/[^0-9]//g;s/^$/-1/;")
fi

# VM names
declare -a VM
for (( i=1 ; i<=$VMS; i++ ))
do
	VM[$i]=`echo $i | awk '{printf "%02d", $0}'`
done

for (( i=1; i<=$VMS; i++ )); do
	VM_NAME=${NAME_PREFIX}${NODE_NUMBER}-${VM[$i]}
	#echo $VM_NAME

	# Call libvirt
	echo -e "virsh -c qemu+ssh://$HOST/system start $VM_NAME"
	virsh -c qemu+ssh://$HOST/system start $VM_NAME

	# let libvirt rest
	sleep 0
done
