#!/bin/bash

# Waits for the deployed VMs to be ready
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 2 ]; then
		echo "Waits for the deployed VMs to be ready"
        echo "Usage: $0 <deploymentType> <#vms>"
        exit 1
fi

DEPLOY_TYPE=$1
VMS=$2

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Do we use PBS?
if [ $DEPLOY_TYPE == 'PBS' ]; then

	# Use PBS wait
	$LOCAL_DIR/pbs/wait-pbs-deploy.sh $VMS
	if [ $? != 0 ]; then
		# PBS waiting timeout, propagate error
		exit 1
	fi
else 
	# Not implemented
	echo "**TODO** Not using PBS, waiting 15 seconds..."
	sleep 15
fi
