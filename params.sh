#!/bin/bash
# Load Vespa parameters for shell scripts

# calculate directory local to script
#LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
FULL_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)/`basename "${BASH_SOURCE[0]}"`
VESPA_DIR=$(dirname $FULL_PATH)

# Go to Vespa source
ORIG_PATH=$PWD
cd $VESPA_DIR/src

# Get the filename TODO: handle exit code != 0
VESPA_PARAMS=$(python -m config.shellparams)

# source the parameters
source $VESPA_PARAMS

# return to path
cd $ORIG_PATH
