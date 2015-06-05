#!/bin/bash
# Generates the file with the nodes for PBS
# Depends on the number of processes per node (cpv)

# Verify input
if [ $# -ne 1 ]; then
  echo "Usage: $0 <cpv>"
  exit 0
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../../params.sh

cpv=$1

# Output file
OUTPUT=$LOCAL_DIR/nodes
rm -f $OUTPUT

# Node names
declare -a NODE
declare -a VM

# Node loop
for (( n=0 ; n<$NODE_L; n++ ))
do
	NODE_NUMBER=`expr $n + $NODE_FIRST`
	NODE[$n]=$(printf "%0${NODE_ZEROS}d\n" $NODE_NUMBER)
	NODE_NAME=${NODE_PREFIX}${NODE[$n]}

	# First VM loop - independent of #cores 
	for (( vm=1 ; vm<=$VM_L; vm++ ))
	do
		VM[$vm]=`echo $vm | awk '{printf "%02d", $0}'`
		VM_NAME=${NAME_PREFIX}${NODE[$n]}-${VM[$vm]}
		echo "$VM_NAME np=$cpv" >> $OUTPUT
		echo "$VM_NAME np=$cpv"
	done

done

