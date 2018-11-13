import logging
import yaml
import gatt
from argparse import ArgumentParser
from cmdhandler import CmdHandler
from cowdevice import CowDevice
from characteristicsmenager import CharacteristicsMenager

config = {}
with open('services.yml', 'r') as f:
    config = yaml.load(f)

parser = ArgumentParser(description=config["description"])

cm = CharacteristicsMenager(config)

cmd_handler = CmdHandler(cm, parser)
cmd_handler.add_arguments()
cmd_handler.parse_args()

logger = logging.getLogger('console')
ch = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.setLevel(cmd_handler.verbosity)
manager = gatt.DeviceManager(adapter_name=cmd_handler.adapter_name)
cow_device = CowDevice(
    mac_address=cmd_handler.mac_address, 
    manager=manager, 
    characteristics=cm,
    read_all=cmd_handler.read_all, 
    service_uuid=config['services']['generic']['uuid']
    )

cow_device.connect()

manager.run() 
