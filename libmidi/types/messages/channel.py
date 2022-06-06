#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI channel message."""

from enum import IntEnum
import struct
from typing import Tuple

from libmidi.utils.bytes import get_data_from_bytes
from libmidi.types.messages.common import BaseMessage, MessageType

class ChannelMessageType(IntEnum):
	"""Enum of message types."""
	NOTE_OFF = 0x8
	NOTE_ON = 0x9
	AFTERTOUCH = 0xA
	CONTROL_CHANGE = 0xB
	PROGRAM_CHANGE = 0xC
	CHANNEL_AFTERTOUCH = 0xD
	PITCH_BEND = 0xE

ALL_CHANNEL_MESSAGE_TYPES = [
	ChannelMessageType.NOTE_OFF,
	ChannelMessageType.NOTE_ON,
	ChannelMessageType.AFTERTOUCH,
	ChannelMessageType.CONTROL_CHANGE,
	ChannelMessageType.PROGRAM_CHANGE,
	ChannelMessageType.CHANNEL_AFTERTOUCH,
	ChannelMessageType.PITCH_BEND,
]

class BaseMessageChannel(BaseMessage):
	"""
	Base class for channel messages.

	Since all channel messages have the same structure (at least a channel data +
	8 bit data bytes), we can commonize a lot of methods.
	"""

	message_type = MessageType.CHANNEL
	channel_message_type: ChannelMessageType

	def __init__(self, channel: int):
		self.channel = channel

	def __str__(self) -> str:
		return (
			super().__str__()
			+ f", channel message type: {self.channel_message_type.name}"
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
		status_byte, channel, remaining_data = cls._get_status_data(data)

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
	channel_message_type = ChannelMessageType.NOTE_OFF
	attributes = ['note', 'velocity']

	def __init__(self, channel: int, note: int, velocity: int):
		super().__init__(channel)

		self.note = note
		self.velocity = velocity

class MessageNoteOn(BaseMessageChannel):
	channel_message_type = ChannelMessageType.NOTE_ON
	attributes = ['note', 'velocity']

	def __init__(self, channel: int, note: int, velocity: int):
		super().__init__(channel)

		self.note = note
		self.velocity = velocity

class MessageAftertouch(BaseMessageChannel):
	channel_message_type = ChannelMessageType.AFTERTOUCH
	attributes = ['note', 'value']

	def __init__(self, channel: int, note: int, value: int):
		super().__init__(channel)

		self.note = note
		self.value = value

class MessageControlChange(BaseMessageChannel):
	channel_message_type = ChannelMessageType.CONTROL_CHANGE
	attributes = ['control', 'value']

	def __init__(self, channel: int, control: int, value: int):
		super().__init__(channel)

		self.control = control
		self.value = value

class MessageProgramChange(BaseMessageChannel):
	channel_message_type = ChannelMessageType.PROGRAM_CHANGE
	attributes = ['program']

	def __init__(self, channel: int, program: int):
		super().__init__(channel)

		self.program = program

class MessageChannelAftertouch(BaseMessageChannel):
	channel_message_type = ChannelMessageType.CHANNEL_AFTERTOUCH
	attributes = ['value']

	def __init__(self, channel: int, value: int):
		super().__init__(channel)

		self.value = value

class MessagePitchBend(BaseMessageChannel):
	channel_message_type = ChannelMessageType.PITCH_BEND
	attributes = ['value_lsb', 'value_msb']

	def __init__(self, channel: int, value_lsb: int, value_msb: int):
		super().__init__(channel)

		self.value_lsb = value_lsb
		self.value_msb = value_msb

		self.value = (value_msb << 7) | value_lsb

def channel_message_from_bytes(data: bytes) -> Tuple[BaseMessageChannel, bytes]:
	message: BaseMessage = None
	remaining_data = None

	message_status = data[0]

	message_type = message_status >> 4

	if message_type == ChannelMessageType.NOTE_OFF:
		message, remaining_data = MessageNoteOff.from_bytes(data)
	elif message_type == ChannelMessageType.NOTE_ON:
		message, remaining_data = MessageNoteOn.from_bytes(data)
	elif message_type == ChannelMessageType.AFTERTOUCH:
		message, remaining_data = MessageAftertouch.from_bytes(data)
	elif message_type == ChannelMessageType.CONTROL_CHANGE:
		message, remaining_data = MessageControlChange.from_bytes(data)
	elif message_type == ChannelMessageType.PROGRAM_CHANGE:
		message, remaining_data = MessageProgramChange.from_bytes(data)
	elif message_type == ChannelMessageType.CHANNEL_AFTERTOUCH:
		message, remaining_data = MessageChannelAftertouch.from_bytes(data)
	elif message_type == ChannelMessageType.PITCH_BEND:
		message, remaining_data = MessagePitchBend.from_bytes(data)
	else:
		raise ValueError(f"Unknown channel message type: 0x{message_type:x}")

	return message, remaining_data
