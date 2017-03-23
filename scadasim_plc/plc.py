from dbusservice import DBusClient

from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

from threading import Timer
import socket
import time

import logging

logging.basicConfig()
log = logging.getLogger('scadasim')
log.setLevel(logging.DEBUG)

class PLC(object):

    def __init__(self, name=None):
        self.connected_sensors = {}
        self.slaveid = 0x00
        self.name = name
        if not name:
            self.name = socket.gethostname()
        self.dbusclient = DBusClient(self.name)
        self.registered = False

        identity = ModbusDeviceIdentification()
        identity.VendorName = 'scadasim'
        identity.ProductCode = 'PLC'
        identity.VendorUrl = 'https://github.com/sintax1/scadasim-plc'
        identity.ProductName = 'scadasim-PLC'
        identity.ModelName = 'SimPLC'
        identity.MajorMinorRevision = '1.0'
        self.identity = identity

    def _initialize_store(self, max_register_size=100):
        store[self.slaveid] = ModbusSlaveContext(
            di = ModbusSequentialDataBlock(0, [False]*max_register_size),
            co = ModbusSequentialDataBlock(0, [False]*max_register_size),
            hr = ModbusSequentialDataBlock(0, [0]*max_register_size),
            ir = ModbusSequentialDataBlock(0, [0]*max_register_size))
        self.context = ModbusServerContext(slaves=store, single=False)

    def _get_sensor_data(self):

        sensor_data = self.dbusclient.readSensors(plcname=self.name)
        register_types = {
            'd': 0, 'c': 1, 'h': 2, 'i': 3
        }

        if not self.slaveid == sensor_data['slaveid']:
            log.error("[PLC][%s] '%s' was expected as slaveid, not '%s' " % (self.name, self.slaveid, sensor_data['slaveid']))

        for sensor in sensor_data['sensors']:
            register = register_types[sensor_data['sensors'][sensor]['register_type']]

            address = int(sensor_data['sensors'][sensor]['data_address'])
            value = int(sensor_data['sensors'][sensor]['value'])

            self.context[self.slaveid].setValues(register, address, value)

    def _registerPLC(self):
        self.slaveid = self.dbusclient.registerPLC(plcname=self.name)
        self.registered = True
        self._initialize_store()
        log.debug("[PLC][%s] Registered on dbus" % self.name)
        return True


    def update(self):
        log.debug("[PLC][%s] Reading Sensors" % self)
        self._get_sensor_data()
        t = Timer(5, self.update, ())
        t.daemon = True
        t.start()

    def __repr__(self):
        return "%s" % self.name

    def main(self):

        log.debug("[PLC][%s] Initialized" % self.name)
        while not self.registered:
            log.debug("[PLC][%s] Trying to register with scadasim on dbus" % self.name)
            self._registerPLC()
            time.sleep(1)

        log.debug("[PLC][%s] Starting update service" % self.name)
        self.update()

        log.debug("[PLC][%s] Starting MODBUS Server" % self.name)
        StartTcpServer(self.context, identity=self.identity, address=("0.0.0.0", 5002))


if __name__ == '__main__':
    plc = PLC()
    plc.main()

"""

'di' - Discrete Inputs initializer 'co' - Coils initializer 'hr' - Holding Register initializer 'ir' - Input Registers iniatializer

    Coil/Register Numbers   Data Addresses  Type        Table Name                          Use
    1-9999                  0000 to 270E    Read-Write  Discrete Output Coils               on/off read/write   co
    10001-19999             0000 to 270E    Read-Only   Discrete Input Contacts             on/off readonly     di
    30001-39999             0000 to 270E    Read-Only   Analog Input Registers              analog readonly     ir
    40001-49999             0000 to 270E    Read-Write  Analog Output Holding Registers     analog read/write   hr

    Each coil or contact is 1 bit and assigned a data address between 0000 and 270E.
    Each register is 1 word = 16 bits = 2 bytes
"""