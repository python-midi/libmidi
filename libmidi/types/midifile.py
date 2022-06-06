#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
"""MIDI file."""

from io import BufferedReader
from pathlib import Path
import time
from typing import List, Union

from libmidi.types.event import Event
from libmidi.types.header import Header
from libmidi.types.messages.meta import BaseMessageMeta, MessageMetaEndOfTrack, MessageMetaSetTempo
from libmidi.types.track import Track
from libmidi.utils.time import tick2second, to_abstime, to_reltime

# The default tempo is 120 BPM.
# (500000 microseconds per beat (quarter note).)
DEFAULT_TEMPO = 500000
DEFAULT_TICKS_PER_BEAT = 480

class MidiFile:
	"""
	Class representing a MIDI 1.0 file.
	Complies with the standard MIDI 1.0 file format specification
	(https://www.midi.org/specifications/file-format-specifications/standard-midi-files).

	A MIDI file is a binary file containing one or more tracks.
	They're written with big-endian byte order.
	All MIDI files must start with the string 'MThd' followed by an unsigned 32 bit integer,
	which represent the number of tracks in the file.
	"""
	def __init__(self,
	             format: int = 1,
	             tracks: List[Track] = None,
	             division: int = DEFAULT_TICKS_PER_BEAT,
	            ):
		self.format = format
		self.tracks = tracks or []
		self.division = division

	def __iter__(self):
		# The tracks of type 2 files are not in sync, so they can
		# not be played back like this.
		if self.format == 2:
			raise TypeError("can't merge tracks in format 2 (asynchronous) file")

		tempo = DEFAULT_TEMPO
		for event in self.merge_tracks().events:
			# Convert message time from absolute time
			# in ticks to relative time in seconds.
			if event.delta_time > 0:
				delta = tick2second(event.delta_time, self.division, tempo)
			else:
				delta = 0

			yield event.copy(delta_time=delta)

			if isinstance(event.message, MessageMetaSetTempo):
				tempo = event.message.tempo

	@classmethod
	def from_stream(cls, stream: BufferedReader):
		tracks = []

		header = Header.from_stream(stream)

		for _ in range(header.ntrks):
			track = Track.from_stream(stream)

			tracks.append(track)

		return cls(header.format, tracks, header.division)

	@classmethod
	def from_file(cls, filename: Union[Path, str]):
		"""Read a MIDI file from a file."""
		with Path(filename).open('rb') as f:
			return cls.from_stream(f)

	def to_bytes(self):
		"""Return the MIDI file as a byte string."""
		header = Header(self.format, self.division, len(self.tracks))
		return header.to_bytes() + b''.join(track.to_bytes() for track in self.tracks)

	def to_file(self, filename: Union[Path, str]):
		"""Write the MIDI file to a file."""
		with Path(filename).open('wb') as f:
			f.write(self.to_bytes())

	def get_length(self):
		"""
		Playback time in seconds.

		This will be computed by going through every message in every
		track and adding up delta times.
		"""
		if self.format == 2:
			raise ValueError('impossible to compute length for type 2 (asynchronous) file')

		return sum(event.delta_time for event in self)

	def play(self, meta_messages: bool = False):
		"""
		Play back all tracks.

		The generator will sleep between each message by
		default. Messages are yielded with correct timing. The time
		attribute is set to the number of seconds slept since the
		previous message.

		By default you will only get normal MIDI messages. Pass
		meta_messages=True if you also want meta messages.

		You will receive copies of the original messages, so you can
		safely modify them without ruining the tracks.
		"""
		start_time = time.time()
		input_time = 0.0

		for event in self:
			input_time += event.delta_time

			playback_time = time.time() - start_time
			duration_to_next_event = input_time - playback_time

			if duration_to_next_event > 0.0:
				time.sleep(duration_to_next_event)

			if isinstance(event.message, BaseMessageMeta) and not meta_messages:
				continue
			else:
				yield event

	@staticmethod
	def _fix_end_of_track(events: List[Event]):
		"""
		Remove all end_of_track messages and add one at the end.

		This is used by merge_tracks() and MidiFile.save().
		"""
		# Accumulated delta time from removed end of track messages.
		# This is added to the next message.
		accum = 0

		for event in events:
			if isinstance(event.message, MessageMetaEndOfTrack):
				accum += event.delta_time
			else:
				if accum:
					delta = accum + event.delta_time
					yield event.copy(delta_time=delta)
					accum = 0
				else:
					yield event

		yield Event(accum, MessageMetaEndOfTrack())

	def merge_tracks(self):
		"""Returns a MidiTrack object with all messages from all tracks.

		The messages are returned in playback order with delta times
		as if they were all in one track.
		"""
		events: List[Event] = []
		for track in self.tracks:
			events.extend(to_abstime(track.events))

		events.sort(key=lambda event: event.delta_time)

		return Track(events=self._fix_end_of_track(to_reltime(events)))
