#!/bin/bash

# Validate input
if [ $# -lt 1 ]; then
        echo "Usage: $0 <prefix> [format] [suffix]"
	echo "will output <prefix><date><suffix>"
        exit 1
fi

# Read arguments
PREFIX=$1
if [ $# -gt 1 ]; then
	FORMAT=$2
	SUFFIX=$3
else
	FORMAT='%Y-%m-%d-%H:%M:%S'
fi

# Produce output
DATE=`date +$FORMAT`
echo "${PREFIX}${DATE}${SUFFIX}"