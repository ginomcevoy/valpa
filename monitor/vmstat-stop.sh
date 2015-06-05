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

# Copy to output dir
if [ ! -z $OUTPUTDIR ]; then
	mkdir -p $OUTPUTDIR
	cp $TARGETDIR/vmstat.dat $OUTPUTDIR/$OUTPUTFILE
 	THEDIR=$OUTPUTDIR
else
	THEDIR=$TARGETDIR
fi

echo "Performance data in $(hostname):$THEDIR"
