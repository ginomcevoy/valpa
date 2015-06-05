#!/bin/bash

sleepy=$(expr 60 \* 60 \* 4) # 4 hour
sleep $sleepy
nohup ./run-all.sh &> logs/balanced-cpv-96cores.log &
