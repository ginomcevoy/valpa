#!/bin/bash

# Runs experiments in an automated fashion, using experiments.xml
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# load parameters
source $LOCAL_DIR/experiments.source
source $LOCAL_DIR/../params.sh

# start clean - will remove vms
if [ $REMOVE_CURRENT_VMS == 'true' ]; then

        echo "User requested to shut down all current VMs!"

	# Stop all VMs
	$LOCAL_DIR/../mgmt/stop-vms-all.sh $NODE_L

	# Undefine all VMs
	$LOCAL_DIR/../mgmt/undefine-vms-all.sh $NODE_L
fi

# Call XML reader
# Arguments:
# 1: the XML with experiments
# 2: the main directory for experiment groups
# 3: the name of the output file for the calling script
#python $LOCAL_DIR/list-reader.py $EXPERIMENT_INPUT $READER_GROUPS $READER_OUTPUT
python $LOCAL_DIR/parser.py $EXPERIMENT_INPUT $READER_GROUPS $READER_OUTPUT

# Read output file - all experiment rounds
for GROUPFILE in $(cat $READER_OUTPUT); do
	
	# concurrent experiments
	for DEPLOYMENT in $(ls $GROUPFILE/*); do

		# Read contents of deployment file as a key-value file
		#app=parpac
		#nc=1
		#cpv=1
		#idf=12
		#pstrat=NONE
		#runs=2
		source $DEPLOYMENT
		echo "Now running: np=$np cpv=$cpv idf=$idf pstrat=$pstrat $runs time(s)."
		echo `date`

		# Number of VMs
		VMS=$(expr $np / $cpv)

		# Define VMs
 		# echo "Usage: $0 <#cpv> {NONE|GREEDY|BALANCED|DISPARATE}"
		echo "Defining $cpv $pstrat"
		$LOCAL_DIR/../mgmt/define-vms-all.sh $cpv $pstrat

		# Start VMs according to distribution tuple
		# "Usage: $0 <cn> <cpv> <idf>"
		echo "Starting with cpv $cpv"
		$LOCAL_DIR/../mgmt/start-vms-dist.sh $np $cpv $idf

		# Wait for VMs to load
		# "Usage: $0 <app-name> <#vms> <#vms/host>"
  		# vms/host 	= #virt-cores/host / cpv
		#  	 	= phycores / (idf * cpv)
 		VMS_HOST=$(awk "BEGIN{print int($PHYPROCS * $PHYPROCCORES / $idf / $cpv)}")
                echo "VMs per host: $VMS_HOST , vms=$VMS"
		$LOCAL_DIR/../run/wait-start-vms.sh $app $VMS $VMS_HOST $cpv $pstrat

		# Prepare VMs
		$LOCAL_DIR/../run/prepare-vms.sh $app $VMS $VMS_HOST $cpv $pstrat

		# Run experiments
		# "Usage: $0 <app_name> <#runs> <distribution params cn, cpv, idf, ps> [app args...]"
		# TODO: pass arguments
		$LOCAL_DIR/../run/do-experiment.sh $app $runs $np $cpv $idf $pstrat
	done

	# Wait for experiments to finish
	# "Usage: $0 <app-name>"
	$LOCAL_DIR/../run/wait-end-jobs.sh $app

	# Stop all VMs
	$LOCAL_DIR/../mgmt/stop-vms-all.sh $NODE_L

	# Undefine all VMs
	$LOCAL_DIR/../mgmt/undefine-vms-all.sh $NODE_L
done
