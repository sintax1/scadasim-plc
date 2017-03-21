from scadasim import Simulator
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

class PLC(object):

	def __init__(self):
		self.connected_sensors = {}

		store = ModbusSlaveContext(
		    di = ModbusSequentialDataBlock(0, [False]*100),
		    co = ModbusSequentialDataBlock(0, [False]*100),
		    hr = ModbusSequentialDataBlock(0, [0]*100),
		    ir = ModbusSequentialDataBlock(0, [0]*100))
		context = ModbusServerContext(slaves=store, single=True)

		identity = ModbusDeviceIdentification()
		identity.VendorName = 'scadasim'
		identity.ProductCode = 'PLC'
		identity.VendorUrl = 'https://github.com/sintax1/scadasim-plc'
		identity.ProductName = 'scadasim-PLC'
		identity.ModelName = 'SimPLC'
		identity.MajorMinorRevision = '1.0'


		pass

	def run(self):
		pass
