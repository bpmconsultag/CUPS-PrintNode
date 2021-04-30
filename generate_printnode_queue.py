#!/usr/bin/env python3

"""
Script to automatically create CUPS Queue based on PrintNode Printer ID
Input slot are inserted into PPD
"""

# Version history:
# 0.1   15.06.2020  gw  Inital
# 0.2   23.06.2020  gw  Set Printer Desc with lpadmin commmand
# 0.3   30.06.2020  gw  Added custom cups queue description (-d)
# 1.0   23.10.2020  gw  Added manipulation of vendor ppd
# 1.1   13.04.2021  gw  Generation of queues without ppd and add dummy InputSlot if Printer has none

import argparse
import re
import subprocess
import sys
import yaml
from printnodeapi import Gateway

# Parse Arguments
ARGPARSER = argparse.ArgumentParser(description="Generate CUPS Queue from PrintNode PrinterID")
ARGPARSER.add_argument("-i", "--id", required=True, type=int, help="PrintNode Printer ID")
ARGPARSER.add_argument("-q", "--queue", required=True, help="CUPS Queue name to be created")
ARGPARSER.add_argument("-m", "--model", required=False, default="printnode.ppd", help="Printer "\
 "Model (See available Models in /usr/share/cups/model) The value of this must end with \".ppd\"."\
 "For raw queues use \"-m raw\". In this case no ppd will be created")
ARGPARSER.add_argument("-d", "--desc", required=False, default="PrintNode printer",
                       help="Description if CUPS Queue")
ARGUMENTS = vars(ARGPARSER.parse_args())

# Global vars
LPADMIN = "/usr/sbin/lpadmin"
PRINTNODE_CONFIG_PATH = "/etc/cups/printNode.yml"
PRINTER_CONF_PATH = "/etc/cups/printers.conf"
API_KEYS = []
PRINTER_ID = ARGUMENTS["id"]
CUPS_QUEUE = ARGUMENTS["queue"]
PRINTER_DESC = ARGUMENTS["desc"]
MODEL = ARGUMENTS["model"]
PPD_PATH = "/etc/cups/ppd/%s.ppd" % CUPS_QUEUE

# Get API keys
try:
    with open("%s" % PRINTNODE_CONFIG_PATH, "r") as PRINTNODE_CONFIG_FILE:
        PRINTNODE_CONFIG = yaml.safe_load(PRINTNODE_CONFIG_FILE)
except yaml.YAMLError as ex:
    sys.stderr.write("Error: Could not parse yaml config file: %s" % (PRINTNODE_CONFIG_PATH))
    sys.exit(1)
except IOError:
    sys.stderr.write("Error: Could not read config file: %s" % (PRINTNODE_CONFIG_PATH))
    sys.exit(2)

# Get all API Keys from printNode.yml
for ACCOUNT in PRINTNODE_CONFIG:
    API_KEY = ACCOUNT.get("API_Key", "")
    if API_KEY:
        API_KEYS.append(API_KEY)

# Get printer settings
for API_KEY in API_KEYS:
    try:
        PRINTNODE_GW = Gateway(url="https://api.printnode.com", apikey="%s" % API_KEY)
        PRINTER_PROPERTIES = PRINTNODE_GW.printers(printer=int(PRINTER_ID))
    except LookupError:
        pass

INPUT_SLOTS = PRINTER_PROPERTIES[4][0]

# Create queue
print("Creating queue: %s" % CUPS_QUEUE)
try:
    if MODEL == "raw":
        subprocess.run(["%s" % LPADMIN, "-p", "%s" % CUPS_QUEUE, "-E",
                        "-v", "printnode://%s" % PRINTER_ID,
                        "-D", "%s" % PRINTER_DESC],
                       check=True)
    else:
        subprocess.run(["%s" % LPADMIN, "-p", "%s" % CUPS_QUEUE,
                        "-E", "-v", "printnode://%s" % PRINTER_ID, "-m", "%s" % MODEL,
                        "-D", "%s" % PRINTER_DESC],
                       check=True)
except subprocess.CalledProcessError as ex:
    print("lpadmin command failed with the following output:")
    print("%s" % ex)
    sys.exit(3)

if MODEL != "raw":
    with open("%s" % PPD_PATH, "r") as PPD_FILE:
        PPD_DATA = PPD_FILE.readlines()

    # Inject InputSlot definitions into PPD file
    MODIFIED_PPD_DATA = ""
    INPUT_SLOTS_WRITTEN = False
    for line in PPD_DATA:

        if re.match(r"^\*InputSlot", line) is not None:

            # don't write inputSlot definitions if no are in printNode capabilities
            if not INPUT_SLOTS:
                continue

            if not INPUT_SLOTS_WRITTEN:
                print("Writing InputSlot Definitons to PPD")
                for INPUT_SLOT in INPUT_SLOTS:
                    # Replace spaces with underscores to allow cups to handle inputSlots
                    # The CUPS-Backend will replace underscores with spaces
                    PREPPED_INPUT_SLOT = INPUT_SLOT.replace(" ", "_")
                    MODIFIED_PPD_DATA += "*InputSlot %s/%s: \"\"\n" % (PREPPED_INPUT_SLOT,
                                                                       INPUT_SLOT)
                INPUT_SLOTS_WRITTEN = True

            # If INPUT_SLOTS were already written skip original definitions
            else:
                continue

        elif "*DefaultInputSlot" in line:
            if INPUT_SLOTS:
                MODIFIED_PPD_DATA += "*DefaultInputSlot: %s\n" % INPUT_SLOTS[0]
            # Write dummy slot to ppd if there are no definitions in printNode capabilities
            else:
                MODIFIED_PPD_DATA += "*DefaultInputSlot: Auto\n"
                MODIFIED_PPD_DATA += "*InputSlot Auto/Auto: \"\"\n"
        else:
            MODIFIED_PPD_DATA += line

    # Write manipulated PPD Data
    with open("%s" % PPD_PATH, "w") as PPD_FILE:
        PPD_FILE.write(MODIFIED_PPD_DATA)

print("Restarting CUPS")
try:
    subprocess.run(["service", "cups", "restart"], check=True)
except subprocess.CalledProcessError as ex:
    print("CUPS failed to restart with the following error: %s" % ex)
    print("See \"service cups status\" or /var/log/cups/error_log")
