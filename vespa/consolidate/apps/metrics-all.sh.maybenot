#!/bin/bash 

# metrics-all.sh
# Composes a single CSV output each of the DIST entries
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Verify arguments
if [ $# -lt 3 ]; then
  echo "Composes a single CSV output for Parpac Benchmark"
  echo "Usage #0 <dist_dir> <csv_name> {Config | Dist}"
fi
 
# Calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Input
DIST_DIR=$1
CSV_NAME=$2
FUSED_TITLE=$3

# Find all config dirs
declare -a CONFIGS
i=0
for CONFIG in $(ls -d1 $DIST_DIR/*/); do
  CONFIGS[i]=${CONFIG}${CSV_NAME}
  i=$i+1 
done

# The main CSV output
OUTPUT=$DIST_DIR/${CSV_NAME}

# Call python script
python $LOCAL_DIR/fuseAppMetrics.py $OUTPUT $FUSED_TITLE ${CONFIGS[@]}

