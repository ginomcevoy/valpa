#!/bin/bash

sleepy=$(expr 60 \* 60 \* 5) # 5 hour
sleep $sleepy
cd ../mgmt
./start-vms-dist.sh 144 1 1
./vcluster-command.sh 'ssh root@# "cat # > /etc/hostname"' 12
./vcluster-command.sh 'ssh root@# "service hostname restart"' 12
