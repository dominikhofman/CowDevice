import yaml
from cmdhandler import CmdHandler

config = {}
with open('services.yml', 'r') as f:
    config = yaml.load(f)

cmd_handler = CmdHandler(config)

# print(cmd_handler.characteristics)