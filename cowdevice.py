import gatt
import logging
import sys

class CowDevice(gatt.Device):
    def __init__(self, mac_address, manager, service_uuid, managed=True, characteristics=None, read_all=False):
        gatt.Device.__init__(self, mac_address, manager, managed)
        self.characteristics = characteristics
        self.read_all_switch = read_all
        self.service_uuid = service_uuid

        self.logger = logging.getLogger('console')
        self.read_counter = 0
        self.write_counter = 0

    def connect(self):
        self.logger.info('Connecting to %s...', self.mac_address)
        super().connect()

    def connect_succeeded(self):
        self.logger.info("Connected")

    def connect_failed(self, error):
        self.logger.error("Connection failed: %s", error)
        sys.exit(1)

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        self.logger.info("Disconnected")
        self.manager.stop()

        
    def disconnect_failed(self):
        super().disconnect_succeeded()
        self.logger.error("Disconnect failed")
        self.manager.stop()

    def services_resolved(self):
        super().services_resolved()
        self.parse_servieces()

        if self.read_all_switch:
            for c in self.characteristics.get_resolved():
                c.read()
                self.read_counter += 1
            self.characteristics.error.read()
            self.read_counter += 1
        
        for c in self.characteristics.get_for_writing_with_no_password_protected():
            c.write()
            self.write_counter += 1

        if self.characteristics.password.desired_value is not None:
            self.logger.debug('Sending password...')
            self.characteristics.password.write()
            self.write_counter += 1

        self.check_stop_condition()

    def parse_servieces(self):
        self.logger.debug("Resolved services")
        try:
            service = [service for service in self.services if service.uuid == self.service_uuid][0]
            for ble_characteristic in service.characteristics:
                uuid = ble_characteristic.uuid
                try:
                    self.characteristics[uuid].ble_characteristic = ble_characteristic
                    self.logger.debug("Characteristic [%s] resolved", self.characteristics[uuid])
                except KeyError:
                    self.logger.warning("Characteristic [%s] not specified in services.yml!", uuid)

        except IndexError:
            self.logger.critical('Specified generic service[{}] not found!'.format(self.service_uuid))

        unresolved = self.characteristics.get_unresolved()
        if unresolved:
            self.logger.warning("Some of characteristics are unresolved! %s", [c.name for c in unresolved])

    def characteristic_value_updated(self, characteristic, value):
        char = self.characteristics[characteristic.uuid]
        char.value = value
        self.logger.info('%s updated', char)
        print("%s: %s" % (char.name, char.value))
        self.read_counter -= 1
        self.check_stop_condition()

        
    def characteristic_write_value_succeeded(self, characteristic):
        name = self.characteristics[characteristic.uuid].name
        self.logger.debug("Write for %s succeded", name)
        if name == "password":
            self.password_accepted()
        self.write_counter -= 1
        self.check_stop_condition()

    def characteristic_write_value_failed(self, characteristic, error):
        name = self.characteristics[characteristic.uuid].name
        self.logger.error("Write for %s failed: %s", name, error)
        self.write_counter -= 1
        self.check_stop_condition()

    def password_accepted(self):
        self.logger.info("Writing password protected characteristics...")
        for c in self.characteristics.get_for_writing_with_password_protected():
            self.logger.debug("Writing %s", c.name)
            c.write()
            self.write_counter += 1

    def check_stop_condition(self):
        if self.read_counter == 0 and self.write_counter == 0:
            self.disconnect()

