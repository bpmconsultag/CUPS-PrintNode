#!/bin/bash

API_KEYS=$(grep -i API_Key /etc/cups/printNode.yml | cut -d':' -f2- | grep -v "''" | grep -v '""')

while IFS= read -r line; do
  if [ -n "${line}" ] ; then 
    curl -sS https://api.printnode.com/printers -u ${line}: | \
      jq '.[] | { computer: .computer.name, id: .id, name: .name, InputTrays: .capabilities.bins, color: .capabilities.color, duplex: .capabilities.duplex }'
  fi
done <<< "${API_KEYS}"
