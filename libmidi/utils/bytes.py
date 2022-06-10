#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""bytes utils."""

from typing import Tuple

def get_data_from_bytes(data: bytes, size: int) -> Tuple[bytes, bytes]:
	"""Pop footer bytes from data and return the rest."""
	return data[:size], data[size:]
