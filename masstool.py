#!/usr/bin/env python3

from argparse import ArgumentParser
import gatt
import time
import subprocess
import os


class CDManager(gatt.DeviceManager):
    """
    An implementation of ``gatt.DeviceManager`` that discovers any GATT device
    and prints all discovered devices.
    """
    def __init__(self, devices_to_process, devices_processed, cmd, timeout, on_success, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.devices_to_process = devices_to_process
        self.devices_processed = devices_processed
        self.cmd = cmd
        self.timeout = timeout
        self.on_success = on_success
        self.try_again_later_set = set()

    def execute(self, mac):
        cmd = self.cmd.format(mac=mac) if '{mac}' in self.cmd else self.cmd
        print('Executing command: %s' % cmd)
        try:
            result = subprocess.run(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            print('TIMEOUT %s' % mac) 
            return 42
        returncode = result.returncode
        stdout = result.stdout.decode('ascii', 'replace')
        stderr = result.stderr.decode('ascii', 'replace')
        print ('retc:<%s> stdout:<%s> stderr:<%s>' % (returncode, stdout, stderr))
        return returncode

    def print_left_devices(self):
        totalcnt = len(self.devices_to_process)
        lcnt = len(self.devices_processed)
        ldevices = self.devices_to_process - self.devices_processed
        print ("DONE %s/%s" % (lcnt, totalcnt))

    def device_discovered(self, device):
        # check stop condition
        if self.devices_to_process == self.devices_processed:
            print('ALL DEVICES PROCESSED, EXITING')
            self.stop_discovery()
            self.stop()
            return

        mac = device.mac_address
        alias = device.alias()

        # skip if not in devices to process
        if mac not in self.devices_to_process:
            return

        # skip if already processed
        if mac in self.devices_processed:
            print("[%s](%s) DONE" % (mac, alias))
            return

        # remove from try_again_later_set and skip
        if mac in self.try_again_later_set:
            print("[%s](%s) IN TRY AGAIN LATER SET SKIPPING..." % (mac, alias))
            self.try_again_later_set.remove(mac)
            return

        print("[%s](%s) PROCESSING..." % (mac, alias))
        print('[%s](%s) EXECUTE COMMAND' % (mac, alias))
        rcode = self.execute(mac)
        if rcode != 0:
            print('[%s](%s) FAILED!' % (mac, alias))
            self.try_again_later_set.add(mac)
        else:
            print('[%s](%s) SUCCEDED!' % (mac, alias))
            self.devices_processed.add(mac)
            self.on_success(mac)

        self.print_left_devices()

def load_macs(fname):
    if fname is None:
        return set()
    
    if not os.path.exists(fname):
        with open(fname, 'w') as f:
            pass

    with open(fname, 'r') as f:
        macs = set([l.strip() for l in f.readlines()])

    return macs


def main():
    arg_parser = ArgumentParser(description="Mass gatt CD change")
    arg_parser.add_argument(
        '--adapter',
        default='hci0',
        help="Name of Bluetooth adapter, defaults to 'hci0'")
    arg_parser.add_argument(
        '--devices-to-process',
        required=True,
        help="List of mac addresses of devices to process")
    arg_parser.add_argument(
        '--devices-processed',
        required=True,
        help="List of already processed mac addresses of devices")
    arg_parser.add_argument(
        '--cmd',
        required=True,
        help="""Cmd to be executed for each device, 
        if cmd return code is not equal to 0 then cmd is considered failed 
        and will be executed again, under tag {mac} will be passed current devices mac""")
    arg_parser.add_argument(
        '--timeout',
        default=30,
        type=int,
        help="""Maximum time for command to execute, after that command is considered to be failed""")
    args = arg_parser.parse_args()

    devices_to_process = load_macs(args.devices_to_process)
    devices_processed = load_macs(args.devices_processed)

    def on_success(mac):
        if not args.devices_processed:
            return 
        with open(args.devices_processed, 'a+') as f:
            f.write('%s\n' % mac)

    device_manager = CDManager(
        adapter_name='hci0', 
        devices_to_process=devices_to_process,
        devices_processed=devices_processed,
        cmd=args.cmd,
        timeout=args.timeout,
        on_success=on_success)
        
    device_manager.print_left_devices()
    device_manager.start_discovery()

    print("Terminate with Ctrl+C")
    try:
        device_manager.run()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
