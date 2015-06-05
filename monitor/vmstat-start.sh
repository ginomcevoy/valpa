#!/bin/bash
#---------------------------------------------------------------
# File            : vmstat-start.sh
# Created by	  : Giacomo Mc Evoy (2013)
# Purpose         : vmstat monitoring (can be called remotely)
#---------------------------------------------------------------

TARGETDIR=/tmp/perfdata
PATH=$PATH:/usr/sbin

# Setup raw output dir
if [ ! -d "$TARGETDIR" ]; then
    mkdir -p "$TARGETDIR"
fi

rm -rf $TARGETDIR/*

export LC_ALL=C

# start vmstat (assuming version 3.3.9+)
OUTPUT=vmstat.dat
rm -f $TARGETDIR/$OUTPUT
OPTIONS=""
# 1 = one second interval
vmstat $OPTIONS 1 >& $TARGETDIR/$OUTPUT &
VMSTAT_PID=$!
echo $VMSTAT_PID > /tmp/vmstat.pid

echo "vmstat started at $(hostname)"
sleep 1
