#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI message."""

from typing import Tuple

from libmidi.types.messages.common import BaseMessage
from libmidi.types.messages.channel import ALL_CHANNEL_MESSAGE_TYPES, channel_message_from_bytes
from libmidi.types.messages.system import ALL_SYSTEM_MESSAGE_TYPES, system_message_from_bytes
from libmidi.types.messages.meta import META_MESSAGE_VALUE, meta_message_from_bytes

def message_from_bytes(data: bytes, last_status_byte: int) -> Tuple[BaseMessage, bytes]:
	"""
	Get a message object from bytes.

	Returns the message object and the remaining bytes.
	"""
	message: BaseMessage = None
	remaining_data = None

	message_status = data[0]
	if message_status < 0x80:
		# Running status
		message_status = last_status_byte
		data = last_status_byte.to_bytes(1, 'big') + data[:]

	message_type = message_status >> 4

	if message_type in ALL_CHANNEL_MESSAGE_TYPES:
		message, remaining_data = channel_message_from_bytes(data)
	elif message_status in ALL_SYSTEM_MESSAGE_TYPES:
		message, remaining_data = system_message_from_bytes(data)
	elif message_status == META_MESSAGE_VALUE:
		message, remaining_data = meta_message_from_bytes(data)

	if not message:
		raise ValueError("Invalid message")

	return message, remaining_data
