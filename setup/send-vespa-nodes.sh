#!/bin/bash

# Copies the scripts and VM profiles to the nodes
# Author: Giacomo Mc Evoy
# LNCC Brazil 2014

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh
VESPA_DIR=$LOCAL_DIR/..

$VESPA_DIR/mgmt-nodes/cluster-ssh.sh "mkdir -p $VESPA_DIR"
$VESPA_DIR/mgmt-nodes/cluster-ssh.sh "mkdir -p $VESPA_DIR/vespa"

# copy critical files to each host
$VESPA_DIR/mgmt-nodes/cluster-scp.sh $VESPA_DIR/setup $VESPA_DIR
$VESPA_DIR/mgmt-nodes/cluster-scp.sh $VESPA_DIR/params.sh $VESPA_DIR
$VESPA_DIR/mgmt-nodes/cluster-scp.sh $VESPA_DIR/vespa/core $VESPA_DIR/vespa

# Copy monitoring executables
$VESPA_DIR/mgmt-nodes/cluster-scp.sh $VESPA_DIR/monitor $VESPA_DIR
$VESPA_DIR/mgmt-nodes/cluster-ssh.sh "chmod +x $VESPA_DIR/monitor/*"

# Copy additional files to each host
$VESPA_DIR/mgmt-nodes/cluster-scp.sh $VESPA_DIR/networking $VESPA_DIR
$VESPA_DIR/mgmt-nodes/cluster-scp.sh $VESPA_DIR/data-output $VESPA_DIR
$VESPA_DIR/mgmt-nodes/cluster-scp.sh $VESPA_DIR/input $VESPA_DIR
$VESPA_DIR/mgmt-nodes/cluster-scp.sh $VESPA_DIR/util $VESPA_DIR

