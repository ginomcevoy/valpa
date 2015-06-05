#!/bin/bash

# Original Author :
#    Joern http://www.linux-kvm.com/content/stop-script-running-vms-using-virsh
#
# Modified by : Vivek Kapoor http://exain.com
# Date: 22 May 2009

# Parameters you can modify :: START

TIMEOUT=10
LISTFILE=/tmp/runvm.lst
LOGFILE=/tmp/stopvms.log
# Parameters you can modify :: STOP

PS=/bin/ps
SSH=/usr/bin/ssh
GREP=/bin/grep
CUT=/usr/bin/cut
VIRSH=/usr/bin/virsh
TR=/usr/bin/tr
CAT=/bin/cat
DATE=/bin/date

# Function to shutdown the virtual machine
kvmshutdown () {
COUNT=0
PID=$($PS ax|$GREP $1|$GREP kvm|$CUT -c 1-6)

echo kvmshutdown \: Shutting down $1 with pid $PID

#$VIRSH shutdown $1
$($SSH root@$1 halt)

while [ "$COUNT" -lt "$TIMEOUT" ]
do
 $PS --pid $PID
 if [ "$?" -eq "1" ]
 then
 return 0
 else
 sleep 5
 COUNT=$(($COUNT+5))
 fi
done

echo kvmshutdown \: Timeout happened. Destroying VM $1

$VIRSH destroy $1

return 1

}

# The program begins here

$VIRSH list 2>/dev/null|$GREP running|$TR -s \ |$CUT -f3 -d\  > $LISTFILE

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