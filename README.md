# lh2ctrl
## Power management of Valve v2 lighthouses over Bluetooth LE

This project is mimicking the original [`lhctrl` project](https://github.com/risa2000/lhctrl), which dealt with v1 lighthouses. It is based on the work @nouser2013 did on [Pimax forum thread](https://community.openmr.ai/t/how-to-power-off-basestations-remotely-solved/15205). He also made a Windows implementation of the ideas [here on GitHub](https://github.com/nouser2013/lighthouse-v2-manager/). The difference between this project and the one above is that this project is targeting linux platform and uses the same BT LE Python interface as the original `lhctrl` did.

### BT LE protocol simplified ###
While v1 lighthouses used a quite convoluted protocol to keep the lighthouse running the v2 lighthouses are much simpler. Using BT LE GATT protocol, one just needs to write zero or one to one particular characteristics (**00001525-1212-efde-1523-785feabcd124**) in order to either power on or off the lighthouse.

### Solution
The implemented solution [lh2ctrl.py](/pylhctrl/lh2ctrl.py) uses Python `bluepy` package to access `bluez` BT LE API. The script writes to a particular characteristic to start or stop the lighthouse.

#### Usage
```
usage: lh2ctrl.py [-h] [-g GLOBAL_TIMEOUT] [-i INTERFACE]
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
