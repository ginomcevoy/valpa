#!/bin/bash
FREE=$(qnodes | grep 'state = free' | wc -l)
echo "$FREE VMs are free"
