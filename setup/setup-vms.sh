#!/bin/bash 
# Configures Vespa VMs 
# This procedures consists of the following steps:
# 1) Destroy any current VMs
# 2) Create all possible VMs
# 3) Configure VMs: hostname, /etc/hosts, copy Vespa files
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/../

# Import params
source $VESPA_DIR/params.sh

# Stop all VMs
$VESPA_DIR/mgmt/stop-vms-all.sh $NODE_L

# Create all possible VMs
NC=$(expr $NODE_L \* $VM_L)
CPV=1
IDF=$VM_L
PS='NONE'
cd $VESPA_DIR/vespa
python quickcluster.py $NC $CPV $IDF $PS

# Create /etc/hosts file
ETC_HOSTS=$VESPA_DIR/data-output/hosts
python -m network.etchosts $ETC_HOSTS 

# Generate inventory for all VMs: TODO: use inventory.all call
INVENTORY=$($VESPA_DIR/util/vms-inventory.sh $NODE_L $VM_L)

# Call playbook that configures VMs
cd $LOCAL_DIR
ansible-playbook setup-vms.yml --inventory=$INVENTORY --forks=$NODE_L --extra-vars="vespa_dir=$VESPA_DIR etc_hosts=$ETC_HOSTS"
