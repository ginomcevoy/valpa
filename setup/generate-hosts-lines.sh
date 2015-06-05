##!/bin/bash 

# Creates the lines to be added to /etc/hosts file
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Load parameters
source $VALPA_DIR/params.sh

# Create arrays
declare -a NODE
declare -a VM

# VM names
for (( i=1 ; i<=$VM_L; i++ ))
do
	VM[$i]=`echo $i | awk '{printf "%02d", $0}'`
done

# Output file
OUTPUT="$VALPA_DIR/data-output/hosts"
rm $OUTPUT

# Create lines for nodes
for (( i=1; i<=$NODE_L; i++ ))
do
	# Node name
	NODE_NAME=$($VALPA_DIR/util/iterator-node-names.sh $i)

    # First node will get $IP_PREFIX.1
	IP_ADDRESS=$($VALPA_DIR/networking/get-node-address.sh $i)

	echo -e "$IP_ADDRESS\t${NODE_NAME}" >> $OUTPUT
done

echo -e "" >> $OUTPUT

# Create lines for VMs
for (( NODE_INDEX=1; NODE_INDEX<=$NODE_L; NODE_INDEX++ ))
do

	# Node number
	NODE_NUMBER=$($VALPA_DIR/util/iterator-node-numbers.sh $NODE_INDEX)

	# VM/node loop
	for (( vm=1; vm<=$VM_L; vm++ ))
	do
		# VM name
		VM_NUMBER=$(expr $vm + 1)
		VM_NAME=$($VALPA_DIR/util/iterator-vm-names.sh $NODE_INDEX $vm)
		VM_ADDRESS=$($VALPA_DIR/networking/get-vm-address.sh $NODE_INDEX $vm)

		echo -e "$VM_ADDRESS\t${VM_NAME}" >> $OUTPUT
	done
done

echo "/etc/hosts file for VMs generated at ${OUTPUT}"
