import collections

from . import util

UsbmonPacket = collections.namedtuple('UsbmonPacket',
	('number', 'id', 'type', 'xfer_type', 'epnum', 'devnum', 'busnum', 'flag_setup', 'flag_data', 'ts_sec', 'ts_usec', 'status', 'length', 'len_cap', 'setup', 'error_count', 'numdesc', 'interval', 'start_frame', 'xfer_flags', 'ndesc', 'data'),
)
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
