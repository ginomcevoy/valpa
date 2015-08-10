#!/bin/bash

# Waits for the running PBS jobs to finish in the virtual cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

TEMP_FILE=/tmp/vespa-qstat.txt
JOBS=1

# give time to the queue
sleep 2

# waiting loop 
while [ $JOBS == '1' ]; do
	# read PBS queue
	qstat > $TEMP_FILE
	JOBS=$(qstat | grep -c Job)
	if [ $JOBS == '1' ]; then
		# at least one job, get name of active job
		NAME=$(awk 'NR==3' $TEMP_FILE | awk '{print $2}')
		echo "Currently running: ${NAME} ..."
		sleep 60
	fi
done
echo "PBS cluster is free!"
