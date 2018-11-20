import os
import yaml

def path_realative_to_script(path):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), path) 

def get_config(file):
    config_path = path_realative_to_script(file)

    with open(config_path, 'r') as f:
        config = yaml.load(f)
        
    return config