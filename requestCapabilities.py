#!/usr/bin/env python3

# Get Capabilities of all Printers of the given Account in PrintNode.yaml

# Version history:
# 1.0    26.08.2022  bl  Initial version
# 1.1    31.08.2022  bl  Added error msg when the Account doesnt exist

import sys
import argparse
import json
import yaml
from printnodeapi import Gateway

"""
Parse command line arguments
"""
PARSER = argparse.ArgumentParser(
    description='Get Capabilities of all Printers of the given Account in PrintNode.yaml')
PARSER.add_argument(
    '-A',
    dest='INPUT_ACC',
    type=str,
    help='Which Account to use')
ARGS = PARSER.parse_args()
ACCOUNT = ARGS.INPUT_ACC
# load YAML data from the file
PRINTNODE_YML_PATH = "/etc/cups/printNode.yml"

ALL_API_KEYS = {}
with open(PRINTNODE_YML_PATH) as PRINTNODE_YML_FILE:

    PRINTNODE_DICT = yaml.safe_load(PRINTNODE_YML_FILE)

    for KEY, VALUE in enumerate(PRINTNODE_DICT):
        if "Account" in VALUE and "API_Key" in VALUE:
            ALL_API_KEYS[VALUE["Account"]] = VALUE["API_Key"]


if ACCOUNT:
    API_KEY_TO_QUERY = [ALL_API_KEYS[ACC]
                        for ACC in ALL_API_KEYS if ACC == ACCOUNT]
else:
    API_KEY_TO_QUERY = [ALL_API_KEYS[ACC] for ACC in ALL_API_KEYS]

if not API_KEY_TO_QUERY:
    print("Given Account does not exist")
    sys.exit()

JSON_DICT = {}
for API_KEY in API_KEY_TO_QUERY:
    GATEWAY = Gateway(url='https://api.printnode.com', apikey=API_KEY)
    for printer in GATEWAY.printers():
        JSON_DICT[printer.id] = {
            "computer": printer.computer.name,
            "name": printer.name,
            "InputTrays": printer.capabilities.bins,
            "color": printer.capabilities.color,
            "duplex": printer.capabilities.duplex
        }
# convert into JSON:
print(json.dumps(JSON_DICT, indent=2))
