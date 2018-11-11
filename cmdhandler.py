import re
from argparse import ArgumentParser, ArgumentTypeError
import logging

class BasicCharacteristic(object):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.uuid = config['uuid']
        self.flags = config['flags']
        self.help = config.get('help', "")
        self.choices = config.get('choices', None)
        self.password_protected = config.get('password_protected', True)
        self.desired_value = None

    def set_desired_value(self, value):
        self.desired_value = value


class NumberCharacteristic(BasicCharacteristic):
    def __init__(self, name, config):
        super().__init__(name, config)
        self.order = config.get('order', 'little')
        self.length = config.get('length', 1)
        
    def add_argument(self, argparesr):
        argparesr.add_argument(*self.flags, type=int, help=self.help, choices=self.choices, dest=self.name)

    def __str__(self):
        return "<NumberCharacteristic {name} {order} {length} {choices} {desired_value}>".format(**self.__dict__)

    def __repr__(self):
        return str(self)

def check_mac(value):
    pattern = re.compile("^((?:[\da-f]{2}[:\-]){5}[\da-f]{2})$", re.IGNORECASE)
    if not pattern.match(value):
         raise ArgumentTypeError("%s is in incorrect format" % value)
    return value

class CmdHandler(object):
    """
    generate characteristics based on config file and command line arguments
    """
    def __init__(self, config):
        self.config = config
        self.parser = ArgumentParser(description=config["description"])
        self.characteristics = None
        self.create_characteristics()
        self.add_constant_arguments()
        self.add_characteristics_arguments()
        self.parse()

    def create_characteristics(self):
        self.characteristics = {}
        for name, config in self.config['services']['generic']['characteristics'].items():
            if config.get('type', 'number') == 'number':
                self.characteristics[name] = NumberCharacteristic(name, config)

    def add_constant_arguments(self):
        # self.parser.add_argument('mac_address', type=check_mac, 
        #     help="MAC address of cowdevice to connect, format: hexdigits separated by colon")
        self.parser.add_argument('-r', '--read-all', action='store_true', dest='read-all'
            help="MAC address of cowdevice to connect, format: hexdigits separated by colon")
            
        
        group = self.parser.add_mutually_exclusive_group()
        group.add_argument('-v', action='store_const', const=logging.WARN, dest='verbosity')
        group.add_argument('-vv', action='store_const', const=logging.INFO, dest='verbosity')
        group.add_argument('-vvv', action='store_const', const=logging.DEBUG, dest='verbosity')
# 
    def add_characteristics_arguments(self):
        for characteristic in self.characteristics.values():
            characteristic.add_argument(self.parser)

    def parse(self):
        args = self.parser.parse_args()
        self.set_verbosity(args.verbosity)
        for name, characteristic in self.characteristics.items():
            characteristic.set_desired_value(args.__dict__[name])

    def set_verbosity(self, verbosity):
        self.verbosity = verbosity if verbosity is not None else logging.ERROR
        print (self.verbosity)
    