import paho.mqtt.client as mqtt
from utils import get_config
import json 
import logger
from logger import get_remote_mqtt_logger, get_remote_main_logger, get_remote_task_logger
import socket
import queue
import time 
import subprocess
import random
import logging

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
        self.execute_topic_out = "/outbox/%s/execute" % self.name

        self.logger = get_remote_mqtt_logger()

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
        self.logger.debug('Publishing on %s', self.info_topic_out)
        self.publish(self.info_topic_out, json.dumps({'status': 'ok'})) #for autoreconnect

    def publish_result(self, response): 
        self.logger.debug('Publishing on %s', self.execute_topic_out)
        self.publish(self.execute_topic_out, json.dumps(response)) #for autoreconnect

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

class Task(object):
    def __init__(self, task):
        super().__init__()

        self.logger = logging.getLogger('task');  

        # defaults
        self.returncode = -42
        self.stdout = ''
        self.stderr = ''
        self.cmd = None

        try:
            self.taskd = json.loads(task.decode('ascii'))
            self.prepare_cmd()
            if 'id' not in self.taskd:
                self.id = random.randint(0, 10000)
                logger.info('No "id" key in task, assigning random (%s)', self.id)
            else:
                self.id = self.taskd['id']

        except json.decoder.JSONDecodeError as e:
            self.returncode = -1
            self.stderr = 'Failed to decode task!'
            self.logger.error(self.stderr)

        except KeyError as e:
            self.returncode = -2
            self.stderr = "Key %s not found in task" % e
            self.logger.error(self.stderr)

        except Exception as e:
            self.returncode = -3
            self.stderr = "Unknown error %s" % e
            self.logger.error(self.stderr)

    def prepare_cmd(self):
        self.logger.debug('Preparing commad')
        self.cmd = "sudo python3 dynamictool.py {mac} {args}".format(**self.taskd).strip()

    def execute(self):
        if self.cmd:
            self.logger.info('Executing command: %s', self.cmd)
            result = subprocess.run(self.cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.returncode = result.returncode
            self.stdout = result.stdout
            self.stderr = result.stderr
        else:
            self.logger.debug('Command not valid, skipping')
        return self.get_response()

    def get_response(self):
        return {
            "id": self.id,
            "returncode": self.returncode,
            "stdout": self.stdout.decode('ascii'),
            "stderr": self.stderr.decode('ascii'),
        }


if __name__ == "__main__":
    logger = get_remote_main_logger()
    get_remote_task_logger()
    q = queue.Queue()

    config = get_config("remote_config.yml")
    remote = RemoteClient(config, q)
    remote.start()
    while True:
        task_message = q.get()
        logger.info('Got new task %s', task_message)
        task = Task(task_message)
        result = task.execute()
        logger.debug("Result: %s", result)
        remote.publish_result(result)
        q.task_done()
