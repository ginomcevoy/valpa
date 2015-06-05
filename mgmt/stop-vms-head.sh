#!/bin/bash 

# Stops the execution of VMs in a libvirt node matching the pattern of generate.sh
# This is meant to be executed from the head of the cluster
# Remote virsh access is needed (with password-less SSH)
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Original Author :
#    Joern http://www.linux-kvm.com/content/stop-script-running-vms-using-virsh
# Modified by : Vivek Kapoor http://exain.com
# Date: 22 May 2009

# Validate input
if [ $1 == 'help' ]; then
        echo "Usage: $0 [hostname] [node_number] <'NOW'>"
        echo "If node number is not provided, it will be inferred from provided hostname"
        echo "If no hostname is provided, assume local hostname"
       	echo "If 'NOW' is provided, kill VMs immediately without halting them via SSH"
        exit 1
fi

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"

# Import params
source $LOCAL_DIR/../params.sh

# Validate hostname
if [ $# -gt 0 ]; then
	HOST=$1
else
	#HOST="localhost"
	HOST=$(hostname)
fi

# May have argument for node number
if [ $# -gt 1 ]; then
    # Use node number
	NODE_NUMBER=$2
else
	# Infer from hostname
	NODE_NUMBER=$(echo $HOST | sed "s/[^0-9]//g;s/^$/-1/;")
fi


# Some parameters
if [ $# -ge 3 ] && [ $3 == 'NOW' ]; then
	TIMEOUT=0
else
	TIMEOUT=8
fi
LISTFILE=/tmp/runvm.lst
LOGFILE=/tmp/stopvms.log
SSH=/usr/bin/ssh
GREP=/bin/grep
CUT=/usr/bin/cut
TR=/usr/bin/tr
CAT=/bin/cat
DATE=/bin/date

PS="ssh $HOST /bin/ps"
VIRSH="virsh -c qemu+ssh://$HOST/system"

# Function to shutdown the virtual machine
kvmshutdown () {
COUNT=0
PID=$($PS ax|$GREP $1|$GREP kvm|$CUT -c 1-6)

echo kvmshutdown \: Shutting down $1 with pid $PID

#$VIRSH shutdown $1
$($SSH root@$1 shutdown -P now)

while [ "$COUNT" -lt "$TIMEOUT" ]
do
 $PS --pid $PID
 if [ "$?" -eq "1" ]
 then
 return 0
 else
 sleep 3
 COUNT=$(($COUNT+3))
 fi
done

echo kvmshutdown \: Timeout happened. Destroying VM $1

$VIRSH destroy $1

return 1

}

# The program begins here
$VIRSH list 2>/dev/null|$GREP running|$TR -s \ | awk '{print $2}'  > $LISTFILE

VMN=`$CAT $LISTFILE`

for vm in $VMN
do
 echo "$vm" is running
 kvmshutdown "$vm"
 if [ "$?" -eq "0" ]
 then
 echo VM "$vm" normally shutdown
 echo `$DATE +%Y-%m-%d\ %H:%M:%S` VM $vm normally shutdown >> $LOGFILE
 else
 echo VM "$vm" destroyed !
 echo `$DATE +%Y-%m-%d\ %H:%M:%S` VM $vm destroyed >> $LOGFILE
 fi;
done
