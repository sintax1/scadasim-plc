from dbusservice import DBusClient

from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

import threading
import socket
import time

import logging
from Queue import Queue

from multiprocessing import Queue, Process

class CallbackDataBlock(ModbusSequentialDataBlock):
    ''' A datablock that stores the new value in memory
    and passes the operation to a message queue for further
    processing.
    '''

    def __init__(self, queue, max_register_size):
        '''
        '''
        self.queue = queue

        values = {k:0 for k in range(1, max_register_size)}
        super(CallbackDataBlock, self).__init__(0, values)

    def setValues(self, address, value):
        ''' Sets the requested values of the datastore

        :param address: The starting address
        :param values: The new values to be set
        '''
        super(CallbackDataBlock, self).setValues(address, value)
        self.queue.put((address, value))


logging.basicConfig()
log = logging.getLogger('scadasim')
log.setLevel(logging.INFO)

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
        self.speed = 1
        self.queue = Queue()

    def _initialize_store(self, max_register_size=100):
        store = {}
        block = CallbackDataBlock(self.queue, max_register_size)

        store[self.slaveid] = ModbusSlaveContext(
            di = block,
            co = block,
            hr = block,
            ir = block)
        self.context = ModbusServerContext(slaves=store, single=False)

    def _get_sensor_data(self):

        sensor_data = self.dbusclient.readSensors(plcname=self.name)
        register_types = {
            'd': 0, 'c': 1, 'h': 2, 'i': 3
        }

        """
        if not self.slaveid == sensor_data['slaveid']:
            log.error("[PLC][%s] '%s' was expected as slaveid, not '%s' " % (self.name, self.slaveid, sensor_data['slaveid']))
        """

        for sensor in sensor_data:
            register = register_types[sensor_data[sensor]['register_type']]

            address = int(sensor_data[sensor]['data_address'])
            value = int(sensor_data[sensor]['value'])

            self.context[self.slaveid].setValues(register, address, [value])

    def _registerPLC(self):
        self.slaveid = self.dbusclient.registerPLC(plcname=self.name)
        self.registered = True
        self._initialize_store()
        log.debug("[PLC][%s] Registered on dbus" % self.name)
        return True

    def update(self):
        log.debug("[PLC][%s] Reading Sensors" % self)
        self._get_sensor_data()

        while True:
            # Update scadasim with any new values from Master
            address, value = self.queue.get()
            if not address: break
            log.debug("[PLC][%s] setting register %s to value %s" % (self.name, address, value))
            self.dbusclient.setValue(plcname=self.name, address=address, value=value)

        delay = (-time.time()%self.speed)
        t = threading.Timer(delay, self.update, ())
        t.daemon = True
        t.start()

    def set_speed(self, speed):
        self.speed = speed

    def __repr__(self):
        return "%s" % self.name

    def main(self):

        log.debug("[PLC][%s] Initialized" % self.name)
        while not self.registered:
            log.debug("[PLC][%s] Trying to register with scadasim on dbus" % self.name)
            try:
                self._registerPLC()
            except KeyError:
                log.warn("[PLC][%s] PLC not found within scadasim. Verify Docker Compose container names match list of plcs in scadasim config")
                
            time.sleep(1)

        log.debug("[PLC][%s] Starting update service" % self.name)
        self.update()

        log.debug("[PLC][%s] Starting MODBUS Server" % self.name)
        StartTcpServer(self.context, identity=self.identity, address=("0.0.0.0", 502))


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