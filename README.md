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
1. Perform all prerequisites
2. git clone https://github.com/bpmconsultag/CUPS-PrintNode.git
3. cd CUPS-PrintNode
4. ./setup.sh
5. Add your Print_API key to /etc/cups/printNode.yml (You may add additonal accounts)
6. /usr/local/bin/printnode/requestCapabilities.sh
7. Note the ID of the desired printer
8. /usr/local/bin/printnode/generate_printnode_queue.py -i {Printer ID} -q {Destination CUPS Queue}

The script generate_printnode_queue.py will automatically generate CUPS Queue using the generic PrintNode PPD and inserting the Name of the inputSlots into it.

## printNode.yml configuration parameters  (see printNode.yml for examples)
Account: Account Descripton

API_Key: PrintNode API Key

Printers: IDs of printers belonging to this account

A5_Printer: Alternative queue for A5 Prints (Will be used always if the document is A5)

Override_Options: Allows override options. Options set below this will always override anything set previously

Printer_ID: ID of the printer for which overrides will take effect

A5_Bin: Override option: Bin for A5 Paper

A5_Rotation: Override option: Rotation for A5 Prints

A5_Duplex: Override option: Duplex for A5

Duplex: Override option: Duplex globally (If set together with A5_Duplex, A5_Duplex will be prefered for A5 prints because it is more specific)

## Additional Information
CUPS-PrintNode stores a logfile in /var/log/cups/printnode_log

## Futrther Ressources:
https://www.printnode.com/en/docs/api/curl

https://github.com/PrintNode/PrintNode-Python
