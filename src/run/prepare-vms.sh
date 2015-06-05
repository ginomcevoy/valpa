#!/bin/bash 

# Waits for the deployed VMs to be ready
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 2 ]; then
		echo "Prepares the deployed VMs"
        echo "Usage: $0 <#vms/host> <ACTIVE_NODES>"
        exit 1
fi

VMS_HOST=$1
ACTIVE_NODES=$2

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Load parameters
source $LOCAL_DIR/run-params.sh

# Validate strategy
#$LOCAL_DIR/../pinnings/check-pinning.sh $PSTRAT
#if [ $? -ne 0 ]; then
#  exit 1
#fi

# VMs are running now, make sure that NFS in mounted correctly
if [ $USE_NFS == 'true' ]; then
	echo "Ensuring NFS in VMs...."
	$LOCAL_DIR/../mgmt/vcluster-command.sh 'ssh root@# mount -a' $VMS_HOST $ACTIVE_NODES
fi

# make sure that KNEM module is loaded
if [ $USE_KNEM == 'true' ]; then
	echo "Ensuring KNEM in VMs...."
	$LOCAL_DIR/../mgmt/vcluster-command.sh 'ssh root@# modprobe knem' $VMS_HOST $ACTIVE_NODES
fi
