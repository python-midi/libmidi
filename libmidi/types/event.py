#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI event."""

from typing import Tuple

from libmidi.types.message import BaseMessage, message_from_bytes
from libmidi.utils.variable_length import VariableInt

class Event:
	"""
	Class representing a MIDI event.
	
	A MIDI event is a sequence of bytes that starts with a variable int delta time,
	followed by a MIDI message.
	"""
	def __init__(self, delta_time: int, message: BaseMessage):
		self.delta_time = delta_time
		self.message = message

	def __str__(self):
		return f"Delta time: {self.delta_time}, message: {self.message}"

	def copy(self, **kwargs):
		if "delta_time" not in kwargs:
			kwargs["delta_time"] = self.delta_time
		if "message" not in kwargs:
			kwargs["message"] = self.message.copy()

		return Event(**kwargs)

	@classmethod
	def from_bytes(cls, data: bytes, last_status_byte: int = None) -> Tuple['Event', bytes]:
		"""Read an event from bytes."""
		delta_time, data = VariableInt.from_bytes(data)
		message, remaining_data = message_from_bytes(data, last_status_byte)

		return cls(delta_time, message), remaining_data

	def to_bytes(self) -> bytes:
		"""Return event as bytes."""
		return VariableInt.to_bytes(self.delta_time) + self.message.to_bytes()
