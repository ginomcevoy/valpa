#!/bin/bash 

# Stops the execution of all VMs matching the pattern of generate.sh
# This is meant to be executed from the head of the cluster
# Remote virsh access is needed (with password-less SSH)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
		echo "Stops the execution of all VMs matching the pattern of generate.sh"
        echo "Usage: $0 <#hosts> <'NOW'>"
        echo "If 'NOW' is provided, kill VMs immediately without halting them via SSH"
        exit 1
fi

# Read input
HOSTS=$1

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Load parameters
source $LOCAL_DIR/../params.sh

# Node names
declare -a NODE
for (( n=0; n<$HOSTS; n++ ))
do
	NODE_NUMBER=`expr $n + $NODE_FIRST`
	NODE[$n]=$(printf "%0${NODE_ZEROS}d\n" $NODE_NUMBER)
done

# Node loop
for (( n=0 ; n<$NODE_L; n++ ))
do
	NODE_NAME=${NODE_PREFIX}${NODE[$n]}

	# call script for each host, will use remote invocation
	$LOCAL_DIR/stop-vms-head.sh $NODE_NAME ${NODE[$n]} $2
done
