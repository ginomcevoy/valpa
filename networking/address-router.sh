#!/bin/bash 

# Returns the netmask, depends on the class
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Import params
source $VESPA_DIR/params.sh

if [ $NET_CLASS == 'C' ]; then
	echo $IP_PREFIX.1
elif [ $NET_CLASS == 'B' ]; then
	echo $IP_PREFIX_B.0.254
fi