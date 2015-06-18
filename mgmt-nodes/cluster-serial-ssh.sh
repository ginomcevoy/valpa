#!/bin/bash 
# Execute a remote command for each node in the physical cluster using SSH
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -ne 1 ]; then
	echo "Usage: $0 <command>"
	echo "<command> will execute via SSH on all cluster nodes"
	echo "<command> may have the '#' symbol to be replaced by node numbers"
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh

# Call multiple-nodes 
$LOCAL_DIR/cluster-command.sh "ssh -t # '${1}'"