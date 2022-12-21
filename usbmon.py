import collections

from . import packet, util

class UsbmonPacket(packet.CapturedPacket):
	def __init__(self, number, id, type, xfer_type, epnum, devnum, busnum, flag_setup, flag_data, ts_sec, ts_usec, status, length, len_cap, setup, error_count, numdesc, interval, start_frame, xfer_flags, ndesc, data):
		super().__init__(number, id, type, xfer_type, epnum, devnum, busnum, setup, length, data)

		self.flag_setup = flag_setup
		self.flag_data = flag_data
		self.ts_sec = ts_sec
		self.ts_usec = ts_usec
		self.status = status
		self.len_cap = len_cap
		self.error_count = error_count
		self.numdesc = numdesc
		self.interval = interval
		self.start_frame = start_frame
		self.xfer_flags = xfer_flags
		self.ndesc = ndesc

	def __repr__(self):
		return f"UsbmonPacket({', '.join([(k + '=' + repr(v)) for k, v in self.__dict__.items()])})"

	def __str__(self):
		return f"UsbmonPacket({', '.join([(k + '=' + str(v)) for k, v in self.__dict__.items()])})"

UsbmonIsoDescriptor = collections.namedtuple('UsbmonIsoDescriptor',
	('iso_status', 'iso_off', 'iso_len')
)

def parse_iso_descriptors(count, usbmon_descriptor_bytes):
	descriptors = []
	ds = util.Struct(usbmon_descriptor_bytes, '=')

	for n in range(count):
		iso_status = ds.unpack_next('i')
		iso_off = ds.unpack_next('I')
		iso_len = ds.unpack_next('I')
		_pad = ds.unpack_next('L')
		descriptors.append(UsbmonIsoDescriptor(iso_status, iso_off, iso_len))

	return (descriptors, ds.offset)

def parse_usbmon_packet(usbmon_packet_bytes, number=None):
	ps = util.Struct(usbmon_packet_bytes, '=')

	id = ps.unpack_next('Q')
	type = ps.unpack_next('B')
	xfer_type = ps.unpack_next('B')
	epnum = ps.unpack_next('B')
	devnum = ps.unpack_next('B')
	busnum = ps.unpack_next('H')
	flag_setup = ps.unpack_next('B')
	flag_data = ps.unpack_next('B')
	ts_sec = ps.unpack_next('Q')
	ts_usec = ps.unpack_next('L')
	status = ps.unpack_next('i')
	length = ps.unpack_next('I')
	len_cap = ps.unpack_next('I')

	s = ps.unpack_next('8s')
	setup = iso = s
	(error_count, numdesc) = ps.unpack('ii', iso)

	interval = ps.unpack_next('i')
	start_frame = ps.unpack_next('i')
	xfer_flags = ps.unpack_next('I')
	ndesc = ps.unpack_next('I')

	assert ps.offset == 64

	return UsbmonPacket(number, id, type, xfer_type, epnum, devnum, busnum, flag_setup, flag_data, ts_sec, ts_usec, status, length, len_cap, setup, error_count, numdesc, interval, start_frame, xfer_flags, ndesc, usbmon_packet_bytes[ps.offset:])
