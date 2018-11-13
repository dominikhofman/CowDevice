class BasicCharacteristic(object):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.uuid = config['uuid']
        self.flags = config['flags']
        self.help = config.get('help', "")
        self.choices = config.get('choices', None)
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

def create_chars(config):
    chars = {}
    for name, config in config['services']['generic']['characteristics'].items():
        if config.get('type', 'number') == 'number':
            chars[name] = NumberCharacteristic(name, config)
    return chars

parser = ArgumentParser(description=config["description"])
chars = create_chars(config)

def add_arguments(chars, argparser):
    for char in chars.values():
        char.add_argument(parser)

add_arguments(chars, parser)

args = parser.parse_args()

def assign_values(chars, args):
    values = {key: value for key, value in args.__dict__.items() if not key.startswith('__')}
    for name, value in values.items():
        chars[name].set_desired_value(value)
    