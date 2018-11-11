import gatt
import logging
from argparse import ArgumentParser, ArgumentTypeError
import cowdevice
import re

def check_mac(value):
    pattern = re.compile("^((?:[\da-f]{2}[:\-]){5}[\da-f]{2})$", re.IGNORECASE)
    if not pattern.match(value):
         raise ArgumentTypeError("%s is in incorrect format" % value)
    return value

def check_time(value):
    pattern = re.compile("^\d\d:\d\d:\d\d$")
    if not pattern.match(value):
         raise ArgumentTypeError("%s is in incorrect format" % value)
    return value

def check_date(value):
    pattern = re.compile("^\d\d/\d\d/\d\d$")
    if not pattern.match(value):
         raise ArgumentTypeError("%s is in incorrect format" % value)
    return value

def check_adv_interval(value):
    ivalue = int(value)
    if ivalue > 10240:
         raise ArgumentTypeError("%s is larger than maximum of 10240" % value)
    return ivalue

def check_password(value):
    if len(value) > 20:
         raise ArgumentTypeError("%s is too long (max 20 characters)" % value)
    return value

# parser = ArgumentParser(description="Cow device handler")
parser.add_argument('mac_address', type=check_mac, help="MAC address of cowdevice to connect, format: hexdigits separated by colon")
parser.add_argument('-l', '--led', type=int, choices=range(0, 2), help="switch device's led state: 0 -- off, 1 -- on")
parser.add_argument('-t', '--time', type=check_time, help="set device's time, format: HH/MM/SS with leading zero's")
parser.add_argument('-d', '--date', type=check_date, help="set device's date, format: DD/MM/YY with leading zero's")
parser.add_argument('-p', '--txpower', choices=[4, 3, 0, -4, -8, -12, -16, -20, -40], help="set device's TxPower in dBm")
parser.add_argument('-a', '--adv_interval', type=check_adv_interval, help="set device's adv_interval in ms, max 10240")
parser.add_argument('-s', '--switch', type=int, choices=range(0, 3), help="switch device's state: 0 -- off, 1 -- normal mode, 2 -- allways run")
parser.add_argument('-p', '--password', type=str, help="provide password, max 20 len")
# args = parser.parse_args()
# print(args)

# args = parser.parse_args()
# print(args)
mac = "ca:2c:83:fe:72:48"
print("Connecting...")

manager = gatt.DeviceManager(adapter_name='hci0')

device = cowdevice.CowDevice(manager=manager, mac_address=mac)
device.connect()

manager.run()