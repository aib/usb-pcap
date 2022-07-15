import collections
import struct

EVENT_SUBMISSION = ord('S')
EVENT_CALLBACK = ord('C')
EVENT_SUBMISSION_ERROR = ord('E')

TRANSFER_TYPE_ISOCHRONOUS = 0
TRANSFER_TYPE_INTERRUPT = 1
TRANSFER_TYPE_CONTROL = 2
TRANSFER_TYPE_BULK = 3

TRANSFER_TYPE_STRINGS = {
	None: "(unknown)",
	TRANSFER_TYPE_ISOCHRONOUS: "isochronous",
	TRANSFER_TYPE_INTERRUPT: "interrupt",
	TRANSFER_TYPE_CONTROL: "control",
	TRANSFER_TYPE_BULK: "bulk"
}

UsbSetupPacket = collections.namedtuple('UsbSetupPacket', ('bmRequestType', 'bRequest', 'wValue', 'wIndex', 'wLength'))

class PacketProcessorException(Exception): pass

class UnknownPacketTypeException(PacketProcessorException):
	def __init__(self, packet_type):
		self.packet_type = packet_type
		super().__init__(f"Unsupported packet type \"{packet_type}\"")

class ExtraneousDataException(PacketProcessorException): pass

class MismatchedRequestAndResponseException(PacketProcessorException):
	def __init__(self, field_name):
		self.field_name = field_name
		super().__init__(f"Request and response mismatched in field \"{field_name}\"")

class CompletedRequest:
	def __init__(self, request_packet, response_packet, bus, device, endpoint, transfer_type, dir_in, setup, data):
		self.request_packet = request_packet
		self.response_packet = response_packet
		self.bus = bus
		self.device = device
		self.endpoint = endpoint
		self.transfer_type = transfer_type
		self.dir_in = dir_in
		self.setup = setup
		self.data = data

		self.dir_str = "in" if self.dir_in else "out"
		self.transfer_type_str = TRANSFER_TYPE_STRINGS.get(transfer_type, TRANSFER_TYPE_STRINGS[None])

	def __str__(self):
		if self.setup is None:
			setup_str = ""
		else:
			setup_str = f"{self.setup.bmRequestType:02x}:{self.setup.bRequest:02x}:{self.setup.wValue:04x}:{self.setup.wIndex:04x} "
		return f"CompletedRequest<{self.bus}.{self.device}.{self.endpoint} {self.transfer_type_str} {self.dir_str} {setup_str}{len(self.data)}>"

class PacketProcessor:
	def __init__(self):
		self.unprocessed_packets = {}
		self.ignored_packet_count = 0

	def process_packet(self, packet):
		pid = packet.id
		ptype = packet.type

		unprocessed = self.unprocessed_packets.get(pid, None)
		if unprocessed is None:
			if ptype != EVENT_SUBMISSION:
				self.ignored_packet_count += 1
				return

			self.unprocessed_packets[pid] = packet
		else:
			if ptype == EVENT_SUBMISSION:
				self.ignored_packet_count += 1
				self.unprocessed_packets[pid] = packet
				return
			elif ptype == EVENT_CALLBACK:
				del self.unprocessed_packets[pid]
				return self.process_packet_pair(unprocessed, packet)
			elif ptype == EVENT_SUBMISSION_ERROR:
				raise Exception(f"Error packets are unsupported") # TODO
			else:
				raise UnknownPacketTypeException(packet.type)

	def process_packet_pair(self, request, response):
		def get_matching_field(field_name):
			reqval = getattr(request, field_name)
			resval = getattr(response, field_name)
			if reqval != resval:
				raise MismatchedRequestAndResponseException(field_name)
			else:
				return reqval

		xfer_type = get_matching_field('xfer_type')
		epnum_field = get_matching_field('epnum')
		devnum = get_matching_field('devnum')
		busnum = get_matching_field('busnum')
		dir_in = epnum_field & 0x80 == 0x80
		epnum = epnum_field & 0x7f

		if dir_in:
			if len(request.data) != 0:
				raise ExtraneousDataException("Found data in IN request packet")

			data = response.data
		else:
			if len(response.data) != 0:
				raise ExtraneousDataException("Found data in OUT response packet")

			data = request.data

		if xfer_type == TRANSFER_TYPE_CONTROL:
			setup_fields = struct.unpack('<BBHHH', request.setup)
			setup = UsbSetupPacket(*setup_fields)
		else:
			setup = None

		return CompletedRequest(request, response, busnum, devnum, epnum, xfer_type, dir_in, setup, data)
