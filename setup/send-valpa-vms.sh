#!/bin/bash

# Copies monitor scripts to VMs
# Author: Giacomo Mc Evoy
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/../

# Import params
source $VALPA_DIR/params.sh

#copy monitor scripts
$VALPA_DIR/mgmt/vcluster-command.sh "ssh # 'mkdir -p $VALPA_DIR'" $VM_L
$VALPA_DIR/mgmt/vcluster-command.sh "scp -r $VALPA_DIR/monitor #:/$VALPA_DIR" $VM_L
