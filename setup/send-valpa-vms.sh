#!/bin/bash

# Copies monitor scripts to VMs
# Author: Giacomo Mc Evoy
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/../

# Import params
source $VESPA_DIR/params.sh

#copy monitor scripts
$VESPA_DIR/mgmt/vcluster-command.sh "ssh # 'mkdir -p $VESPA_DIR'" $VM_L
$VESPA_DIR/mgmt/vcluster-command.sh "scp -r $VESPA_DIR/monitor #:/$VESPA_DIR" $VM_L
