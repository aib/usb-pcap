from . import usb, util

class UsbpcapPacket:
	def __init__(self, number, header_len, irp_id, irp_status, urb_func, irp_info, bus, device, endpoint, transfer, data_length, stage, setup_data, data):
		if irp_info & 0x01:
			type_ = ord('C')
		else:
			type_ = ord('S')

		self.number = number
		self.id = irp_id
		self.type = type_
		self.xfer_type = transfer
		self.epnum = endpoint
		self.devnum = device
		self.busnum = bus
		self.setup = setup_data
		self.length = data_length
		self.data = data

	def __repr__(self):
		return f"UsbpcapPacket({', '.join([(k + '=' + repr(v)) for k, v in self.__dict__.items()])})"

	def __str__(self):
		return f"UsbpcapPacket({', '.join([(k + '=' + str(v)) for k, v in self.__dict__.items()])})"

def parse_usbpcap_packet(usbpcap_packet_bytes, number=None):
	ps = util.Struct(usbpcap_packet_bytes, '=')

	header_len = ps.unpack_next('H')
	irp_id = ps.unpack_next('Q')
	irp_status = ps.unpack_next('L')
	urb_func = ps.unpack_next('H')

	irp_info = ps.unpack_next('B')
	bus = ps.unpack_next('H')
	device = ps.unpack_next('H')
	endpoint = ps.unpack_next('B')
	transfer = ps.unpack_next('B')
	data_length = ps.unpack_next('L')

	stage = None

	if transfer == usb.TRANSFER_TYPE_ISOCHRONOUS:
		raise Exception("ISO not supported") # TODO
	elif transfer == usb.TRANSFER_TYPE_CONTROL:
		stage = ps.unpack_next('B')

	if stage == 0:
		setup_data = usbpcap_packet_bytes[header_len:header_len+8]
		data_length -= 8
		data = usbpcap_packet_bytes[header_len+8:]
	else:
		setup_data = None
		data = usbpcap_packet_bytes[header_len:]

	assert ps.offset == header_len

	return UsbpcapPacket(number, header_len, irp_id, irp_status, urb_func, irp_info, bus, device, endpoint, transfer, data_length, stage, setup_data, data)
