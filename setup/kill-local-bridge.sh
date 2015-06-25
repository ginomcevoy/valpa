# Kill virtual bridge locally
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VESPA_DIR=$LOCAL_DIR/..

# Name of bridge
VESPA_BRIDGE=$NET_VALUE

kill `cat /var/run/libvirt/network/${VESPA_BRIDGE}.pid`
sudo ifconfig br0 down
sudo brctl delbr br0
