#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI variable-length quantity utils."""

from io import BufferedReader
from typing import Tuple

class VariableInt:
	"""MIDI variable-length quantity utils."""

	@staticmethod
	def from_bytes(data: bytes) -> Tuple[int, bytes]:
		"""
		Read a variable-length quantity from bytes.
		
		Returns the value and the remaining bytes.
		"""
		delta = 0

		while True:
			byte = int.from_bytes(data[0:1], 'big')
			delta = (delta << 7) | (byte & 0x7f)
			if byte < 0x80:
				return delta, data[1:]
			data = data[1:]

	@staticmethod
	def from_stream(buffer: BufferedReader) -> int:
		"""Read a variable-length quantity from a stream."""
		delta = 0

		while True:
			byte = int.from_bytes(buffer.read(1), 'big')
			delta = (delta << 7) | (byte & 0x7f)
			if byte < 0x80:
				return delta

	@staticmethod
	def to_bytes(value: int) -> bytes:
		"""Return value as bytes."""
		if value < 0:
			raise ValueError('variable int must be a non-negative integer')

		bytes_list = []
		while value:
			bytes_list.append(value & 0x7f)
			value >>= 7

		if bytes_list:
			bytes_list.reverse()

			# Set high bit in every byte but the last.
			for i in range(len(bytes_list) - 1):
				bytes_list[i] |= 0x80
			return bytes(bytes_list)
		else:
			return bytes([0])

	@staticmethod
	def to_stream(value: int, buffer: BufferedReader):
		"""Write a variable-length quantity to a stream."""
		buffer.write(VariableInt.to_bytes(value))
