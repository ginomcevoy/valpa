#!/bin/bash
# Resets the hostnames of all VMs to their names
# Author: Giacomo Mc Evoy
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

cd $LOCAL_DIR/../mgmt
./vcluster-command.sh "ssh -o StrictHostKeyChecking=no root@# 'echo # > /etc/hostname'"
./vcluster-command.sh "ssh root@# 'service hostname restart'"
./vcluster-command.sh 'ssh # hostname'
