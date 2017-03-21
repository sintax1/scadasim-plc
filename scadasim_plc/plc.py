from scadasim import Simulator

from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

from threading import Timer

class PLC(object):

    def __init__(self):
        self.connected_sensors = {}

        store = ModbusSlaveContext(
            di = ModbusSequentialDataBlock(0, [False]*100),
            co = ModbusSequentialDataBlock(0, [False]*100),
            hr = ModbusSequentialDataBlock(0, [0]*100),
            ir = ModbusSequentialDataBlock(0, [0]*100))
        self.context = ModbusServerContext(slaves=store, single=True)

        identity = ModbusDeviceIdentification()
        identity.VendorName = 'scadasim'
        identity.ProductCode = 'PLC'
        identity.VendorUrl = 'https://github.com/sintax1/scadasim-plc'
        identity.ProductName = 'scadasim-PLC'
        identity.ModelName = 'SimPLC'
        identity.MajorMinorRevision = '1.0'
        self.identity = identity

    def update(self):
        print "Update"
        t = Timer(5, self.update, ())
        t.daemon = True
        t.start()


    def main(self):
        print "Starting update service"
        self.update()

        print "Starting MODBUS Server"
        StartTcpServer(self.context, identity=self.identity, address=("0.0.0.0", 5002))


if __name__ == '__main__':
    plc = PLC()
    plc.main()

"""
#---------------------------------------------------------------------------# 
# import various server implementations
#---------------------------------------------------------------------------# 
from pymodbus.server.async import StartTcpServer
from pymodbus.server.async import StartUdpServer
from pymodbus.server.async import StartSerialServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer



import sys
import logging
import logging.handlers
import socket




#---------------------------------------------------------------------------# 
# callback processes for simulating register updating on its own
#---------------------------------------------------------------------------# 

# increments holding regsiters register #0x0 
def updating_writer(a):
    log.debug("register update simulation")
    context = a[0]
    slave_id = 0x00
    holdingRegister = 3
    coil = 1
    
    # access holding registers addr 0 - 3 = drums 1 - 4 in lab 6
    drumsAddress = 0x0
    drums = context[slave_id].getValues(holdingRegister, drumsAddress, count=4)
    # access coils addr 0 - 3 = pumps 1 - 4 in lab6
    pumpsAddress = 0x0
    pumps = context[slave_id].getValues(coil, pumpsAddress, count=4)

    # access coils addr 10 - 11 = input and output valves respectively
    valvesAddress = 0x0a # dec 10 = hex 0x0a
    valves = context[slave_id].getValues(coil, valvesAddress, count=2)

    # update drums 
    if valves[0] == True: 
        drums[1] = drums[1] + 2
    if valves[1] == True:
        drums[0] = drums[0] - 2

    if pumps[0] == True:
        if drums[0] > 0:
            drums[1] = drums[1] + 1
            drums[0] = drums[0] - 1
    if pumps[1] == True:
        if drums[2] > 0:
            drums[0] = drums[0] + 1
            drums[2] = drums[2] - 1
    if pumps[2] == True:
        if drums[3] > 0:
            drums[2] = drums[2] + 1
            drums[3] = drums[3] - 1
    if pumps[3] == True:
        if drums[1] > 0:
            drums[3] = drums[3] + 1
            drums[1] = drums[1] - 1

    for i in range(0,4):
        if drums[i] >= 100:
            drums[i] = 100
        if drums[i] <= 0:
            drums[i] = 0


    context[slave_id].setValues(holdingRegister, drumsAddress, drums)
   

def logToArcSight(a):
    context = a[0]
    slave_id = 0x00
    holdingRegister = 3
    coil = 1
    
    # access holding registers addr 0 - 3 = drums 1 - 4 in lab 6
    drumsAddress = 0x0
    drums = context[slave_id].getValues(holdingRegister, drumsAddress, count=4)
    # access coils addr 0 - 3 = pumps 1 - 4 in lab6
    pumpsAddress = 0x0
    pumps = context[slave_id].getValues(coil, pumpsAddress, count=4)

    # access coils addr 10 - 11 = input and output valves respectively
    valvesAddress = 0x0a # dec 10 = hex 0x0a
    valves = context[slave_id].getValues(coil, valvesAddress, count=2)

    for i in range(0,4):
        log.info("|PLC-SIM|pyModbus|1.0.0.0|INFO|INFO: PLC Status Update|2|app=Modbus/TCP cs1Label=Drum_" + str(i+1) + "_Level cn1=" + str(drums[i]))
        if pumps[i]:
            pumps[i] = 'On'
        else:
            pumps[i] = 'Off'
        log.info("|PLC-SIM|pyModbus|1.0.0.0|INFO|INFO: PLC Status Update|2|app=Modbus/TCP cs1Label=Pump_" + str(i+1) + "_State cs1=" + pumps[i])

    for i in range(0,2):
        if valves[i]:
            valves[i] = 'On'
        else:
            valves[i] = 'Off'

    log.info("|PLC-SIM|pyModbus|1.0.0.0|INFO|INFO: PLC Status Update|2|app=Modbus/TCP cs1Label=Input_Valve_State cs1=" + valves[0])
    log.info("|PLC-SIM|pyModbus|1.0.0.0|INFO|INFO: PLC Status Update|2|app=Modbus/TCP cs1Label=Output_Valve_State cs1=" + valves[1])
"""
