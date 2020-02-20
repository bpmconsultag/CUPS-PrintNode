#!/bin/bash

curl -u  $(cat /etc/printNode.conf):  https://api.printnode.com/printers | jq '.[] | { printer: .name, InputTrays: .capabilities.bins, color: .capabilities.color, duplex: .capabilities.duplex }'
