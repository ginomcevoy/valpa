#!/bin/bash
#---------------------------------------------------------------
# File            : vmstat-stop.sh
# Created by	  : Giacomo Mc Evoy (2013)
# Purpose         : Stop vmstat monitoring
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
  OUTPUTFILE=monitor-$(hostname).vmstat
fi

TARGETDIR=/tmp/perfdata
VMSTAT_PID=$(cat /tmp/vmstat.pid)
kill $VMSTAT_PID
echo "vmstat stopped"

if [ -d $OUTPUTDIR ]; then
	mv $TARGETDIR/sar_data.dat $OUTPUTDIR/$OUTPUTFILE
	echo "Performance data in $(hostname):$OUTPUTFILE"
else
	>&2 echo "Monitor - output dir does not exist: $(hostname):$OUTPUTDIR"
	exit 1
fi