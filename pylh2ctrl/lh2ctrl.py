"""
Valve v2 lighthouse power management over BT LE
"""

# external libs
from bluepy import btle

# standard imports
import signal
import sys
import time
from functools import partial

#   globals
#-------------------------------------------------------------------------------
# return error code
EXIT_OK = 0
EXIT_ERR = -1
# verbosity level INFO
INFO   = 1
# LHv2 GATT service
LHV2_GATT_SERVICE_UUID = btle.UUID('00001523-1212-efde-1523-785feabcd124')
LHV2_GATT_CHAR_POWER_CTRL_UUID = btle.UUID('00001525-1212-efde-1523-785feabcd124')
LHV2_GATT_CHAR_MODE_UUID = btle.UUID('00001524-1212-efde-1523-785feabcd124')
# Power management
POWER_ON = b'\x01'
POWER_OFF = b'\x00'

#   defaults
#-------------------------------------------------------------------------------
TRY_COUNT       = 5
TRY_PAUSE       = 2
GLOBAL_TIMEOUT  = 0

#   LHV2 class
#-------------------------------------------------------------------------------
class LHV2:
    """LHv2 abstraction."""
    def __init__(self, macAddr, hciIface, verbose = 0):
        """Connect to the BTLE server in LHv2."""
        self.dev = btle.Peripheral()
        self.macAddr = macAddr
        self.hciIface = hciIface
        self.verbose = verbose
        self.services = None
        self.characteristics = None
        self.name = None

    def connect(self, try_count, try_pause):
        """Connect to LH, try it `try_count` times."""
        while True:
            try:
                if (self.verbose >= INFO):
                    print(f'Connecting to {self.macAddr} at {time.asctime()} -> ', end='')
                self.dev.connect(self.macAddr, iface=self.hciIface, addrType=btle.ADDR_TYPE_RANDOM)
                if (self.verbose >= INFO):
                    print(self.dev.getState())
                break
            except btle.BTLEDisconnectError as e:
                if try_count <= 1:
                    raise e
                if (self.verbose >= INFO):
                    print(e)
                try_count -= 1
                time.sleep(try_pause)
                continue
            except:
                raise
        # initialize the device topology only at the first connect
        # services are not needed at the moment
        #if self.services is None: 
        #    self.services = self.dev.discoverServices()
        if self.characteristics is None:
            chars = self.dev.getCharacteristics()
            self.characteristics = dict([(c.uuid, c) for c in chars])
        if self.name is None:
            self.name = self.getCharacteristic(btle.AssignedNumbers.device_name).read().decode()
        if self.verbose >= INFO:
            mode = self.getCharacteristic(LHV2_GATT_CHAR_MODE_UUID).read()
            print(f'Connected to {self.name} ({self.dev.addr}, mode={mode.hex()})')

    def disconnect(self):
        if self.verbose >= INFO:
            print(f'Diconnecting from {self.name} at {time.asctime()}')
            self.dev.disconnect()

    def getCharacteristic(self, uuid):
        return self.characteristics[uuid]

    def writeCharacteristic(self, uuid, val):
        charc = self.getCharacteristic(uuid)
        charc.write(val, withResponse=True)
        if self.verbose >= INFO:
            print(f'Writing {val.hex()} to {charc.uuid.getCommonName()}')

    def getName(self):
        return self.name

    def powerOn(self):
        self.writeCharacteristic(LHV2_GATT_CHAR_POWER_CTRL_UUID, POWER_ON)

    def powerOff(self):
        self.writeCharacteristic(LHV2_GATT_CHAR_POWER_CTRL_UUID, POWER_OFF)

#   functions
#-------------------------------------------------------------------------------
def wait(secs, verb=0):
    if secs != 0:
        if (verb >= INFO):
            print(f'Sleeping for {secs} sec ... ', end='', flush=True)
        time.sleep(secs)
        if (verb >= INFO):
            print('Done!', flush=True)
    else:
        if (verb >= INFO):
            print(f'Sleeping indefinitely', flush=True)
        signal.pause()

def boot(args):
    """Boot the lighthouses."""
    try:
        for mac in args.lh_mac:
            lhv2 = LHV2(mac, args.interface, args.verbose)
            lhv2.connect(args.try_count, args.try_pause)
            if args.verbose >= INFO:
                print(f'Booting up {lhv2.getName()}')
            lhv2.powerOn()
            lhv2.disconnect()
        wait(args.global_timeout, verb=args.verbose)
    except KeyboardInterrupt:
        print()
        print('Keyboard interrupt caught')
        pass

def shutdown(args):
    """Shut down the lighthouses."""
    for mac in args.lh_mac:
        lhv2 = LHV2(mac, args.interface, args.verbose)
        lhv2.connect(args.try_count, args.try_pause)
        if args.verbose >= INFO:
            print(f'Shutting down {lhv2.getName()}')
        lhv2.powerOff()
        lhv2.disconnect()

def sigterm_hndlr(args, sigterm_def, signum, frame):
    """Signal wrapper for the shutdown function."""
    if args.verbose >= INFO:
        print()
        print(f'Signal {repr(signum)} caught.')
    shutdown(args)
    if sigterm_def != signal.SIG_DFL:
        sigterm_def(signum, frame)
    else:
        sys.exit(EXIT_OK)

def main(args):
    """Main runner."""
    signal.signal(signal.SIGTERM, partial(sigterm_hndlr, args, signal.getsignal(signal.SIGTERM)))
    signal.signal(signal.SIGHUP, partial(sigterm_hndlr, args, signal.getsignal(signal.SIGHUP)))
    boot(args)
    shutdown(args)

#   main
#-------------------------------------------------------------------------------
if __name__ == '__main__':

    from argparse import ArgumentParser

    ap = ArgumentParser(description='Wakes up and runs Valve v2 lighthouse(s) using BT LE power management')
    ap.add_argument('lh_mac', type=str, nargs='+', help='MAC address(es) of the lighthouse(s) (in format aa:bb:cc:dd:ee:ff)')
    ap.add_argument('-g', '--global_timeout', type=int, default=GLOBAL_TIMEOUT, help='time (sec) how long to keep the lighthouse(s) alive (0=forever) [%(default)s]')
    ap.add_argument('-i', '--interface', type=int, default=0, help='The Bluetooth interface on which to make the connection to be set. On Linux, 0 means /dev/hci0, 1 means /dev/hci1 and so on. [%(default)s]')
    ap.add_argument('--try_count', type=int, default=TRY_COUNT, help='number of tries to set up a connection [%(default)s]')
    ap.add_argument('--try_pause', type=int, default=TRY_PAUSE, help='sleep time when reconnecting [%(default)s]')
    ap.add_argument('-v', '--verbose', action='count', default=0, help='increase verbosity of the log to stdout')

    args = ap.parse_args()
    main(args)
