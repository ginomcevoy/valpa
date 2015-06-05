#!/bin/bash 

# Removes VM definitions from libvirt that match the pattern of generate.sh
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Load parameters
source ../params.sh

# May have argument for node number
if [ $# -eq 1 ]; then
    # Use node name
	NODE_NUMBER=$1
else
	# Infer from hostname
	NODE_NUMBER=$(hostname | sed "s/[^0-9]//g;s/^$/-1/;")
fi

for DEFINED_VM in $(virsh list --all 2>/dev/null|tr -s \ |cut -f3 -d\ | sed -e '1,2d'); do
	FOUND=$(echo "$DEFINED_VM" | grep $NAME_PREFIX)
	#echo $FOUND
	#FOUND=$(echo "$FOUND" | grep $NODE_NUMBER)
	#echo $FOUND
	if [ -n "$FOUND" ]; then
		echo "Removing VM: $DEFINED_VM"

		# call libvirt
		virsh undefine $DEFINED_VM

		# let libvirt rest
		sleep 1

	else
		echo "Not removing: $DEFINED_VM"
	fi
done