#!/bin/bash 

# Waits for the deployed PBS VMs to be ready and in the 'free' state
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
		echo "Waits for the deployed PBS VMs to be ready and in the 'free' state"
        echo "Usage: $0 <#vms>"
        exit 1
fi

VMS=$1
TIMEOUT_MAX=300	 	# max wait
INTERVAL=3 			# check for cluster readiness at this period

READY=0
TIMEOUT_COUNT=0

# waiting loop 
while [ $READY == '0' -a $TIMEOUT_COUNT -lt $TIMEOUT_MAX ]; do
	# use pbs node list
	CURRENT_NODES=$(qnodes | grep 'state = free'  | wc -l)
	if [ $CURRENT_NODES -ge $VMS ]; then
		READY=1
	else
		# not yet
		echo "Waiting for PBS cluster..."
		sleep $INTERVAL
		TIMEOUT_COUNT=$(expr $TIMEOUT_COUNT + $INTERVAL)
	fi
done

if [ $TIMEOUT_COUNT -lt $TIMEOUT_MAX ]; then
	# deployment success
	echo "VMs are ready for PBS jobs!"
else
	# deployment timeout, return error code
	echo "PBS Deployment timeout!"
	exit 1
fi