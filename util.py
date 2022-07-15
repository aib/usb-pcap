import struct

class Struct:
	def __init__(self, buffer, format_first_char=''):
		self.buffer = buffer
		self.offset = 0
		self.format_first_char = format_first_char

	def unpack(self, format, buffer):
		full_format = self.get_full_format(format)
		return struct.unpack(full_format, buffer)

	def unpack_next(self, format):
		full_format = self.get_full_format(format)
		vsize = struct.calcsize(full_format)
		val = struct.unpack_from(full_format, self.buffer, offset=self.offset)
		self.offset += vsize
		if len(val) == 1:
			return val[0]
		else:
			return val

	def get_full_format(self, format):
		return self.format_first_char + format

def get_hexdump(bytes_, bytes_per_row=16, addr_len=4):
	out = ""

	if addr_len > 0:
		addr_max_len = len("%x" % (len(bytes_),))
		addr_len = max(addr_len, addr_max_len)

	for row in range(len(bytes_) // bytes_per_row + 1):
		addr = row * bytes_per_row
		rowbytes = bytes_[addr:addr+bytes_per_row]

		if addr_len > 0:
			adrs = f"%0{addr_len}x: " % (addr,)
		else:
			adrs = ""

		hexs = " ".join(["%02x" % (b,) for b in rowbytes])
		chrs = "".join([chr(b) if chr(b).isprintable() else "." for b in rowbytes])
		pad = " " * (3 * bytes_per_row - len(hexs))
		out += ("\n" if out else "") + f"{adrs}{hexs}{pad} {chrs}"

	return out

def hexdump(*args, **kwargs):
	print(get_hexdump(*args, **kwargs))
