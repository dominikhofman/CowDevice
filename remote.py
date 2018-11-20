import paho.mqtt.client as mqtt
from utils import get_config
import json 
import logging
import socket
import queue
import time 

class RemoteClient(mqtt.Client):
    def __init__(self, config, queue):
        mqtt.Client.__init__(self)
        self.config = config['mqtt_config']
        self.queue = queue

        self.name = self.config['name'] if self.config['name'] else socket.gethostname()
        self.auto_reconnect = self.config['auto_reconnect']
        self.reconnect_delay = self.config['reconnect_delay']
        self.keep_alive = self.config['keep_alive']
        self.will_set('/outbox/%s/lwt' % self.name, 'disconnected', 0, False)
        self.info_topic = "/inbox/%s/info" % self.name
        self.info_topic_out = "/outbox/%s/info" % self.name
        self.execute_topic = "/inbox/%s/execute" % self.name
                                                                                
        self.logger = logging.getLogger('remote');                                                                               
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.setLevel(logging.DEBUG)   

    def start(self):
        self.connect(self.config['host'], self.config['port'])
        self.loop_start()
        
    def on_connect(self, client, userdata, flags, rc):
        self.logger.info('Connected')
        for t in [self.info_topic, self.execute_topic]:
            self.logger.debug('Subscribing %s', t)
            self.subscribe(t)

        self.message_callback_add(self.info_topic, self.on_info_topic)
        self.message_callback_add(self.execute_topic, self.on_execute_topic)

        self.publish_info()

    def on_disconnect(self, userdata, rc): 
        if rc != 0:
            self.logger.error("Unexpected disconnection")

        if self.auto_reconnect:
            time.sleep(self.reconnect_delay)
            self.logger.info("Reconnecting...")
            self.connect(mqttBrokerName, mqttBrokerPort, self.keep_alive)

    def publish_info(self): 
        self.logger.debug('Publishing  %s', t)
        self.publish(self.info_topic_out, json.dumps({'status': 'ok'})) #for autoreconnect

    def on_info_topic(self, client, userdata, message):
        self.logger.info('Info topic')
        self.publish_info()

    def on_execute_topic(self, client, userdata, message):
        self.logger.debug('Execute topic')
        try:
            self.queue.put(message.payload)
        except Exception as e:
            self.logger.error(e)

    def on_unknown_topic(self, client, userdata, message):
        self.logger.error('Unknown topic')



if __name__ == "__main__":
    q = queue.Queue()

    config = get_config("remote_config.yml")
    remote = RemoteClient(config, q)
    remote.start()

    while True:
        task = q.get()
        logging.error('Working %s', task)
        time.sleep(1)
        q.task_done()
