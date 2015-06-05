#!/bin/bash 

# Starts VMs in the libvirt cluster that match the pattern of generate.sh
# This is meant to be executed from the head of the cluster
# Remote virsh access is needed (with password-less SSH)
# Uses the DIST variables (cp, cpv, df)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 3 ]; then
		echo "Starts VMs that match the pattern of generate.sh in libvirt nodes"
        echo "Usage: $0 <cn> <cpv> <idf>"
        exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Load parameters
source $LOCAL_DIR/../params.sh

# Read input
CN=$1
CPV=$2
IDF=$3

# Total number of physical cores
PHYCORES=`expr $PHYPROCS \* $PHYPROCCORES`

# Convert to #hosts and #vms/host
VCORES_HOST=$(awk "BEGIN{print int($PHYCORES / $IDF)}") 
HOSTS=$(expr $CN / $VCORES_HOST)
VMS_HOST=$(expr $VCORES_HOST / $CPV)

# call script with #hosts and #vms_host
$LOCAL_DIR/start-vms-all.sh $HOSTS $VMS_HOST
