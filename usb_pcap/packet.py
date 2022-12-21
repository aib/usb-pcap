class CapturedPacket:
	def __init__(self, number, id, type, xfer_type, epnum, devnum, busnum, setup, length, data):
		self.number = number
		self.id = id
		self.type = type
		self.xfer_type = xfer_type
		self.epnum = epnum
		self.devnum = devnum
		self.busnum = busnum
		self.setup = setup
		self.length = length
		self.data = data
