#!/bin/bash 
###############################################
# Check dependencies for service nodes
# Optional VERBOSE variable (empty by default)
#
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2015
###############################################

# Validation functions
error_msg() {
  echo -e '\E[31m'"\033[1m[FAIL]\033[0m"
  >&2 echo -e "$1"
}

error_exit() {
  error_msg "$1"
  exit 1
}

ok_msg() {
  echo -e '\E[32m'"\033[1m[ OK ]\033[0m"
}

# By default, don't print intermediate outputs to stdout
# VERBOSE flag overrides this behavior
if [ -z $VERBOSE ]; then
  OUTPUT="/dev/null"
else
  OUTPUT="/dev/stdout"
fi

echo Checking for requirements at the service nodes...
echo

# bridge-utils presence
echo -n "Testing for bridge-utils...                           "
which brctl > $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Vespa requires bridge-utils at service nodes!"
else
  ok_msg
fi

# Torque mom (service node) presence
echo -n "Testing for Torque MOM...                             "
which pbs_mom > $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Vespa requires Torque MOM at service nodes!"
else
  ok_msg
fi

# QEMU/KVM presence
echo -n "Testing for KVM...                                    "
which kvm &> $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Vespa requires KVM at service nodes!"
else
  ok_msg
fi

# Any SSH server, e.g openSSH
echo -n "Testing for SSH server...                             "
echo quit | telnet localhost 22  2>/dev/null | grep Connected > $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Vespa requires SSH server at service nodes!"
else
  ok_msg
fi

# sysstat monitoring
echo -n "Testing for sysstat...                                "
which sar >  $OUTPUT
if [ $? -ne 0 ]; then
  echo -e '\E[33m'"\033[1m[WARN]\033[0m"
  >&2 echo
  >&2 echo "WARNING: missing sysstat for resource monitoring"
else
  echo -e '\E[32m'"\033[1m[ OK ]\033[0m"
fi

echo
echo Node requirements satisfied!
echo
