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
