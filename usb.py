class SetupPacket:
	def __init__(self, bmRequestType, bRequest, wValue, wIndex, wLength):
		self.bmRequestType = bmRequestType
		self.bRequest = bRequest
		self.wValue = wValue
		self.wIndex = wIndex
		self.wLength = wLength

		self.direction_str = "out" if self.bmRequestType & 0x80 == 0x00 else "in"
		self.type_str = \
			"standard" if self.bmRequestType & 0x60 == 0x00 else \
			"class"    if self.bmRequestType & 0x60 == 0x20 else \
			"vendor"   if self.bmRequestType & 0x60 == 0x40 else \
			"reserved"
		self.recipient_str = \
			"device"    if self.bmRequestType & 0x1f == 0x00 else \
			"interface" if self.bmRequestType & 0x1f == 0x01 else \
			"endpoint"  if self.bmRequestType & 0x1f == 0x02 else \
			"other"     if self.bmRequestType & 0x1f == 0x03 else \
			"reserved"

	def get_requesttype_str(self):
		return f"{self.type_str}/{self.recipient_str}/{self.direction_str}"

	def get_summary(self, requesttype_fields=False):
		return f"{self.bmRequestType:02x}:{self.bRequest:02x}:{self.wValue:04x}:{self.wIndex:04x}"

	def __str__(self):
		return f"UsbSetupPacket<{self.get_summary()}>"
