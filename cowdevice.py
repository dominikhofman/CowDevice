import gatt
import logging

class CowDevice(gatt.Device):
    def __init__(self, mac_address, manager, service_uuid, managed=True, characteristics=None, password=None, read_all=False):
        gatt.Device.__init__(self, mac_address, manager, managed)
        self.password = password
        self.characteristics = characteristics
        self.read_all_switch = read_all
        self.service_uuid = service_uuid

        self.logger = logging.getLogger('cowdevice')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def connect(self):
        self.logger.info('Connecting to %s...', self.mac_address)
        super().connect()

    def connect_succeeded(self):
        self.logger.info("Connected")

    def connect_failed(self, error):
        self.logger.error("Connection failed: %s", error)

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        self.logger.info("Disconnected")
        
    def disconnect_failed(self):
        super().disconnect_succeeded()
        self.logger.error("Disconnect failed")

    def services_resolved(self):
        super().services_resolved()
        self.parse_servieces()

        if self.read_all_switch:
            self.read_all()
        
        for c in self.characteristics.get_for_writing_with_no_password_protected():
            c.write()

        if self.password is not None:
            self.logger.debug('Sending password...')
            self.characteristics.get_by_name('password').write()

    def parse_servieces(self):
        self.logger.debug("Resolved services")
        try:
            service = [service for service in self.services if service.uuid == self.service_uuid][0]
            for ble_characteristic in service.characteristics:
                uuid = ble_characteristic.uuid
                if uuid not in self.characteristics.characteristics:
                    self.logger.warning("Characteristic [%s] not specified in services.yml!", uuid)
                else:
                    self.characteristics[uuid].ble_characteristic = ble_characteristic
                    self.logger.debug("Characteristic [%s] resolved", self.characteristics[uuid])
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

    def read_all(self):
        for characteristic in self.characteristics.values():
            if characteristic.ble_characteristic is not None:
                characteristic.read()
        
    def characteristic_write_value_succeeded(self, characteristic):
        name = self.characteristics[characteristic.uuid].name
        self.logger.debug("Write for %s succeded", name)
        if name == "password":
            self.password_accepted()

    def characteristic_write_value_failed(self, characteristic, error):
        name = self.characteristics[characteristic.uuid].name
        self.logger.error("Write for %s failed: %s", name, error)

    def password_accepted(self):
        self.logger.info("Writing password protected characteristics...")
        for c in self.characteristics.get_for_writing_with_password_protected():
            c.write()
