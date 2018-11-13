import logging
import yaml
import gatt
from cmdhandler import CmdHandler
from cowdevice import CowDevice

config = {}
with open('services.yml', 'r') as f:
    config = yaml.load(f)

cmd_handler = CmdHandler(config)
logger = logging.getLogger('cowdevice')
logger.setLevel(cmd_handler.verbosity)
manager = gatt.DeviceManager(adapter_name=cmd_handler.adapter_name)
cow_device = CowDevice(
    mac_address=cmd_handler.mac_address, 
    manager=manager, 
    characteristics=cmd_handler.characteristics_menager,
    read_all=cmd_handler.read_all, 
    service_uuid=config['services']['generic']['uuid']
    )

cow_device.connect()

manager.run() 
