#!/bin/bash
#---------------------------------------------------------------
# Project         : bin
# File            : monitor-stop.sh
# Version         : $Id: perfmon.sh,v 1.6 2008-03-14 17:54:48 fred Exp $
# Author          : Frederic Lepied
# Created On      : Wed May  9 17:19:40 2007
# Modified by     : Giacomo Mc Evoy (2013)
# Purpose         : 
#---------------------------------------------------------------

# Validate inputs
if [ $# -lt 1 ]; then
	echo "Usage: $0 <OUTPUT_DIR> [OUTPUT_FILENAME]"
	exit 1
fi

# Inputs
OUTPUTDIR=$1

if [ $# == '2' ]; then
  OUTPUTFILE=$2 
else
  OUTPUTFILE=monitor-$(hostname).sar
fi

TARGETDIR=/tmp/perfdata
SARPID=$(cat /tmp/sar.pid)
#IOSTATPID=$(cat /tmp/iostat.pid)

# Stop sar and its child sadc
pkill -TERM -P $SARPID
kill -TERM $SARPID &> /dev/null
echo "sar stopped at $(hostname)"

#kill $IOSTATPID
#echo "iostat stopped"

# collect postrun data
#cp /proc/interrupts $TARGETDIR/interrupts.after

#if type -p ifconfig >& /dev/null && type -p ethtool >& /dev/null; then
#    for ifc in `ifconfig | grep ^eth | cut -f1 -d ' '`; do
#        ethtool -S $ifc > $TARGETDIR/$ifc.after
#    done
#fi

# Verify that the output path exists (if NFS is not mounted, test should fail)
if [ -d $OUTPUTDIR ]; then
	mv $TARGETDIR/sar_data.dat $OUTPUTDIR/$OUTPUTFILE
	echo "Performance data in $(hostname):$OUTPUTFILE"
else
	>&2 echo "Monitor - output dir does not exist: $(hostname):$OUTPUTDIR"
	exit 1
fi

