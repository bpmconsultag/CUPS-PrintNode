# CUPS-PrintNode
CUPS backend enabling printing through the PrintNode Cloud.

## Prerequisites
* packages: python3 python3-requests python3-future jq cups
* python packages: yaml 
* CUPS
* PrintNode-Python https://github.com/PrintNode/PrintNode-Python
* PrintNode Account
* Client with Installed PrintNode Agent

## Installation
1: Perform all prerequisites

2: git clone https://github.com/bpmconsultag/CUPS-PrintNode.git

3: cd CUPS-PrintNode

4: ./setup.sh

3: /usr/local/bin/printnode/requestCapabilities.sh

4: Note the ID of the desired printer

5: /usr/local/bin/printnode/generate_printnode_queue.py -i {Printer ID} -q {Destination CUPS Queue}

The script generate_printnode_queue.py will automatically generate CUPS Queue using the generic PrintNode PPD and inserting the Name of the inputSlots into it.

## Additional Information
CUPS-PrintNode stores a logfile in /var/log/cups/printnode_log

## Futrther Ressources:
https://www.printnode.com/en/docs/api/curl
https://github.com/PrintNode/PrintNode-Python
