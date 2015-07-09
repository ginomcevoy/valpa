#!/bin/bash 

# Converts sysstat output to txt files (less space)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Verify parameters
if [ $# -lt  2 ]; then
  echo "Converts sysstat output to txt files " 
  echo "Usage: $0 <sar_dir> <node>"
  exit 1
fi

# Parameters
SAR_DIR=$1
NODE=$2

# Work the sar file
SAR_NAME=monitor-$NODE.sar
SAR_FILE=$SAR_DIR/$SAR_NAME

# Old CPU data: (%user     %nice   %system   %iowait    %steal     %idle)
#LC_ALL="POSIX" sar -f $SAR_FILE -u ALL -P ALL | grep Average | awk '{print $3,$5,$6,$8,$10,$12}' > $SAR_DIR/metrics-$NODE-cpu.txt  
 
# New CPU data available: (%usr %nice %sys %iowait %steal %irq %soft %guest %gnice %idle)
# Selecting: %usr %sys %iowait %irq %guest %idle
LC_ALL="POSIX" sar -f $SAR_FILE -u ALL -P ALL | sed -e '1,3d' | sed -e '/Average/d' | sed -e '/all/d' | awk '{print $3,$5,$6,$8,$10,$12}' | sed -e '/usr/d' | sed -r 's/^\s*//; s/\s*$//; /^$/d' > $SAR_DIR/metrics-$NODE-cpu.txt
OK=$?
sed -i '1s/^/usr sys iowait irq guest idle\n/' $SAR_DIR/metrics-$NODE-cpu.txt


# Generate memory data (kbmemfree kbmemused)
LC_ALL="POSIX" sar -f $SAR_FILE -r | sed -e '1,3d' | sed -e '$d' | awk '{print $2,$3}' > $SAR_DIR/metrics-$NODE-memory.txt
sed -i '1s/^/kbmemfree kbmemused\n/' $SAR_DIR/metrics-$NODE-memory.txt

# Generate network data (rxkb/s, txkb/s)
LC_ALL="POSIX" sar -f $SAR_FILE -n DEV | grep eth0 | sed -e '/Average/d' | awk '{print $5,$6}' > $SAR_DIR/metrics-$NODE-network.txt
sed -i '1s/^/rxkbs txkbs\n/' $SAR_DIR/metrics-$NODE-network.txt

# Generate network error data (rxerr/s, txerr/s, rxdrop/s, txdrop/s)
LC_ALL="POSIX" sar -f $SAR_FILE -n EDEV | grep eth0 | sed -e '/Average/d' | awk '{print $3,$4,$6,$7}' > $SAR_DIR/metrics-$NODE-network-errors.txt
sed -i '1s/^/rxerrs txerrs rxdrops txdrops\n/' $SAR_DIR/metrics-$NODE-network-errors.txt

if [ $OK -eq 0 ]; then
	# All done, remove SAR file
	rm -f $SAR_FILE
fi