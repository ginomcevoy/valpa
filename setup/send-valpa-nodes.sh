#!/bin/bash

# Copies the scripts and VM profiles to the nodes
# Author: Giacomo Mc Evoy
# LNCC Brazil 2014

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh
VALPA_DIR=$LOCAL_DIR/..

$VALPA_DIR/mgmt-nodes/cluster-ssh.sh "mkdir -p $VALPA_DIR"
$VALPA_DIR/mgmt-nodes/cluster-ssh.sh "mkdir -p $VALPA_DIR/src"

# copy critical files to each host
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $VALPA_DIR/setup $VALPA_DIR
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $VALPA_DIR/params.sh $VALPA_DIR
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $VALPA_DIR/src/config $VALPA_DIR/src

# Copy additional files to each host
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $VALPA_DIR/networking $VALPA_DIR
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $VALPA_DIR/data-output $VALPA_DIR
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $VALPA_DIR/input $VALPA_DIR
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $VALPA_DIR/monitor $VALPA_DIR
$VALPA_DIR/mgmt-nodes/cluster-scp.sh $VALPA_DIR/util $VALPA_DIR
