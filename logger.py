import logging

def get_base_logger(name):
    logger = logging.getLogger(name);                                                                               
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)   
    return logger

def get_remote_mqtt_logger():
    return get_base_logger('mqtt')

def get_remote_main_logger():
    return get_base_logger('main')

def get_remote_task_logger():
    return get_base_logger('task')