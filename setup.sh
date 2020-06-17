#!/bin/bash

set -euo pipefail

scriptDir="/usr/local/bin/printnode/"
mkdir -p "${scriptDir}"

cp printnode /usr/lib/cups/backend/
chmod 755 /usr/lib/cups/backend/printnode

echo "Copying configfile to /etc/cups/printNode.yml"
cp printNode.yml /etc/cups/
chmod 600  /etc/cups/printNode.yml
chown lp:lp /etc/cups/printNode.yml

echo "Copying scripts to ${scriptDir}"
cp requestCapabilities.sh "${scriptDir}"
chmod 755 "${scriptDir}/requestCapabilities.sh"
cp generate_printnode_queue.py "${scriptDir}"
chmod 755 "${scriptDir}/generate_printnode_queue.py"

touch /var/log/cups/printnode_log
chown lp:lp /var/log/cups/printnode_log
chmod 644 /var/log/cups/printnode_log

cp printnode.ppd /usr/share/cups/model/
chmod 644 /usr/share/cups/model/printnode.ppd

echo "Installation executed sucessfully"
