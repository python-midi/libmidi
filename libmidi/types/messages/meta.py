#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI meta message."""

from enum import IntEnum
from typing import Tuple
import struct

from libmidi.utils.bytes import get_data_from_bytes
from libmidi.types.messages.common import BaseMessage, MessageType
from libmidi.utils.variable_length import VariableInt

SYSTEM_MESSAGE_VALUE = 0xFF

class MetaMessageType(IntEnum):
	"""Enum of meta message types."""
	UNKNOWN = -1
	SEQUENCE_NUMBER = 0x00
	TEXT = 0x01
	COPYRIGHT_NOTICE = 0x02
	TRACK_NAME = 0x03
	INSTRUMENT_NAME = 0x04
	LYRIC = 0x05
	MARKER = 0x06
	CUE_POINT = 0x07
	CHANNEL_PREFIX = 0x20
	END_OF_TRACK = 0x2F
	SET_TEMPO = 0x51
	SMPTE_OFFSET = 0x54
	TIME_SIGNATURE = 0x58
	KEY_SIGNATURE = 0x59
	SEQUENCER_SPECIFIC = 0x7F

ALL_META_MESSAGE_TYPES = [
	MetaMessageType.TEXT,
	MetaMessageType.COPYRIGHT_NOTICE,
	MetaMessageType.TRACK_NAME,
	MetaMessageType.INSTRUMENT_NAME,
	MetaMessageType.LYRIC,
	MetaMessageType.MARKER,
	MetaMessageType.CUE_POINT,
	MetaMessageType.CHANNEL_PREFIX,
	MetaMessageType.END_OF_TRACK,
	MetaMessageType.SET_TEMPO,
	MetaMessageType.SMPTE_OFFSET,
	MetaMessageType.TIME_SIGNATURE,
	MetaMessageType.KEY_SIGNATURE,
	MetaMessageType.SEQUENCER_SPECIFIC,
]

class BaseMessageMeta(BaseMessage):
	message_type = MessageType.META
	meta_message_type: MetaMessageType

	def __str__(self) -> str:
		return (
			super().__str__()
			+ f", meta message type: {self.meta_message_type.name}"
		)

	@classmethod
	def _assert_status_byte(cls, status_byte: int):
		assert status_byte == SYSTEM_MESSAGE_VALUE, "Invalid status byte"

	def get_length(self) -> int:
		return super().get_length() + 1

	def get_status_byte(self) -> int:
		return 0xFF

	@classmethod
	def _get_meta_message_data(cls, data: bytes) -> Tuple[bytes, bytes]:
		status_byte, system_message_type, remaining_data = cls._get_status_data(data)

		meta_message_type, remaining_data = get_data_from_bytes(remaining_data, 1)
		meta_message_type = meta_message_type[0]

		length, remaining_data = VariableInt.from_bytes(remaining_data)

		if cls.meta_message_type != MetaMessageType.UNKNOWN:
			assert meta_message_type == cls.meta_message_type, (
				f"Expected meta message type {cls.meta_message_type.name}, got {meta_message_type}")
		elif meta_message_type in ALL_META_MESSAGE_TYPES:
			raise Exception("Using unknown meta message type on a well known type")

		data, remaining_data = get_data_from_bytes(remaining_data, length)

		return meta_message_type, data, remaining_data

	def _header_to_bytes(self) -> bytes:
		return bytes(
			struct.pack(">BB", self.get_status_byte(), self.meta_message_type.value)
			+ VariableInt.to_bytes(self.get_length() - 2)
		)

class MessageMetaSequenceNumber(BaseMessageMeta):
	meta_message_type = MetaMessageType.SEQUENCE_NUMBER
	attributes = ['sequence_number']

	def __init__(self, sequence_number: int):
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
	meta_message_type = MetaMessageType.TEXT

class MessageMetaCopyrightNotice(BaseMessageMetaText):
	meta_message_type = MetaMessageType.COPYRIGHT_NOTICE

class MessageMetaTrackName(BaseMessageMetaText):
	meta_message_type = MetaMessageType.TRACK_NAME

class MessageMetaInstrumentName(BaseMessageMetaText):
	meta_message_type = MetaMessageType.INSTRUMENT_NAME

class MessageMetaLyric(BaseMessageMetaText):
	meta_message_type = MetaMessageType.LYRIC

class MessageMetaMarker(BaseMessageMetaText):
	meta_message_type = MetaMessageType.MARKER

class MessageMetaCuePoint(BaseMessageMetaText):
	meta_message_type = MetaMessageType.CUE_POINT

