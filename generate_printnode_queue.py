#!/usr/bin/env python3

"""
Script to automatically create CUPS Queue based on PrintNode Printer ID
Input slot are inserted into PPD
"""

# Version history:
# 0.1   15.06.2020  gw  Inital
# 0.2   23.06.2020  gw  Set Printer Desc with lpadmin commmand
# 0.3   30.06.2020  gw  Added custom cups queue description (-d)

# Command line arguments:
# -i PrintNode Printer ID
# -q Target CUPS Queue

import ast
import sys
import subprocess

def print_usage():
    """Info and usage of command line parameters"""
    print("Script to create a CUPS Queue from a PrintNode Printer ID")
    print("InputSlots are automatically injected into the ppd file")
    print("PrintNode Name will be inserted into printer.conf Info field\n")
    print("Usage: generatePPD.py -i {PrinterNode Printer ID} (Required)")
    print("       generatePPD.py -q {CUPS queue to be created/modified} "\
          "(Required)")
    print("       generatePPD.py -d {CUPS queue description}")

PRINTER_ID = None
CUPS_QUEUE = None
PRINTER_DESC = ''

# Validate Params
if len(sys.argv) == 1:
    print_usage()
    sys.exit(0)

for i in range(1, len(sys.argv)):
    try:
        if sys.argv[i] == "-i":
            PRINTER_ID = sys.argv[i + 1]
        if sys.argv[i] == "-q":
            CUPS_QUEUE = sys.argv[i + 1]
        if sys.argv[i] == "-d":
            PRINTER_DESC = sys.argv[i + 1]
        if sys.argv[i] == "--help" or sys.argv[i] == "-h":
            print_usage()
            sys.exit(0)
    except IndexError:
        sys.stderr.write("Error: Wrong number of parameters specified\n\n")
        print_usage()
        sys.exit(1)

if PRINTER_ID is None or CUPS_QUEUE is None:
    sys.stderr.write("Error: Wrong number of parameters specified\n\n")
    print_usage()
    sys.exit(2)

try:
    PRINTER_ID_INT = int(PRINTER_ID)
except ValueError:
    sys.stderr.write("Please specify PrintNode Printer ID as first parameter " \
        "Parameter was no valid Int\n\n")
    print_usage()
    sys.exit(3)

# Global vars
PPD_PATH = "/etc/cups/ppd/%s.ppd" % CUPS_QUEUE
LPADMIN = "/usr/sbin/lpadmin"
PRINTER_CONF_PATH = "/etc/cups/printers.conf"
REQUEST_CAPABILITES_SCRIPT = "/usr/local/bin/printnode/requestCapabilities.sh"

# Fetch all printers capabilities
try:
    RESPONSE = subprocess.run("%s" % REQUEST_CAPABILITES_SCRIPT,
                              check=True, stdout=subprocess.PIPE)
except subprocess.CalledProcessError as ex:
    print("requestCapabilities.sh script failed with the following output:")
    print("%s" % ex)
    sys.exit(4)

# Generate Capabilities array
CAPABILITIES = RESPONSE.stdout.decode('utf-8').replace("'", '"')
CAPABILITIES = CAPABILITIES.split("\n")

PARSING_CONFIG = False
PRINTER_CAPABILITIES_LIST = []

# Preperate capabilities list
for line in CAPABILITIES:
    if PARSING_CONFIG:
        if line != "}":
            PRINTER_CAPABILITIES_LIST.append(line)
        else:
            break

    if "\"id\"" in line:
        PARSING_CONFIG = PRINTER_ID in line

if not PRINTER_CAPABILITIES_LIST:
    sys.stderr.write("Error: Could not find Printer." \
      " Ensure the printer ID is correct\n\n")
    print_usage()
    sys.exit(5)

# Generate capabilities dict
def prepare_values(value):
    """ Format strings of PrintNode capabilities to only contain values """
    return value[value.index(":"):].replace(",", "").replace(": ", \
        "").replace('"', "")

PRINTER_CAPABILITIES_DICT = {}
READING_INPUT_SLOTS = False
INPUT_SLOTS = ""
for line in PRINTER_CAPABILITIES_LIST:
    if "]," in line:
        PRINTER_CAPABILITIES_DICT["InputSlots"] = INPUT_SLOTS
        READING_INPUT_SLOTS = False

    # Reading input slot and replace spaces with underscores
    if READING_INPUT_SLOTS:
        if INPUT_SLOTS == "":
            INPUT_SLOTS = "%s" % \
              line[line.index('"'):].replace(" ", "_")
        else:
            INPUT_SLOTS = "%s %s" % (INPUT_SLOTS, \
              line[line.index('"'):].replace(" ", "_"))

    if "\"name\"" in line:
        if not PRINTER_DESC:
            PRINTER_DESC = prepare_values(line)
    elif "\"InputTrays\"" in line:
        READING_INPUT_SLOTS = True

print("Capabilities found!")

# Create queue
print("Creating queue: %s" % CUPS_QUEUE)
try:
    subprocess.run(["%s" % LPADMIN, "-p", "%s" % CUPS_QUEUE,
                    "-E", "-v", "printnode://%s" % PRINTER_ID, "-m", "printnode.ppd",
                    "-D", "%s" % PRINTER_DESC],
                   check=True)
except subprocess.CalledProcessError as ex:
    print("lpadmin command failed with the following output:")
    print("%s" % ex)
    sys.exit(6)

with open("%s" % PPD_PATH, "r") as PPD_FILE:
    PPD_DATA = PPD_FILE.readlines()

INPUT_SLOTS = ast.literal_eval("[ %s ]" % PRINTER_CAPABILITIES_DICT["InputSlots"])

# Inject InputSlot definitions into PPD file
MODIFIED_PPD_DATA = ""
INPUT_SLOT_WRITTEN = False
for line in PPD_DATA:
    if "*InputSlot " in line and not INPUT_SLOT_WRITTEN:
        print("Writing InputSlot Definitons to PPD")
        for input_slot in INPUT_SLOTS:
            MODIFIED_PPD_DATA += "*InputSlot %s/%s: \"\"\n" \
              % (input_slot, input_slot)
        INPUT_SLOT_WRITTEN = True
    elif "*DefaultInputSlot" in line:
        MODIFIED_PPD_DATA += "*DefaultInputSlot: %s\n" % INPUT_SLOTS[0]
    else:
        MODIFIED_PPD_DATA += line

with open("%s" % PPD_PATH, "w") as PPD_FILE:
    PPD_FILE.write(MODIFIED_PPD_DATA)
