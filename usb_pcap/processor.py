import collections
import struct

from . import usb, usbmon

EVENT_SUBMISSION = ord('S')
EVENT_CALLBACK = ord('C')
EVENT_SUBMISSION_ERROR = ord('E')

class PacketProcessorException(Exception): pass

class UnknownPacketTypeException(PacketProcessorException):
	def __init__(self, packet_type):
		self.packet_type = packet_type
		super().__init__(f"Unsupported packet type \"{packet_type}\"")

class MismatchedRequestAndResponseException(PacketProcessorException):
	def __init__(self, field_name):
		self.field_name = field_name
		super().__init__(f"Request and response mismatched in field \"{field_name}\"")

class IsoPacket:
	def __init__(self, status, data):
		self.status = status
		self.data = data

	def __str__(self):
		return f"IsoPacket<status {self.status}, data {len(self.data)} bytes>"

class IsoTransfer:
	def __init__(self, packets):
		self.packets = packets
		self.good_packets = [p for p in packets if p.status == 0]

	def __str__(self):
		return f"IsoTransfer<{len(self.good_packets)}/{len(self.packets)} packets>"

class CompletedRequest:
	def __init__(self, request_packet, response_packet, bus, device, endpoint, transfer_type, dir_in, setup, iso, data, data_length):
		self.request_packet = request_packet
		self.response_packet = response_packet
		self.bus = bus
		self.device = device
		self.endpoint = endpoint
		self.transfer_type = transfer_type
		self.dir_in = dir_in
		self.setup = setup
		self.iso = iso
		self.data = data
		self.data_length = data_length

		self.dir_str = "in" if self.dir_in else "out"
		self.transfer_type_str = usb.TRANSFER_TYPE_STRINGS.get(transfer_type, usb.TRANSFER_TYPE_STRINGS[None])

	def __str__(self):
		if self.setup is not None:
			srn = self.setup.get_standard_request_name()
			setup_str = f"{srn if srn is not None else self.setup.type_str}/{self.setup.recipient_str}/{self.setup.direction_str} {self.setup.get_summary()} "
		else:
			setup_str = ""

		if self.data_length != len(self.data):
			len_str = f"{len(self.data)}/{self.data_length} (truncated) bytes"
		else:
			len_str = f"{self.data_length} bytes"

		return f"CompletedRequest<{self.bus}.{self.device}.{self.endpoint} {self.transfer_type_str} {self.dir_str} {setup_str}{len_str}>"

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
			data_packet = response
		else:
			data_packet = request

		if xfer_type == usb.TRANSFER_TYPE_CONTROL:
			setup_fields = struct.unpack('<BBHHH', request.setup)
			setup = usb.SetupPacket(*setup_fields)
		else:
			setup = None

		if xfer_type == usb.TRANSFER_TYPE_ISOCHRONOUS:
			packets = []

			descriptors, data_offset = usbmon.parse_iso_descriptors(data_packet.ndesc, data_packet.data)
			for d in descriptors:
				packet = IsoPacket(d.iso_status, data_packet.data[data_offset+d.iso_off:data_offset+d.iso_off+d.iso_len])
				packets.append(packet)

			iso = IsoTransfer(packets)
		else:
			iso = None

		return CompletedRequest(request, response, busnum, devnum, epnum, xfer_type, dir_in, setup, iso, data_packet.data, data_packet.length)
