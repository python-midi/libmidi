#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI header."""

from io import BufferedReader, BufferedWriter
import struct

from libmidi.types.chunk import Chunk

class Header(object):
	"""
	Class representing a MIDI header.
	
	A MIDI header is a chunk that starts with the string 'MThd' and
	contains the following data:
	- format: Overall organization of MIDI file.
	          0: single multi-channel track
	          1: one or more simultaneous tracks (or MIDI outputs) of a sequence
	          2: one or more sequentially independent single-track patterns
	- ntrks: Number of tracks in the file.
	- division: The number of ticks per quarter note.
	"""

	HEADER = b'MThd'

	def __init__(self, format: int, ntrks: int, division: int):
		"""Initialize header."""
		self.format = format
		self.ntrks = ntrks
		self.division = division

	@classmethod
	def from_bytes(cls, data: bytes):
		chunk, remaining_bytes = Chunk.from_bytes(data)

		assert chunk.name == cls.HEADER, "Expected MThd chunk"
		assert len(chunk.data) == 6, "Expected 6 bytes in MThd chunk"

		format, ntrks, division = struct.unpack(">HHH", chunk.data)

		return cls(format, ntrks, division)

	@classmethod
	def from_stream(cls, stream: BufferedReader):
		"""Read header from stream."""
		chunk = Chunk.from_stream(stream)

		assert chunk.name == cls.HEADER, "Expected MThd chunk"
		assert len(chunk.data) == 6, "Expected 6 bytes in MThd chunk"

		format, ntrks, division = struct.unpack(">HHH", chunk.data)

		return cls(format, ntrks, division)

	def to_bytes(self) -> bytes:
		"""Return header as bytes."""
		# TODO: wtf? division and ntrks needs to be swapped?
		data = struct.pack(">HHH", self.format, self.division, self.ntrks)
		chunk = Chunk(name=self.HEADER, data=data)
		return chunk.to_bytes()

	def to_stream(self, stream: BufferedWriter) -> int:
		"""Write header to stream."""
		return stream.write(self.to_bytes())
