#!/bin/bash 

# Starts VMs in the libvirt cluster that match the pattern of generate.sh
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 2 ]; then
		echo "Starts VMs that match the pattern of generate.sh in libvirt nodes"
        echo "Usage: $0 <#hosts> <#vms/host>"
        exit 1
fi

# Read input
HOSTS=$1
VMS_HOST=$2

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
for (( n=0 ; n<$HOSTS; n++ ))
do
	NODE_NAME=${NODE_PREFIX}${NODE[$n]}

	# call script for each host, will use remote invocation
	$LOCAL_DIR/start-vms-head.sh $VMS_HOST $NODE_NAME ${NODE[$n]}
done
