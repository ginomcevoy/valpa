#!/bin/bash 

# Outputs the dhcpd.conf for a DHCP server that gives
# IP addresses to all VMs in the virtual cluster
# Author: Giacomo Mc Evoy - giacomo@lncc.br
# LNCC Brazil 2014

# calculate directory local to script
LOCAL_DIR="$( cd "$( dirname "$0" )" && pwd )"
VALPA_DIR=$LOCAL_DIR/..

# Import params
source $VALPA_DIR/params.sh

echo "Building dhcpd.conf file..."

# Output file
OUTPUT=$VALPA_DIR/data-output/dhcpd.conf

# Get the subnet+netmask+router
DHCP_SUBNET=$($VALPA_DIR/networking/address-subnet.sh)
DHCP_NETMASK=$($VALPA_DIR/networking/address-netmask.sh)
DHCP_ROUTER=$($VALPA_DIR/networking/address-router.sh)
DHCP_BROADCAST=$($VALPA_DIR/networking/address-broadcast.sh)

# Perform replacements
cp $VALPA_DIR/templates/dhcpd-conf-template.txt $OUTPUT

sed -i "s/DHCP\_SUBNET/${DHCP_SUBNET}/g" ${OUTPUT} 
sed -i "s/DHCP\_NETMASK/${DHCP_NETMASK}/g" ${OUTPUT} 
sed -i "s/DHCP\_ROUTER/${DHCP_ROUTER}/g" ${OUTPUT} 
sed -i "s/DHCP\_BROADCAST/${DHCP_BROADCAST}/g" ${OUTPUT} 

# Temporary files for VM entry
TEMP_HOSTS=/tmp/valpa-dhcpd.hosts.tmp
TEMP_LINE=/tmp/valpa-dhcpd.line.tmp

rm -f $TEMP_HOSTS

# Iterate physical machines
NODE_INDEX=1
while [ `$VALPA_DIR/util/iterator-nodes.sh $NODE_INDEX` ]; do

	NODE_NUMBER_NONZERO=$($VALPA_DIR/util/iterator-node-numbers.sh $NODE_INDEX 'NONZERO')
	NODE_NUMBER_2=$(printf "%02d\n" ${NODE_NUMBER_NONZERO})

	# Iterate VMs
	for (( VM_INDEX=1; VM_INDEX<=$VM_L; VM_INDEX++ )); do

		# Get VM name
		VM_NAME=`$VALPA_DIR/util/iterator-vm-names.sh $NODE_INDEX $VM_INDEX`
		
		# Build line from template
		cp $VALPA_DIR/templates/dhcpd-conf-entry.txt $TEMP_LINE

		# VM name
		sed -i "s/VM\_NAME/${VM_NAME}/g" ${TEMP_LINE} 

		# VM MAC address
		FORMATTED_INDEX=$(echo $VM_INDEX | awk '{printf "%02d", $0}')
		MAC_SUFFIX="${NODE_NUMBER_2}:$FORMATTED_INDEX"
		VM_MAC="$MAC_BASE:$MAC_SUFFIX"
		sed -i "s/VM\_MAC/${VM_MAC}/g" ${TEMP_LINE} 

		# VM IP address
		VM_IP=$($VALPA_DIR/networking/get-vm-address.sh $NODE_INDEX $VM_INDEX)
		sed -i "s/VM\_IP/${VM_IP}/g" ${TEMP_LINE} 

		cat $TEMP_LINE >> $OUTPUT
	done

	NODE_INDEX=`expr $NODE_INDEX + 1`
done

echo "}" >> $OUTPUT
echo "dhcpd.conf file at $OUTPUT"