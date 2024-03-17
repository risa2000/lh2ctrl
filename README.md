# lh2ctrl
## Power management of Valve v2 lighthouses over Bluetooth LE

This project is mimicking the original [`lhctrl` project](https://github.com/risa2000/lhctrl), which dealt with v1 lighthouses. It is based on the work @nouser2013 did on [Pimax forum thread](https://community.openmr.ai/t/how-to-power-off-basestations-remotely-solved/15205). He also made a Windows implementation of the ideas [here on GitHub](https://github.com/nouser2013/lighthouse-v2-manager/). The difference between this project and the one above is that this project is targeting linux platform and uses the same BT LE Python interface as the original `lhctrl` did.

### BT LE protocol simplified ###
While v1 lighthouses used a quite convoluted protocol to keep the lighthouse running the v2 lighthouses are much simpler. Using BT LE GATT protocol, one just needs to write zero or one to one particular characteristics (**00001525-1212-efde-1523-785feabcd124**) in order to either power on or off the lighthouse.

### Solution
The implemented solution [lh2ctrl.py](/pylhctrl/lh2ctrl.py) uses Python `bluepy` package to access `bluez` BT LE API. The script writes to a particular characteristic to start or stop the lighthouse.

#### Installing Bluepy in a Python virtual environment (`venv`)
If your distro requires that you install and use `bluepy` in a Python virtual environment (`venv`), you can use this example about how to do it:

```bash
python3 -m venv $HOME/.venvs/bluepy
source $HOME/.venvs/bluepy/bin/activate
pip install bluepy
```
Then remember to activate the `bluepy` `venv` every time before using this tool:
```bash
source $HOME/.venvs/bluepy/bin/activate
```

#### Usage
```
usage: lh2ctrl.py [-h] [-g GLOBAL_TIMEOUT | --on | --off] [-i INTERFACE]
                  [--try_count TRY_COUNT] [--try_pause TRY_PAUSE] [-v]
                  lh_mac [lh_mac ...]

Wakes up and runs Valve v2 lighthouse(s) using BT LE power management

positional arguments:
  lh_mac                MAC address(es) of the lighthouse(s) (in format
                        aa:bb:cc:dd:ee:ff)

optional arguments:
  -h, --help            show this help message and exit
  -g GLOBAL_TIMEOUT, --global_timeout GLOBAL_TIMEOUT
                        time (sec) how long to keep the lighthouse(s) alive
                        (0=forever) [0]
  --on                  just switch the devices on and stop
  --off                 just switch the devices off and stop
  -i INTERFACE, --interface INTERFACE
                        The Bluetooth interface on which to make the
                        connection to be set. On Linux, 0 means /dev/hci0, 1
                        means /dev/hci1 and so on. [0]
  --try_count TRY_COUNT
                        number of tries to set up a connection [5]
  --try_pause TRY_PAUSE
                        sleep time when reconnecting [2]
  -v, --verbose         increase verbosity of the log to stdout
  ```
  
#### Usage example
You can use some other BT or BTLE tools (e.g. `blescan` or `bluetoothctl`) to figure out the corresponding MACs for your lighthouses (LHs):
```bash
bluetoothctl scan on
```
Look for LHB-XXXXXXXX:
```
[NEW] Device F4:7F:AD:38:CA:A2 LHB-D20A32D4
[NEW] Device A5:03:4A:3E:84:E3 LHB-B03C2E25
```
Turn on and off:
```bash
./lh2ctrl.py --on F4:7F:AD:38:CA:A2 A5:03:4A:3E:84:E3
./lh2ctrl.py --off F4:7F:AD:38:CA:A2 A5:03:4A:3E:84:E3
```
Without `--on` or `--off`, the stations will stay on until you stop the script. Use `-g` to specify a timeout after which the script will stop automatically.

You can wrap this script execution in a shell script (and if you are using `venv` add its activation as well):
```bash
#!/bin/bash
source $HOME/.venvs/bluepy/bin/activate
<full_path>/lh2ctrl.py -v $1 F4:7F:AD:38:CA:A2 A5:03:4A:3E:84:E3
```
Save it somewhere in your `$PATH` as e.g. `vr-base-stations` and then use it as
```bash
vr-base-stations --on
```
#### Usage with SteamVR
To start and stop the base stations automatically with SteamVR, just change the `SteamVR` binary _launch options_ to
```bash
vr-base-stations --on & %command%; vr-base-stations --off
```
(where `vr-base-stations` is the previously created script, assuming it is available in your `$PATH`)

### Troubleshooting
#### BT signal strength
If you cannot find your LHs in the scan, or the scanned signal strength is low (RSSI < ~ -80 dBm), you might need to attach an additional antenna to improve your radio communication. This could happen on a PC motherboard with an integrated Bluetooth interface, or RPi in a shielded case, or in RPi model 4+ with an integrated USB 3.0, where the USB 3.0 heavy traffic can also be a source of a strong interference.
