#!/bin/bash
################################################
# Check dependencies for both master and nodes
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

echo Checking for common requirements...
echo

# Test for sudo call
echo -n "Testing for sudo...                                   "
if [ "$UID" -ne "0" ] ; then
  error_exit "Please install with sudo/root privileges."
else
  ok_msg
fi

# libvirt presence
echo -n "Testing for libvirt...                                "
virsh list > $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Libvirt not installed or not properly configured for user!"
else
  ok_msg 
fi

# Python presence
echo -n "Testing for Python 2.7+...                            "
PYTHON_V=/tmp/python-version
python -V 2> $PYTHON_V 
cat $PYTHON_V > $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Vespa requires Python 2.7+!"
fi

# Python 2.7+
PYTHON_MAJOR=$(cat /tmp/python-version | cut -d ' ' -f 2 | cut -d '.' -f 1)
PYTHON_MINOR=$(cat /tmp/python-version | cut -d ' ' -f 2 | cut -d '.' -f 2)
echo $PYTHON_MAJOR.$PYTHON_MINOR > $OUTPUT
if [ $PYTHON_MAJOR -ne 2 -o $PYTHON_MINOR -lt 7 ]; then
  error_exit "Vespa requires Python 2.7+!"
else
  ok_msg
fi 

echo
echo Common requirements satisfied!
echo

