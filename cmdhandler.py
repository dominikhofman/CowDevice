import logging
import re 
from argparse import ArgumentTypeError
from characteristicsmenager import CharacteristicsMenager

def check_mac(value):
    pattern = re.compile("^((?:[\da-f]{2}[:\-]){5}[\da-f]{2})$", re.IGNORECASE)
    if not pattern.match(value):
         raise ArgumentTypeError("%s is in incorrect format" % value)
    return value
class PasswordRequiredException(Exception):
    pass


class CmdHandler(object):
    """
    generate characteristics based on config file and command line arguments
    """
    def __init__(self, menager, parser):
        self.characteristics_menager = menager
        self.parser = parser
        self.logger = logging.getLogger('console')


    def add_arguments(self):
        self.parser.add_argument('mac_address', type=check_mac, 
            help="MAC address of cowdevice to connect, format: hexdigits separated by colon or dash")
        
        self.parser.add_argument('-r', '--read-all', action='store_true', dest='read_all',
            help="read all specified in services.yml characteristics")

        self.parser.add_argument('--adapter-name', dest='adapter_name', default="hci0",
            help="bluetooth adapter name, default hci0")

        self.characteristics_menager.password.add_argument(self.parser)

        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('-v', action='store_const', const=logging.WARN, dest='verbosity', help='Warning')
        group.add_argument('-vv', action='store_const', const=logging.INFO, dest='verbosity', help='Info')
        group.add_argument('-vvv', action='store_const', const=logging.DEBUG, dest='verbosity', help='Debug')

        for characteristic in self.characteristics_menager.values():
            characteristic.add_argument(self.parser)
    
    def parse_args(self):
        args = self.parser.parse_args()
        self.set_verbosity(args.verbosity)
        self.mac_address = args.mac_address
        self.adapter_name = args.adapter_name
        self.read_all = args.read_all
        for name, characteristic in self.characteristics_menager.characteristics_by_name.items(): 
            characteristic.desired_value = args.__dict__.get(name, None)

        self.characteristics_menager.password.desired_value = args.password
        if args.password is None and self.characteristics_menager.get_for_writing_with_password_protected():
            raise PasswordRequiredException("Password required!")


    def set_verbosity(self, verbosity):
        self.verbosity = verbosity if verbosity is not None else logging.ERROR
