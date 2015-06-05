#!/bin/bash

# Uses remote virsh to load network configurations
# Needs access to the working nodes (not through the bridge, as this script will create it)
# Author: Giacomo Mc Evoy
# LNCC Brazil 2013

# ********* BUG ************
# libvirt won't attach the network device to the bridge
# do this manually with command
# sudo brctl addif <bridge> <eth#>

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh

# Node names
declare -a NODE
for (( n=0; n<$NODE_L; n++ ))
do
	NODE_NUMBER=`expr $n + $NODE_FIRST`
	NODE[$n]=$(printf "%0${NODE_ZEROS}d\n" $NODE_NUMBER)
done

# Node loop
for (( n=0 ; n<$NODE_L; n++ ))
do
	NODE_NAME=${NODE_PREFIX}${NODE[$n]}

	# remove previous config
 	virsh -c qemu+ssh://$NODE_NAME/system net-destroy $NET_NAME 2> /dev/null
 	virsh -c qemu+ssh://$NODE_NAME/system net-undefine $NET_NAME 2> /dev/null
        #ssh -t $NODE_NAME /home/giacomo2/kvmgen/setup/kill-network.sh
	
	# load network config
 	virsh -c qemu+ssh://$NODE_NAME/system net-create $LOCAL_DIR/../data-output/vms/$NODE_NAME/$NODE_NAME.xml
	
	# patch networking
	#ssh -t $NODE_NAME sudo brctl addif br1 eth0
done

