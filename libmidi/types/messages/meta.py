#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI meta message."""

import struct
from typing import Dict, Tuple, Type

from libmidi.utils.bytes import get_data_from_bytes
from libmidi.types.messages.common import BaseMessage
from libmidi.utils.variable_length import VariableInt

META_MESSAGE_VALUE = 0xFF

class BaseMessageMeta(BaseMessage):
	"""Base class for all meta messages."""
	meta_message_type: int

	def __str__(self) -> str:
		"""Return a string representation of the message."""
		return (
			super().__str__()
			+ f", meta message type: {self.meta_message_type.name}"
		)

	@classmethod
	def _assert_status_byte(cls, status_byte: int):
		assert status_byte == META_MESSAGE_VALUE, "Invalid status byte"

	def get_length(self) -> int:
		return super().get_length() + 1

	def get_status_byte(self) -> int:
		return META_MESSAGE_VALUE

	@classmethod
	def _get_meta_message_data(cls, data: bytes) -> Tuple[bytes, bytes]:
		_, _, remaining_data = cls._get_status_data(data)

		meta_message_type, remaining_data = get_data_from_bytes(remaining_data, 1)
		meta_message_type = meta_message_type[0]

		length, remaining_data = VariableInt.from_bytes(remaining_data)

		if cls.meta_message_type != -1:
			assert meta_message_type == cls.meta_message_type, (
				f"Expected meta message type {hex(cls.meta_message_type)}, got {hex(meta_message_type)}")
		elif meta_message_type in META_MESSAGE_TYPES:
			raise Exception("Using unknown meta message type on a well known type")

		data, remaining_data = get_data_from_bytes(remaining_data, length)

		return meta_message_type, data, remaining_data

	def _header_to_bytes(self) -> bytes:
		return bytes(
			struct.pack(">BB", self.get_status_byte(), self.meta_message_type.value)
			+ VariableInt.to_bytes(self.get_length() - 2)
		)

class MessageMetaSequenceNumber(BaseMessageMeta):
	meta_message_type = 0x00
	attributes = ['sequence_number']

	def __init__(self, sequence_number: int):
		"""Initialize a meta sequence message."""
		self.sequence_number = sequence_number

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		assert len(data) == 2, f"Expected 2 bytes, got {len(data)}"
		sequence_number = int.from_bytes(data, 'big', signed=False)
		return cls(sequence_number), remaining_data

	def get_length(self) -> int:
		return super().get_length() + 2

	def to_bytes(self) -> bytes:
		return (
			self._header_to_bytes()
			+ self.sequence_number.to_bytes(2, 'big')
		)

class BaseMessageMetaText(BaseMessageMeta):
	"""Base class for meta messages with text."""
	attributes = ['text']

	def __init__(self, text: str):
		"""Initialize a meta text message."""
		self.text = text

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		text = data.decode('ASCII', errors='ignore')
		return cls(text), remaining_data

	def get_length(self):
		return super().get_length() + len(self.text.encode('ASCII'))

	def to_bytes(self) -> bytes:
		return (
			self._header_to_bytes()
			+ self.text.encode('ASCII')
		)

class MessageMetaText(BaseMessageMetaText):
	meta_message_type = 0x01

class MessageMetaCopyrightNotice(BaseMessageMetaText):
	meta_message_type = 0x02

class MessageMetaTrackName(BaseMessageMetaText):
	meta_message_type = 0x03

class MessageMetaInstrumentName(BaseMessageMetaText):
	meta_message_type = 0x04

class MessageMetaLyric(BaseMessageMetaText):
	meta_message_type = 0x05

class MessageMetaMarker(BaseMessageMetaText):
	meta_message_type = 0x06

class MessageMetaCuePoint(BaseMessageMetaText):
	meta_message_type = 0x07

class MessageMetaChannelPrefix(BaseMessageMeta):
	meta_message_type = 0x20
	attributes = ['channel_prefix']

	def __init__(self, channel_prefix: int):
		"""Initialize a meta channel prefix message."""
		self.channel_prefix = channel_prefix

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		assert len(data) == 1, f"Expected 1 byte, got {len(data)}"
		channel_prefix = int.from_bytes(data, 'big', signed=False)
		return cls(channel_prefix), remaining_data

	def get_length(self) -> int:
		return super().get_length() + 1

	def to_bytes(self) -> bytes:
		return (
			self._header_to_bytes()
			+ self.channel_prefix.to_bytes(1, 'big')
		)

class MessageMetaPortPrefix(BaseMessageMeta):
	meta_message_type = 0x21
	attributes = ['port_prefix']

	def __init__(self, port_prefix: int):
		"""Initialize a meta port prefix message."""
		self.port_prefix = port_prefix

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		assert len(data) == 1, f"Expected 1 byte, got {len(data)}"
		port_prefix = int.from_bytes(data, 'big', signed=False)
		return cls(port_prefix), remaining_data

	def get_length(self) -> int:
		return super().get_length() + 1

	def to_bytes(self) -> bytes:
		return (
			self._header_to_bytes()
			+ self.port_prefix.to_bytes(1, 'big')
		)

class MessageMetaEndOfTrack(BaseMessageMeta):
	meta_message_type = 0x2F

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		return cls(), remaining_data

	def to_bytes(self) -> bytes:
		return self._header_to_bytes()