class MessageMetaChannelPrefix(BaseMessageMeta):
	meta_message_type = MetaMessageType.CHANNEL_PREFIX
	attributes = ['channel_prefix']

	def __init__(self, channel_prefix: int):
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

class MessageMetaEndOfTrack(BaseMessageMeta):
	meta_message_type = MetaMessageType.END_OF_TRACK

	@classmethod
	def from_bytes(cls, data: bytes):
		meta_message_type, data, remaining_data = cls._get_meta_message_data(data)
		return cls(), remaining_data

	def to_bytes(self) -> bytes:
		return self._header_to_bytes()

class MessageMetaSetTempo(BaseMessageMeta):
	meta_message_type = MetaMessageType.SET_TEMPO
	attributes = ['tempo']

	def __init__(self, tempo: int):
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
	meta_message_type = MetaMessageType.SMPTE_OFFSET
	attributes = ['hours', 'minutes', 'seconds', 'frames', 'sub_frames']

	def __init__(self, hours: int, minutes: int, seconds: int, frames: int, sub_frames: int):
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
	meta_message_type = MetaMessageType.TIME_SIGNATURE
	attributes = [
		'numerator',
		'denominator',
		'clocks_per_metronome_click',
		'number_of_32nd_notes_per_quarter_note'
	]

	def __init__(self, numerator: int, denominator: int,
			clocks_per_metronome_click: int, number_of_32nd_notes_per_quarter_note: int):
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
	meta_message_type = MetaMessageType.KEY_SIGNATURE
	attributes = ['key_signature', 'scale']

	def __init__(self, key_signature: int, scale: int):
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
	meta_message_type = MetaMessageType.SEQUENCER_SPECIFIC
	attributes = ['data']

	def __init__(self, data: bytes):
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
	meta_message_type = MetaMessageType.UNKNOWN
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

def meta_message_from_bytes(data: bytes) -> Tuple[BaseMessageMeta, bytes]:
	"""Get a meta message object from bytes."""

	message: BaseMessageMeta = None
	remaining_data = None

	message_status = data[0]

	assert message_status == SYSTEM_MESSAGE_VALUE, "Invalid system message type"

	meta_message_type = data[1]
	try:
		meta_message_type = MetaMessageType(meta_message_type)
	except ValueError:
		meta_message_type = MetaMessageType.UNKNOWN

	if meta_message_type == MetaMessageType.TEXT:
		message, remaining_data = MessageMetaText.from_bytes(data)
	elif meta_message_type == MetaMessageType.COPYRIGHT_NOTICE:
		message, remaining_data = MessageMetaCopyrightNotice.from_bytes(data)
	elif meta_message_type == MetaMessageType.TRACK_NAME:
		message, remaining_data = MessageMetaTrackName.from_bytes(data)
	elif meta_message_type == MetaMessageType.INSTRUMENT_NAME:
		message, remaining_data = MessageMetaInstrumentName.from_bytes(data)
	elif meta_message_type == MetaMessageType.LYRIC:
		message, remaining_data = MessageMetaLyric.from_bytes(data)
	elif meta_message_type == MetaMessageType.MARKER:
		message, remaining_data = MessageMetaMarker.from_bytes(data)
	elif meta_message_type == MetaMessageType.CUE_POINT:
		message, remaining_data = MessageMetaCuePoint.from_bytes(data)
	elif meta_message_type == MetaMessageType.CHANNEL_PREFIX:
		message, remaining_data = MessageMetaChannelPrefix.from_bytes(data)
	elif meta_message_type == MetaMessageType.END_OF_TRACK:
		message, remaining_data = MessageMetaEndOfTrack.from_bytes(data)
	elif meta_message_type == MetaMessageType.SET_TEMPO:
		message, remaining_data = MessageMetaSetTempo.from_bytes(data)
	elif meta_message_type == MetaMessageType.SMPTE_OFFSET:
		message, remaining_data = MessageMetaSMPTEOffset.from_bytes(data)
	elif meta_message_type == MetaMessageType.TIME_SIGNATURE:
		message, remaining_data = MessageMetaTimeSignature.from_bytes(data)
	elif meta_message_type == MetaMessageType.KEY_SIGNATURE:
		message, remaining_data = MessageMetaKeySignature.from_bytes(data)
	elif meta_message_type == MetaMessageType.SEQUENCER_SPECIFIC:
		message, remaining_data = MessageMetaSequencerSpecific.from_bytes(data)
	elif meta_message_type == MetaMessageType.UNKNOWN:
		message, remaining_data = MessageMetaUnknown.from_bytes(data)

	return message, remaining_data
