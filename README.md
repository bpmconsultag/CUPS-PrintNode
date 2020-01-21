# CUPS-PrintNode
CUPS backend enabling printing through the PrintNode Cloud.

## Prerequisites
* python3 python3-requests python3-future
* CUPS
* PrintNode-Python https://github.com/PrintNode/PrintNode-Python
* PrintNode Account
* Client with Installed PrintNode Agent

## Installation
1. Move printnode to /usr/lib/cups/backend/printnode
2. Get API Key from https://printnode.com
3. Write API Key to /etc/printNode.conf
4. Get Printer ID from https://app.printnode.com/devices
5. Add CUPS queue like the following: 

``` lpadmin -p {PRINTER NAME} -E -v printnode://{PRINTNODE PRINTER ID} -P {PATH TO PPD} ```
  
## Capabilities
CUPS-PrintNode supports printing from different Trays. In order for these to Work the name of the InputSlots must be adjusted to the InputSlots name in PrintNode. 

### Requesting printer capabilities 
The printer's capabilites can be requested with a curl command:

**Note:** The API key must be terminated with a colon.

``` curl https://api.printnode.com/printers -u {PrintNode API key}: | less ```

**Note:** Depending on the language which the PrintNode agent was installed as the name of the InputSlots can be different. In some Cases the InputSlot definition of PrintNode contain spaces. CUPS is not able to handle spaces in the name of an InputSlot. So if that is the case the spaces in the PPD File must be replaced with a underscore as seen in the example following:

Printer=HP LaserJet MFP M426dw

Vendor PPD:
```
*InputSlot Tray1/Tray 1: "<</MediaPosition 3 /ManualFeed false>> setpagedevice"
*InputSlot Tray2/Tray 2: "<</MediaPosition 0 /ManualFeed false>> setpagedevice"
*InputSlot Tray3/Tray 3: "<</MediaPosition 1 /ManualFeed false>> setpagedevice"
*InputSlot ManualFeed/Manual Feed: "<</MediaPosition 3 /ManualFeed true>> setpagedev
InputSlot definition in PPD:
```

PrintNode Capabilities InputSlot:
```
 "capabilities": {
      "bins": [
        "Auto Select",
        "Manual Feed",
        "Tray 1",
        "Tray 2",
        "Tray 3"
      ],
....
```

Now the PPD must be adjusted to match the following so the InputSlots are the same in the PPD and the PrintNode cloud. The following is desired:

Adjusted PPD:
```
*InputSlot Tray_1/Tray 1: "<</MediaPosition 3 /ManualFeed false>> setpagedevice"
*InputSlot Tray_2/Tray 2: "<</MediaPosition 0 /ManualFeed false>> setpagedevice"
*InputSlot Tray_3/Tray 3: "<</MediaPosition 1 /ManualFeed false>> setpagedevice"
*InputSlot Manual_Feed/Manual Feed: "<</MediaPosition 3 /ManualFeed true>> setpagedev
InputSlot definition in PPD:
```

## Additional Information
CUPS-PrintNode stores a logfile in /var/log/cups/printnode_log
