#!/bin/bash 
# Execute a local command for each node in the physical cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -ne 1 ]; then
	echo "Execute a local command for each node in the physical cluster"
	echo "Usage: $0 <command>"
	echo "<command> should have the '#' symbol to be replaced by node *names*"
	exit 1
fi
COMMAND=$1

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

# Output file
OUTPUT=/tmp/valpa-command.sh
rm -f $OUTPUT

# Node loop to create commands
INDEX=1
while [ `$VALPA_DIR/util/iterator-nodes.sh $INDEX` ]; do
	NODE_NAME=`$VALPA_DIR/util/iterator-node-names.sh $INDEX`
	COMMANDTMP=${COMMAND//\#/$NODE_NAME}
	echo $COMMANDTMP
	echo $COMMANDTMP >> $OUTPUT
	INDEX=`expr $INDEX + 1`
done

# Execute commands
chmod +x $OUTPUT
$OUTPUT

# Clean
rm $OUTPUT