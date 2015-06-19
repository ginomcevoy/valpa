#!/bin/bash 

# Stops the execution of VMs in a VALPA node matching the pattern
# VM prefix names specified in VALPA parameters
# This is meant to be executed at each node (e.g. via Ansible)
# Assumes KVM when killing VM processes
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015

# Input parameter: VM name, used to identify VMs managed by VALPA

# Original Author :
#    Joern http://www.linux-kvm.com/content/stop-script-running-vms-using-virsh
# Modified by : Vivek Kapoor http://exain.com
# Date: 22 May 2009

# Validate input
if [[ $# -lt 1 ]]; then
	>&2 echo "Usage: $0 [vm_prefix] <'NOW'>"
	>&2 echo "vm_prefix: from VALPA parameters"
	>&2 echo "If 'NOW' is provided, kill VMs immediately without halting them via SSH"
	exit 1
fi

VM_PREFIX=$1

# Timeout parameter (10 seconds by default, immediately if NOW supplied)
if [ $# -gt 1 ] && [ $2 == 'NOW' ]; then
	TIMEOUT=0
else
	TIMEOUT=10
fi

LISTFILE=/tmp/runvm.lst
LOGFILE=/tmp/stopvms.log
SSH="/usr/bin/ssh -o StrictHostKeyChecking=no"
GREP=/bin/grep
CUT=/usr/bin/cut
TR=/usr/bin/tr
CAT=/bin/cat
DATE=/bin/date
PS=/bin/ps
VIRSH=virsh 

# Function to shutdown the virtual machine
kvmshutdown () {
COUNT=0
PID=$($PS ax|$GREP $1|$GREP kvm|$CUT -c 1-6)

echo Shutting down $1 with pid $PID

$($SSH root@$1 shutdown -P now)

while [ "$COUNT" -lt "$TIMEOUT" ]
do
 $PS --pid $PID > /dev/null
 if [ "$?" -eq "1" ]
 then
 return 0
 else
 sleep 3
 COUNT=$(($COUNT+3))
 fi
done

echo Timeout happened. Destroying VM $1

$VIRSH destroy $1

return 1

}

# The program begins here
$VIRSH list 2>/dev/null|$GREP $VM_PREFIX | $TR -s \ | awk '{print $2}'  > $LISTFILE

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
