#!/bin/bash

# Copy config.txt, topology.txt for a config
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -ne 2 ]; then
  echo "Usage: $0 <configInputDir> <configOutputDir>"
  exit 1
fi

# Input
INPUT_DIR=$1
OUTPUT_DIR=$2

# work
cp $INPUT_DIR/config.txt $OUTPUT_DIR/
cp $INPUT_DIR/../topology.txt $OUTPUT_DIR/
