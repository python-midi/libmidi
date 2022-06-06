#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI message."""

from enum import Enum
from typing import List, Tuple

from libmidi.utils.bytes import get_data_from_bytes

class MessageType(Enum):
	CHANNEL = 0
	SYSTEM = 1
	META = 2

class BaseMessage:
	message_type: MessageType
	attributes: List[str] = []

	@classmethod
	def _assert_status_byte(cls, status_byte: int) -> None:
		raise NotImplementedError

	@classmethod
	def from_bytes(cls, data: bytes) -> Tuple['BaseMessage', bytes]:
		"""Read a message from bytes."""
		raise NotImplementedError

	def get_status_byte(self) -> int:
		"""Return the status byte of the message."""
		raise NotImplementedError

	def to_bytes(self) -> bytes:
		"""Return message as bytes."""
		raise NotImplementedError

	def copy(self, **kwargs) -> 'BaseMessage':
		for attr in self.attributes:
			if attr not in kwargs:
				kwargs[attr] = getattr(self, attr)

		return self.__class__(**kwargs)

	def __str__(self) -> str:
		return (
			f"Message type: {self.message_type.name}"
			f", length: {self.get_length()}"
			", " + ", ".join(f"{attr}: {getattr(self, attr)}" for attr in self.attributes)
		)

	def get_length(self) -> int:
		return 1

	@classmethod
	def _get_status_data(cls, data: bytes) -> Tuple[int, int, bytes]:
		status_bytes, remaining_data = get_data_from_bytes(data, 1)
		status_byte = status_bytes[0]
		cls._assert_status_byte(status_byte)
		message_type, status_data = status_byte >> 4, status_byte & 0x0F
		return message_type, status_data, remaining_data
