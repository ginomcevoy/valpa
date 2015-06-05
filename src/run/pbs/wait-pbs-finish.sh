#!/bin/bash

# Waits for the running PBS jobs to finish in the virtual cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

JOBS=1

# give time to the queue
sleep 2

# waiting loop 
while [ $JOBS == '1' ]; do
	# use pbs queue for any job
	JOBS=$(qstat | grep -c Job)
	if [ $JOBS == '1' ]; then
		# not yet
		echo "Waiting for PBS jobs to finish..."
		sleep 30
	fi
done
echo "PBS cluster is free!"
