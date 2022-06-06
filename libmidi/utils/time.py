#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI time utils."""

from typing import List

from libmidi.types.event import Event

def to_abstime(events: List[Event]):
	"""Convert messages to absolute time."""
	now = 0
	for event in events:
		now += event.delta_time
		yield event.copy(delta_time=now)

def to_reltime(events: List[Event]):
	"""Convert messages to relative time."""
	now = 0
	for event in events:
		delta = event.delta_time - now
		yield event.copy(delta_time=delta)
		now = event.delta_time

def tick2second(tick, ticks_per_beat, tempo):
	"""Convert absolute time in ticks to seconds.

	Returns absolute time in seconds for a chosen MIDI file time
	resolution (ticks per beat, also called PPQN or pulses per quarter
	note) and tempo (microseconds per beat).
	"""
	scale = tempo * 1e-6 / ticks_per_beat
	return tick * scale

def second2tick(second, ticks_per_beat, tempo):
	"""Convert absolute time in seconds to ticks.

	Returns absolute time in ticks for a chosen MIDI file time
	resolution (ticks per beat, also called PPQN or pulses per quarter
	note) and tempo (microseconds per beat).
	"""
	scale = tempo * 1e-6 / ticks_per_beat
	return second / scale

def bpm2tempo(bpm):
	"""Convert beats per minute to MIDI file tempo.

	Returns microseconds per beat as an integer::

		240 => 250000
		120 => 500000
		60 => 1000000
	"""
	# One minute is 60 million microseconds.
	return int(round((60 * 1000000) / bpm))

def tempo2bpm(tempo):
	"""Convert MIDI file tempo to BPM.

	Returns BPM as an integer or float::

		250000 => 240
		500000 => 120
		1000000 => 60
	"""
	# One minute is 60 million microseconds.
	return (60 * 1000000) / tempo
