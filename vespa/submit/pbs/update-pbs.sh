#!/bin/bash 

# Reconfigures the PBS server for the given node profile
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Verify parameters
if [ $# -lt 2 ]; then
	echo "Reconfigures the PBS server for the given node profile"
	echo "Usage: $0 <nodesFile> <pbs_server_dir> [1 wait]"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

NODES_FILE=$1
PBS_SERVER=$2

# Do we need to update node definitions?
NEEDS_UPDATE=$(diff $NODES_FILE $PBS_SERVER/nodes | wc -l)
if [ $NEEDS_UPDATE -ne '0' ]; then

	#Kill PBS server
	echo "Killing Torque server"
	ssh root@localhost service torque-server stop
        ALIVE='1'
        while [ $ALIVE == '1' ]; do
                echo "Waiting for PBS to shut down...."
                ALIVE=$(ps -fea | grep pbs_server | grep -v grep | grep -c pbs_server)
                sleep 1
        done
        ALIVE='1'
	ssh root@localhost service torque-scheduler stop
        while [ $ALIVE == '1' ]; do
                echo "Waiting for Torque to shut down...."
                ALIVE=$(ps -fea | grep pbs_sched | grep -v grep | grep -c pbs_sched)
                sleep 3
        done

	# Update PBS server
	ssh root@localhost cp $NODES_FILE $PBS_SERVER/nodes
	ssh root@localhost service torque-server start
	ssh root@localhost service torque-scheduler start
 	
	if [ $# -eq 2 ]; then
		WAIT=20
		echo "Waiting for Torque scheduler to start... ($WAIT seconds)"
		sleep $WAIT
	fi
	ssh root@localhost 'qmgr -c "set server scheduling=true"'
	echo "Torque server restarted"
fi
