import re

class BasicCharacteristic(object):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.uuid = config['uuid']
        self.flags = config.get('flags', ['--%s' % self.name])
        self.help = config.get('help', "")
        self.choices = config.get('choices', None)
        self.password_protected = config.get('password_protected', True)
        self.desired_value = None
        self.ble_characteristic = None
    
    def read(self):
        self.ble_characteristic.read_value()
    
    def __repr__(self):
        return str(self)    

class NumberCharacteristic(BasicCharacteristic):
    def __init__(self, name, config):
        super().__init__(name, config)
        self.order = config.get('order', 'little')
        self.length = config.get('length', 1)
        self.signed = config.get('signed', False)
        self.value = None
        
    def add_argument(self, argparesr):
        argparesr.add_argument(*self.flags, type=int, help=self.help, choices=self.choices, dest=self.name)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value is None:
            self.__value = None
            return
        self.__value = int.from_bytes(value, byteorder=self.order, signed=self.signed)

    def write(self):
        value = self.desired_value.to_bytes(self.length, byteorder=self.order)
        self.ble_characteristic.write_value(value)

    def __str__(self):
        return "<NumberCharacteristic {name} desired_value:{desired_value} value:{value}>".format(value=self.value, **self.__dict__)

class StringCharacteristic(BasicCharacteristic):
    def __init__(self, name, config):
        super().__init__(name, config)
        self.encoding = config.get('encoding', 'hex')
        self.value = None
        self.re = config.get('re', '^.*$')
        
    def add_argument(self, argparesr):
        argparesr.add_argument(*self.flags, type=self.validate, help=self.help, choices=self.choices, dest=self.name)

    def validate(self, value):
        pattern = re.compile(self.re)
        if not pattern.match(value):
            raise ArgumentTypeError("%s is in incorrect format" % value)
        return value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value is None:
            self.__value = None
            return
        self.__value = value.decode(self.encoding)

    def write(self):
        self.ble_characteristic.write_value(self.desired_value.encode(self.encoding))

    def __str__(self):
        return "<StringCharacteristic {name} desired_value:{desired_value} value:{value}>".format(value=self.value, **self.__dict__)


class ErrorCharacteristic(BasicCharacteristic):
    def __init__(self, config):
        super().__init__('error', config)
        self.errors = config['errors']
        self.password_protected = False
        self.value = b'\x00'

    def add_argument(self, argparesr):
        pass

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        value = int.from_bytes(value, byteorder='little', signed=False)
        self.__value = [d['message'] for d in self.errors if value & (1 << d['bitmask'])]

    def __str__(self):
        return "<ErrorCharacteristic %s>" % (self.value)

class PasswordCharacteristic(BasicCharacteristic):
    def __init__(self, config):
        super().__init__('password', config)
        self.password_protected = False

    def add_argument(self, argparesr):
        argparesr.add_argument('--password', dest='password', help="password")

    def read(self):
        pass

    def __str__(self):
        return "<PasswordCharacteristic %s>" % (self.desired_value)

    def write(self):
        self.ble_characteristic.write_value(self.desired_value.encode('ascii'))




class CharacteristicsMenager(object):
    def __init__(self, config=None):
        if config is not None:
            self.create_from_config(config)

    def __getitem__(self, key):
        if key == self.error.uuid:
            return self.error
        if key == self.password.uuid:
            return self.password
        return self.characteristics[key]

    def __contains__(self, item):
        if item == self.error.uuid:
            return True
        if item == self.password.uuid:
            return True
        return item in self.characteristics

    def create_from_config(self, config):
        self.characteristics_by_name = {}
        types = {
            "number": NumberCharacteristic,
            "string": StringCharacteristic,
        }
        for name, characteristic_config in config['services']['generic']['characteristics'].items():
            try:
                self.characteristics_by_name[name] = types[characteristic_config['type']](name, characteristic_config)
            except KeyError:
                self.logger.warning('Type key not exists or has invalid value, skipping characteristic %s', name)

        self.characteristics = {characteristic.uuid: characteristic for characteristic in self.characteristics_by_name.values()} 
        self.password = PasswordCharacteristic(config['services']['generic']['special']['password'])
        self.error = ErrorCharacteristic(config['services']['generic']['special']['error'])


    def values(self):
        return self.characteristics.values()

    def items(self):
        return self.characteristics.items()

    def get_by_name(self, name):
        return self.characteristics_by_name[name]

    def get_for_writing_with_password_protected(self):
        return [c for c in self.characteristics.values() if c.desired_value is not None and c.password_protected ]

    def get_for_writing_with_no_password_protected(self):
        return [c for c in self.characteristics.values() if c.desired_value is not None and not c.password_protected ]

    def get_unresolved(self):
        return [c for c in self.characteristics.values() if c.ble_characteristic is None]

    def get_resolved(self):
        return [c for c in self.characteristics.values() if c.ble_characteristic is not None]

    def get_all(self):
        copy = self.characteristics.copy()
        copy[self.password.uuid] = self.password
        copy[self.error.uuid] = self.error
        return copy
