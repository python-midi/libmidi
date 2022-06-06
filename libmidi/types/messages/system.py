#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI system message."""

from enum import IntEnum
from typing import Tuple

from libmidi.utils.bytes import get_data_from_bytes
from libmidi.types.messages.common import BaseMessage, MessageType

SYSTEM_MESSAGE_VALUE = 0xF

class SystemMessageType(IntEnum):
	"""Enum of system message types."""
	SYSTEM_EXCLUSIVE = 0x0
	TIME_CODE_QUARTER_FRAME = 0x1
	SONG_POSITION_POINTER = 0x2
	SONG_SELECT = 0x3
	TUNE_REQUEST = 0x6
	END_OF_EXCLUSIVE = 0x7

ALL_SYSTEM_MESSAGE_TYPES = [
	SystemMessageType.SYSTEM_EXCLUSIVE,
	SystemMessageType.TIME_CODE_QUARTER_FRAME,
	SystemMessageType.SONG_POSITION_POINTER,
	SystemMessageType.SONG_SELECT,
	SystemMessageType.TUNE_REQUEST,
]

class BaseMessageSystem(BaseMessage):
	message_type = MessageType.SYSTEM
	system_message_type: SystemMessageType

	def __str__(self) -> str:
		return (
			super().__str__()
			+ f", system message type: {self.system_message_type.name}"
		)

	def get_status_byte(self):
		return (self.message_type << 4) | self.system_message_type

	@classmethod
	def _assert_status_byte(cls, status_byte: int):
		assert status_byte == (cls.message_type << 4) | cls.system_message_type, (
				"Invalid channel message type")

	@classmethod
	def _check_system_message_type(cls, system_message_type: int) -> bool:
		assert system_message_type == cls.system_message_type, "Invalid system message type"

class MessageSystemExclusive(BaseMessageSystem):
	system_message_type = SystemMessageType.SYSTEM_EXCLUSIVE
	attributes = ["data"]

	def __init__(self, data: bytes):
		self.data = data

	def get_length(self) -> int:
		return super().get_length() + len(self.data)

	@classmethod
	def from_bytes(cls, data: bytes):
		status_byte, system_message_type, remaining_data = cls._get_status_data(data)
		cls._check_system_message_type(system_message_type)

		data_length = 0
		while remaining_data[data_length] != SystemMessageType.END_OF_EXCLUSIVE:
			data_length += 1

		data, remaining_data = get_data_from_bytes(remaining_data, data_length + 1)

		return cls(data[:-1]), remaining_data

	def to_bytes(self) -> bytes:
		return bytes([self.get_status_byte()]) + self.data + bytes([SystemMessageType.END_OF_EXCLUSIVE])

class MessageSystemTimeCodeQuarterFrame(BaseMessageSystem):
	system_message_type = SystemMessageType.TIME_CODE_QUARTER_FRAME
	attributes = ["timecode_message_type", "values"]

	def __init__(self, timecode_message_type: int, values: int):
		self.timecode_message_type = timecode_message_type
		self.values = values

	@classmethod
	def from_bytes(cls, data: bytes):
		status_byte, system_message_type, remaining_data = cls._get_status_data(data)
		cls._check_system_message_type(system_message_type)

		data, remaining_data = get_data_from_bytes(remaining_data, 1)
		data = data[0]

		timecode_message_type, values = data >> 4, data & 0x0F

		return cls(timecode_message_type, values), remaining_data

	def to_bytes(self) -> bytes:
		return bytes([self.get_status_byte(), (self.timecode_message_type << 4) | self.values])

class MessageSystemSongPositionPointer(BaseMessageSystem):
	system_message_type = SystemMessageType.SONG_POSITION_POINTER
	attributes = ["position"]

	def __init__(self, position: int):
		self.position = position

	@classmethod
	def from_bytes(cls, data: bytes):
		status_byte, system_message_type, remaining_data = cls._get_status_data(data)
		cls._check_system_message_type(system_message_type)

		data, remaining_data = get_data_from_bytes(remaining_data, 2)
		position = data[0] | (data[1] << 7)

		return cls(position), remaining_data

	def to_bytes(self) -> bytes:
		return bytes([self.get_status_byte(), self.position & 0x7F, (self.position >> 7) & 0x7F])

class MessageSystemSongSelect(BaseMessageSystem):
	system_message_type = SystemMessageType.SONG_SELECT
	attributes = ["song_number"]

	def __init__(self, song_number: int):
		self.song_number = song_number

	@classmethod
	def from_bytes(cls, data: bytes):
		status_byte, system_message_type, remaining_data = cls._get_status_data(data)
		cls._check_system_message_type(system_message_type)

		data, remaining_data = get_data_from_bytes(remaining_data, 1)
		song_number = (data[0] << 7)

		return cls(song_number), remaining_data

	def to_bytes(self) -> bytes:
		return bytes([self.get_status_byte(), self.song_number & 0x7F])

class MessageSystemTuneRequest(BaseMessageSystem):
	system_message_type = SystemMessageType.TUNE_REQUEST

	@classmethod
	def from_bytes(cls, data: bytes):
		status_byte, system_message_type, remaining_data = cls._get_status_data(data)
		cls._check_system_message_type(system_message_type)

		return cls(), remaining_data

	def to_bytes(self) -> bytes:
		return bytes([self.get_status_byte()])

def system_message_from_bytes(data: bytes) -> Tuple[BaseMessageSystem, bytes]:
	message: BaseMessage = None
	remaining_data = None

	message_status = data[0]

	message_type, system_message_type = message_status >> 4, message_status & 0x0F

	assert message_type == SYSTEM_MESSAGE_VALUE, "Invalid message type"

	if system_message_type == SystemMessageType.SYSTEM_EXCLUSIVE:
		message, remaining_data = MessageSystemExclusive.from_bytes(data)
	elif system_message_type == SystemMessageType.TIME_CODE_QUARTER_FRAME:
		message, remaining_data = MessageSystemTimeCodeQuarterFrame.from_bytes(data)
	elif system_message_type == SystemMessageType.SONG_POSITION_POINTER:
		message, remaining_data = MessageSystemSongPositionPointer.from_bytes(data)
	elif system_message_type == SystemMessageType.SONG_SELECT:
		message, remaining_data = MessageSystemSongSelect.from_bytes(data)
	elif system_message_type == SystemMessageType.TUNE_REQUEST:
		message, remaining_data = MessageSystemTuneRequest.from_bytes(data)
	else:
		raise ValueError(f"Invalid system message type {system_message_type}")

	return message, remaining_data
