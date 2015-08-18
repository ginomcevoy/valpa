#!/bin/bash 
###############################################
# Check dependencies for master node
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

echo Checking for requirements at master node...
echo

# Ansible presence
echo -n "Testing for Ansible 1.9+...                           "
ANSIBLE_V=/tmp/ansible-version
ansible --version > $ANSIBLE_V 
cat $ANSIBLE_V > $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Vespa requires Ansible 1.9+!"
fi

# Ansible 1.9+
ANSIBLE_MAJOR=$(cat /tmp/ansible-version | cut -d ' ' -f 2 | cut -d '.' -f 1)
ANSIBLE_MINOR=$(cat /tmp/ansible-version | cut -d ' ' -f 2 | cut -d '.' -f 2)
echo $ANSIBLE_MAJOR.$ANSIBLE_MINOR > $OUTPUT
ANSIBLE_MSG="Vespa requires Ansible 1.9+ at the master node!\nConsider installing Ansible using 'sudo pip install ansible'"

if [ $ANSIBLE_MAJOR -lt 1 ]; then
  error_exit "$ANSIBLE_MSG"
elif [ $ANSIBLE_MAJOR -eq 1 -a $ANSIBLE_MINOR -lt 9 ]; then
  error_exit "$ANSIBLE_MSG"
else
  ok_msg
fi

# Parallel presence
echo -n "Testing for parallel...                               "
parallel -V > $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Vespa requires GNU paralell at the master node!"
else
  ok_msg
fi

# Torque server
echo -n "Testing for Torque server...                          "
which pbs_server > $OUTPUT
if [ $? -ne 0 ]; then
  error_exit "Vespa requires Torque server at master node!"
else
  ok_msg
fi

# Torque configuration
echo -n "Testing for Torque configuration...                   "
qstat &> $OUTPUT
if [ $? -ne 0 ]; then
  echo -e '\E[33m'"\033[1m[WARN]\033[0m"
  echo
  >&2 echo "WARNING: Vespa requires Torque to be correctly configured:"
  >&2 qstat
else
  ok_msg
fi

echo
echo Master requirements satisfied!
echo
