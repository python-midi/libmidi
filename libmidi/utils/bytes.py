#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""bytes utils."""

def get_data_from_bytes(data: bytes, size: int):
	return data[:size], data[size:]
