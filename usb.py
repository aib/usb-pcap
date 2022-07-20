class SetupPacket:
	def __init__(self, bmRequestType, bRequest, wValue, wIndex, wLength):
		self.bmRequestType = bmRequestType
		self.bRequest = bRequest
		self.wValue = wValue
		self.wIndex = wIndex
		self.wLength = wLength

		self.direction = (self.bmRequestType & 0x80) >> 7
		self.direction_str = "out" if self.direction == 0 else "in"

		self.type = (self.bmRequestType & 0x60) >> 5
		self.type_str = \
			"standard" if self.type == 0 else \
			"class"    if self.type == 1 else \
			"vendor"   if self.type == 2 else \
			"reserved"

		self.recipient = (self.bmRequestType & 0x1f) >> 0
		self.recipient_str = \
			"device"    if self.recipient == 0 else \
			"interface" if self.recipient == 1 else \
			"endpoint"  if self.recipient == 2 else \
			"other"     if self.recipient == 3 else \
			"reserved"

	def get_requesttype_str(self):
		return f"{self.type_str}/{self.recipient_str}/{self.direction_str}"

	def get_summary(self, requesttype_fields=False):
		return f"{self.bmRequestType:02x}:{self.bRequest:02x}:{self.wValue:04x}:{self.wIndex:04x}"

	def __str__(self):
		return f"UsbSetupPacket<{self.get_summary()}>"