class MessageMetaSetTempo(BaseMessageMeta):
	meta_message_type = 0x51
	attributes = ['tempo']

	def __init__(self, tempo: int):
		"""Initialize a meta set tempo message."""
		self.tempo = tempo

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		assert len(data) == 3, f"Expected 3 bytes, got {len(data)}"
		tempo = int.from_bytes(data, 'big', signed=False)
		return cls(tempo), remaining_data

	def get_length(self) -> int:
		return super().get_length() + 3

	def to_bytes(self) -> bytes:
		return (
			self._header_to_bytes()
			+ self.tempo.to_bytes(3, 'big', signed=False)
		)

class MessageMetaSMPTEOffset(BaseMessageMeta):
	meta_message_type = 0x54
	attributes = ['hours', 'minutes', 'seconds', 'frames', 'sub_frames']

	def __init__(self, hours: int, minutes: int, seconds: int, frames: int, sub_frames: int):
		"""Initialize a meta SMPTE offset message."""
		self.hours = hours
		self.minutes = minutes
		self.seconds = seconds
		self.frames = frames
		self.sub_frames = sub_frames

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		assert len(data) == 5, f"Expected 5 bytes, got {len(data)}"
		return cls(*struct.unpack('>BBBBB', data)), remaining_data

	def get_length(self) -> int:
		return super().get_length() + 5

	def to_bytes(self) -> bytes:
		return (
			self._header_to_bytes()
			+ struct.pack('>BBBBB', self.hours, self.minutes, self.seconds, self.frames, self.sub_frames)
		)

class MessageMetaTimeSignature(BaseMessageMeta):
	meta_message_type = 0x58
	attributes = [
		'numerator',
		'denominator',
		'clocks_per_metronome_click',
		'number_of_32nd_notes_per_quarter_note'
	]

	def __init__(self, numerator: int, denominator: int,
			clocks_per_metronome_click: int, number_of_32nd_notes_per_quarter_note: int):
		"""Initialize a meta time signature message."""
		self.numerator = numerator
		self.denominator = denominator
		self.clocks_per_metronome_click = clocks_per_metronome_click
		self.number_of_32nd_notes_per_quarter_note = number_of_32nd_notes_per_quarter_note

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		assert len(data) == 4, f"Expected 4 bytes, got {len(data)}"
		return cls(*struct.unpack('>BBBB', data)), remaining_data

	def get_length(self) -> int:
		return super().get_length() + 4

	def to_bytes(self) -> bytes:
		return (
			self._header_to_bytes()
			+ struct.pack('>BBBB', self.numerator, self.denominator,
					self.clocks_per_metronome_click, self.number_of_32nd_notes_per_quarter_note)
		)

class MessageMetaKeySignature(BaseMessageMeta):
	meta_message_type = 0x59
	attributes = ['key_signature', 'scale']

	def __init__(self, key_signature: int, scale: int):
		"""Initialize a meta key signature message."""
		self.key_signature = key_signature
		self.scale = scale

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		assert len(data) == 2, f"Expected 2 bytes, got {len(data)}"
		return cls(*struct.unpack('>BB', data)), remaining_data
	
	def get_length(self) -> int:
		return super().get_length() + 2

	def to_bytes(self) -> bytes:
		return (
			self._header_to_bytes()
			+ struct.pack('>BB', self.key_signature, self.scale)
		)

class MessageMetaSequencerSpecific(BaseMessageMeta):
	meta_message_type = 0x7F
	attributes = ['data']

	def __init__(self, data: bytes):
		"""Initialize a meta sequencer specific message."""
		self.data = data

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		return cls(data), remaining_data

	def get_length(self) -> int:
		return super().get_length() + len(self.data)

	def to_bytes(self) -> bytes:
		return self._header_to_bytes() + self.data

class MessageMetaUnknown(BaseMessageMeta):
	meta_message_type = -1
	attributes = ['type_byte', 'data']

	def __init__(self, type_byte: int, data: bytes):
		self.type_byte = type_byte
		self.data = data

	def _header_to_bytes(self) -> bytes:
		return (
			bytes(struct.pack(">BB", self.get_status_byte(), self.type_byte))
			+ bytes(VariableInt.to_bytes(self.get_length() - 2))
		)

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		return cls(meta_message_type, data), remaining_data

	def get_length(self) -> int:
		return super().get_length() + len(self.data)

	def to_bytes(self) -> bytes:
		return self._header_to_bytes() + self.data

META_MESSAGE_TYPES: Dict[int, Type[BaseMessageMeta]] = {
	message_meta_type.meta_message_type: message_meta_type
	for message_meta_type in [
		MessageMetaSequenceNumber,
		MessageMetaText,
		MessageMetaCopyrightNotice,
		MessageMetaTrackName,
		MessageMetaInstrumentName,
		MessageMetaLyric,
		MessageMetaMarker,
		MessageMetaCuePoint,
		MessageMetaChannelPrefix,
		MessageMetaPortPrefix,
		MessageMetaEndOfTrack,
		MessageMetaSetTempo,
		MessageMetaSMPTEOffset,
		MessageMetaTimeSignature,
		MessageMetaKeySignature,
		MessageMetaSequencerSpecific,
	]
}

def meta_message_from_bytes(data: bytes) -> Tuple[BaseMessageMeta, bytes]:
	"""Get a meta message object from bytes."""
	assert data[0] == META_MESSAGE_VALUE, "Invalid meta message type"

	if data[1] in META_MESSAGE_TYPES:
		return META_MESSAGE_TYPES[data[1]].from_bytes(data)

	return MessageMetaUnknown.from_bytes(data)
