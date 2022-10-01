#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI channel message."""

import struct
from typing import Dict, Tuple, Type

from libmidi.utils.bytes import get_data_from_bytes
from libmidi.types.messages.common import BaseMessage

class BaseMessageChannel(BaseMessage):
	"""
	Base class for channel messages.

	Since all channel messages have the same structure (at least a channel data +
	8 bit data bytes), we can commonize a lot of methods.
	"""
	channel_message_type: int

	def __init__(self, channel: int):
		"""Initialize a channel message."""
		self.channel = channel

	def __str__(self) -> str:
		"""Return a string representation of the message."""
		return (
			super().__str__()
			+ f", channel message type: {hex(self.channel_message_type)}"
			+ f", channel: {self.channel}"
		)

	@classmethod
	def _assert_status_byte(cls, status_byte: int):
		assert status_byte >> 4 == cls.channel_message_type, "Invalid channel message type"

	def copy(self, **kwargs) -> 'BaseMessageChannel':
		if 'channel' not in kwargs:
			kwargs['channel'] = self.channel

		return super().copy(**kwargs)

	@classmethod
	def from_bytes(cls, data: bytes):
		_, channel, remaining_data = cls._get_status_data(data)

		message_data, remaining_data = get_data_from_bytes(remaining_data, len(cls.attributes))

		zipped_data = dict(zip(cls.attributes, struct.unpack(f">{'B' * len(cls.attributes)}", message_data)))

		for attr, value in zipped_data.items():
			if 0 >= value > 127:
				raise ValueError(f"Invalid value for {attr}")

		return cls(channel, **dict(zipped_data)), remaining_data

	def get_status_byte(self):
		return (self.channel_message_type << 4) | self.channel

	def get_length(self) -> int:
		# status + channel + attributes
		return super().get_length() + 1 + len(self.attributes)

	def to_bytes(self):
		status_byte = self.get_status_byte()
		message_data = struct.pack(f">{'B' * len(self.attributes)}",
		                           *[getattr(self, attr) for attr in self.attributes])
		return status_byte.to_bytes(1, 'big', signed=False) + message_data

class MessageNoteOff(BaseMessageChannel):
	channel_message_type = 0x8
	attributes = ['note', 'velocity']

	def __init__(self, channel: int, note: int, velocity: int):
		"""Initialize a note off message."""
		super().__init__(channel)

		self.note = note
		self.velocity = velocity

class MessageNoteOn(BaseMessageChannel):
	channel_message_type = 0x9
	attributes = ['note', 'velocity']

	def __init__(self, channel: int, note: int, velocity: int):
		"""Initialize a note on message."""
		super().__init__(channel)

		self.note = note
		self.velocity = velocity

class MessageAftertouch(BaseMessageChannel):
	channel_message_type = 0xA
	attributes = ['note', 'value']

	def __init__(self, channel: int, note: int, value: int):
		"""Initialize an aftertouch message."""
		super().__init__(channel)

		self.note = note
		self.value = value

class MessageControlChange(BaseMessageChannel):
	channel_message_type = 0xB
	attributes = ['control', 'value']

	def __init__(self, channel: int, control: int, value: int):
		"""Initialize a control change message."""
		super().__init__(channel)

		self.control = control
		self.value = value

class MessageProgramChange(BaseMessageChannel):
	channel_message_type = 0xC
	attributes = ['program']

	def __init__(self, channel: int, program: int):
		"""Initialize a program change message."""
		super().__init__(channel)

		self.program = program

class MessageChannelAftertouch(BaseMessageChannel):
	channel_message_type = 0xD
	attributes = ['value']

	def __init__(self, channel: int, value: int):
		"""Initialize a channel aftertouch message."""
		super().__init__(channel)

		self.value = value

class MessagePitchBend(BaseMessageChannel):
	channel_message_type = 0xE
	attributes = ['value_lsb', 'value_msb']

	def __init__(self, channel: int, value_lsb: int, value_msb: int):
		"""Initialize a pitch bend message."""
		super().__init__(channel)

		self.value_lsb = value_lsb
		self.value_msb = value_msb

		self.value = (value_msb << 7) | value_lsb

CHANNEL_MESSAGE_TYPES: Dict[int, Type[BaseMessageChannel]] = {
	channel_message_type.channel_message_type: channel_message_type
	for channel_message_type in [
		MessageNoteOff,
		MessageNoteOn,
		MessageAftertouch,
		MessageControlChange,
		MessageProgramChange,
		MessageChannelAftertouch,
		MessagePitchBend,
	]
}

def channel_message_from_bytes(data: bytes) -> Tuple[BaseMessageChannel, bytes]:
	"""Get a channel message from bytes."""
	message_type = data[0] >> 4

	if message_type in CHANNEL_MESSAGE_TYPES:
		return CHANNEL_MESSAGE_TYPES[message_type].from_bytes(data)

	raise ValueError(f"Invalid channel message type {message_type}")
