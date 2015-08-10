#!/bin/bash
# Creates a VM from an XML
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2013

# Validate input
if [ $# -lt 2 ]; then
	echo "Create a VM from an XML"
	echo "Usage: $0 <hostname> <xml>"
	exit 1
fi

# Params
HOST=$1
XML=$2

# Call libvirt
echo -e "virsh -c qemu+ssh://$HOST/system create $XML"
virsh -c qemu+ssh://$HOST/system create $XML

# Wait before sending another libvirt request, may prevent VM hangup
sleep 3
