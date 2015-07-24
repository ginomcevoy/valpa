#!/bin/bash 

# Converts vmstat output to txt files 
# Assumes vmstat 3.3.9
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Verify parameters
if [ $# -lt  2 ]; then
  echo "Converts vmstat output to txt files " 
  echo "Usage: $0 <data_dir> <node>"
  exit 1
fi

# Parameters
DATA_DIR=$1
NODE=$2

# Work the vmstat file
FILE_NAME=monitor-$NODE.vmstat
VMSTAT_FILE=$DATA_DIR/$FILE_NAME

# CPU data available: %user %system %idle %iowait %steal
# Selecting all of them
cat $VMSTAT_FILE | sed -e '/memory/d' | sed -e '/swpd/d' | awk '{print $13,$14,$15,$16,$17}' > $DATA_DIR/metrics-$NODE-cpu.txt
OK=$?
sed -i '1s/^/usr sys idle iowait steal\n/' $DATA_DIR/metrics-$NODE-cpu.txt

# Memory data available: swpd free buff cache
# Selecting: free cache
cat $VMSTAT_FILE | sed -e '/memory/d' | sed -e '/swpd/d' | awk '{print $4,$6}' > $DATA_DIR/metrics-$NODE-memory.txt
sed -i '1s/^/kbmemfree kbmemused\n/' $DATA_DIR/metrics-$NODE-memory.txt

# Disk data available: bi bo (blocks received in blocks/s, blocks sent in blocks/s)
# Selecting: bi bo
cat $VMSTAT_FILE | sed -e '/memory/d' | sed -e '/swpd/d' | awk '{print $9,$10}' > $DATA_DIR/metrics-$NODE-disk.txt
sed -i '1s/^/blkrxs blktxs\n/' $DATA_DIR/metrics-$NODE-disk.txt

if [ $OK -eq 0 ]; then
	# All done, remove vmstat file
	rm -f $VMSTAT_FILE
fi