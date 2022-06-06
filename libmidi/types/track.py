#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI track."""

from io import BufferedReader
from typing import List

from libmidi.types.chunk import Chunk
from libmidi.types.event import Event

class Track:
	"""
	Class representing a MIDI track.

	A MIDI track is a sequence of MIDI events.
	It starts with a header chunk and ends with a end of track meta message.
	"""

	HEADER = b'MTrk'

	def __init__(self, events: List[Event] = None):
		self.events = events or []

	@classmethod
	def from_stream(cls, stream: BufferedReader):
		"""Read a track from a stream."""
		events = []
		chunk = Chunk.from_stream(stream)

		assert chunk.name == cls.HEADER, "Invalid track chunk type"

		data = chunk.data
		last_status_byte: int = None
		while data:
			event, data = Event.from_bytes(data, last_status_byte)
			last_status_byte = event.message.get_status_byte()
			events.append(event)

		return cls(events)

	def to_bytes(self) -> bytes:
		"""Write a track to bytes."""
		chunk = Chunk(name=self.HEADER, data=b''.join(event.to_bytes() for event in self.events))
		return chunk.to_bytes()

	def to_stream(self, stream: BufferedReader):
		"""Write a track to a stream."""
		stream.write(self.to_bytes())
