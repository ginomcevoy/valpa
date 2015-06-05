#!/bin/bash 

# Removes all VM definitions in a libvirt node matching the pattern of generate.sh
# This is meant to be executed from the head of the cluster
# Remote virsh access is needed (with password-less SSH)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Original Author :
#    Joern http://www.linux-kvm.com/content/stop-script-running-vms-using-virsh
# Modified by : Vivek Kapoor http://exain.com
# Date: 22 May 2009

# Validate input
if [ $1 == 'help' ]; then
		echo "Removes all VM definitions in a libvirt node matching the pattern of generate.sh"
        echo "Usage: $0 [hostname]"
        echo "If no hostname is provided, assume local hostname"
        exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh

# Validate hostname
if [ $# -ge 1 ]; then
	HOST=$1
else
	#HOST="localhost"
	HOST=$(hostname)
fi

# All VMs defined in node
VMS_IN_NODE=$(virsh -c qemu+ssh://$HOST/system list --all  | sed -e '1,2d' | sed -e 's/^[ \t]*//' | awk '{print $2}')

for DEFINED_VM in $VMS_IN_NODE; do

	# check if matches name prefix from generate.sh
	FOUND=$(echo "$DEFINED_VM" | grep $NAME_PREFIX)

	if [ -n "$FOUND" ]; then
		echo "Removing VM: $DEFINED_VM"

		# call libvirt
		#echo "virsh -c qemu+ssh://$HOST/system undefine $DEFINED_VM"
		virsh -c qemu+ssh://$HOST/system undefine $DEFINED_VM

		# let libvirt rest
		#sleep 1
	else
		echo "Not removing: $DEFINED_VM"
	fi
done
