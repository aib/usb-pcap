import unittest
import traceback

import pcapng
from usb_pcap import processor, usbmon, usbpcap

class TestParse(unittest.TestCase):
	def test_capture_files(self):
		CAPTURE_FILES = [
#			{
#				'file': 'tests/usbmon_example1.pcapng',
#				'parser': 'usbmon',
#				'pairs': 42,
#			}, {
#				'file': 'tests/usbpcap_example1.pcapng',
#				'parser': 'usbpcap',
#				'pairs': 42,
#			}
		]

		for f in CAPTURE_FILES:
			self.process_capture_file(f)

	def process_capture_file(self, cap):
		proc = processor.PacketProcessor()
		packet_number = 0
		pairs = []

		if cap['parser'] == 'usbmon':
			parser = usbmon.parse_usbmon_packet
		elif cap['parser'] == 'usbpcap':
			parser = usbpcap.parse_usbpcap_packet
		else:
			raise Exception("Invalid parser")

		with open(cap['file'], 'rb') as f:
			for block in pcapng.FileScanner(f):
				if isinstance(block, pcapng.blocks.EnhancedPacket):
					packet_number += 1

					try:
						packet = parser(block.packet_data, packet_number)
					except Exception as e:
						print(f"Failed to process packet {packet_number}:", file=sys.stderr)
						traceback.print_exc(file=sys.stderr)
						continue

					pp = proc.process_packet(packet)

					if pp is not None:
						pairs.append(pp)

		self.assertEqual(cap['pairs'], len(pairs))
