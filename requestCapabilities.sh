#!/bin/bash

API_KEYS=$(grep -i API_Key /etc/cups/printNode.yml |  cut -d':' -f2-)

while IFS= read -r line; do
  if [ -n "${line}" ] ; then
    curl -sS https://api.printnode.com/printers -u ${line}: | \
      jq '.[] | { id: .id, name: .name, InputTrays: .capabilities.bins, color: .capabilities.color, duplex: .capabilities.duplex }'
  fi
done <<< "${API_KEYS}"
