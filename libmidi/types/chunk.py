#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI chunk."""

from io import BufferedReader
import struct
from typing import Tuple

from libmidi.utils.bytes import get_data_from_bytes

class Chunk:
	"""
	Class representing a MIDI chunk.
	
	A MIDI chunk is a sequence of bytes that starts with a 4-byte
	string, followed by a 32-bit integer representing the size of the following data.
	"""
	def __init__(self, name: bytes, data: bytes):
		self.name = name
		self.data = data

	def __str__(self):
		return f"Chunk(name={self.name}, length={self.get_length()})"

	@classmethod
	def from_bytes(cls, data: bytes) -> Tuple['Chunk', bytes]:
		"""Read a chunk from bytes."""
		chunk_header, remaining_data = get_data_from_bytes(data, 8)
		name, length = struct.unpack('>4sL', chunk_header)
		chunk_data, remaining_data = get_data_from_bytes(data, length)

		return Chunk(name, chunk_data), remaining_data

	@classmethod
	def from_stream(cls, buffer: BufferedReader):
		"""Read a chunk from a stream."""
		name, length = struct.unpack('>4sL', buffer.read(8))
		data = buffer.read(length)

		return Chunk(name, data)

	def get_length(self) -> int:
		"""Return length of data."""
		return len(self.data)

	def to_bytes(self) -> bytes:
		"""Return chunk as bytes."""
		return struct.pack('>4sL', self.name, self.get_length()) + self.data
