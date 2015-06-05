#!/bin/bash 

# Returns the netmask, depends on the class
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

if [ $NET_CLASS == 'C' ]; then
	echo $IP_PREFIX.255
elif [ $NET_CLASS == 'B' ]; then
	echo $IP_PREFIX_B.255.255
fi