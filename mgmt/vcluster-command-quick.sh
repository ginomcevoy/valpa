#!/bin/bash
# Remotely execute a command over VMs in virtual cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 1 ]; then
	echo "Remotely execute a command over VMs in virtual cluster"
	echo "Usage: $0 <command> [#vms/node (default is VM_L)]"
	echo "<command> should have the # simbol, it will replaced by the VM *name*."
	exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

# Input variables
COMMAND=$1
if [ $# -eq 2 ]; then
	NUMVM=$2
else
	NUMVM=$VM_L
fi

# Output file
OUTPUT=/tmp/valpa-command.sh
rm -f $OUTPUT &> /dev/null

# Iterate physical machines
NODE_INDEX=1
while [ `$VALPA_DIR/util/iterator-nodes.sh $NODE_INDEX` ]; do

	# Iterate VMs
	for (( VM_INDEX=1; VM_INDEX<=$NUMVM; VM_INDEX++ )); do

		# Get VM name
		VM_NAME=`$VALPA_DIR/util/iterator-vm-names.sh $NODE_INDEX $VM_INDEX`
		COMMANDTMP=${COMMAND//\#/$VM_NAME}
		echo $COMMANDTMP
		echo "$COMMANDTMP &" >> $OUTPUT
	done

	NODE_INDEX=`expr $NODE_INDEX + 1`
done

chmod +x $OUTPUT
$OUTPUT & &> /tmp/valpa-generated.log
