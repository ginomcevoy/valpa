#!/bin/bash
#---------------------------------------------------------------
# Project         : bin
# File            : monitor-start.sh
# Version         : $Id: perfmon.sh,v 1.6 2008-03-14 17:54:48 fred Exp $
# Author          : Frederic Lepied
# Created On      : Wed May  9 17:19:40 2007
# Modified by	  : Giacomo Mc Evoy (2013)
# Purpose         : SAR monitoring (can be called remotely)
#---------------------------------------------------------------

TARGETDIR=/tmp/perfdata
PATH=$PATH:/usr/sbin

# Setup raw output dir
if [ ! -d "$TARGETDIR" ]; then
    mkdir -p "$TARGETDIR"
fi

rm -rf $TARGETDIR/*

export LC_ALL=C

# collect some prerun data
#cp /proc/cpuinfo $TARGETDIR/
#cp /proc/interrupts $TARGETDIR/interrupts.before

#if type -p ifconfig >& /dev/null && type -p ethtool >& /dev/null; then
#    for ifc in `ifconfig | grep ^eth | cut -f1 -d ' '`; do
#	ethtool -S $ifc > $TARGETDIR/$ifc.before
#    done
#fi

# start sar (assuming version 9+)
rm -f $TARGETDIR/sar_data.dat
#OPTIONS_ORIG="-bBqrRuv${P}W -P ALL -n DEV -n EDEV -I SUM -I XALL"
#OPTIONS2013="-ruw -P ALL -n DEV -n EDEV"
OPTIONS="-rw -u ALL -P ALL -n DEV -n EDEV"  # 2014: more CPU metrics
# 1 = one second interval
sar $OPTIONS -o $TARGETDIR/sar_data.dat 1 >& $TARGETDIR/sar.out &
SARPID=$!
echo $SARPID > /tmp/sar.pid

#rm -f $TARGETDIR/iostat_data.dat
#iostat -t -d -k -x 1 >& $TARGETDIR/iostat_data.dat &
#IOSTATPID=$!
#echo $IOSTATPID > /tmp/iostat.pid

#echo "sar and iostat started"
echo "sar started at $(hostname)"
sleep 1
