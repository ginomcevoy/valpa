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
	echo 255.255.255.0
elif [ $NET_CLASS == 'B' ]; then
	echo 255.255.0.0
fi