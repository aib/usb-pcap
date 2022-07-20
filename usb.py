SETUP_DIRECTION_OUT = 0
SETUP_DIRECTION_IN = 1

SETUP_TYPE_STANDARD = 0
SETUP_TYPE_CLASS = 1
SETUP_TYPE_VENDOR = 2

SETUP_RECIPIENT_DEVICE = 0
SETUP_RECIPIENT_INTERFACE = 1
SETUP_RECIPIENT_ENDPOINT = 2
SETUP_RECIPIENT_OTHER = 3

class SetupPacket:
	def __init__(self, bmRequestType, bRequest, wValue, wIndex, wLength):
		self.bmRequestType = bmRequestType
		self.bRequest = bRequest
		self.wValue = wValue
		self.wIndex = wIndex
		self.wLength = wLength

		self.direction = (self.bmRequestType & 0x80) >> 7
		self.direction_str = "out" if self.direction == SETUP_DIRECTION_OUT else "in"

		self.type = (self.bmRequestType & 0x60) >> 5
		self.type_str = \
			"standard" if self.type == SETUP_TYPE_STANDARD else \
			"class"    if self.type == SETUP_TYPE_CLASS else \
			"vendor"   if self.type == SETUP_TYPE_VENDOR else \
			"reserved"

		self.recipient = (self.bmRequestType & 0x1f) >> 0
		self.recipient_str = \
			"device"    if self.recipient == SETUP_RECIPIENT_DEVICE else \
			"interface" if self.recipient == SETUP_RECIPIENT_INTERFACE else \
			"endpoint"  if self.recipient == SETUP_RECIPIENT_ENDPOINT else \
			"other"     if self.recipient == SETUP_RECIPIENT_OTHER else \
			"reserved"

	def get_requesttype_str(self):
		return f"{self.type_str}/{self.recipient_str}/{self.direction_str}"

	def get_summary(self, requesttype_fields=False):
		return f"{self.bmRequestType:02x}:{self.bRequest:02x}:{self.wValue:04x}:{self.wIndex:04x}"

	def __str__(self):
		return f"UsbSetupPacket<{self.get_summary()}>"
