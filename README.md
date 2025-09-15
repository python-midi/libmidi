# libmidi

[![PyPi version](https://img.shields.io/pypi/v/libmidi)](https://pypi.org/project/libmidi/)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e9bb9f5cc25b4229aae9a02ec67b6236)](https://www.codacy.com/gh/python-midi/libmidi/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=python-midi/libmidi&amp;utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/libmidi/badge/?version=latest)](https://libmidi.readthedocs.io/en/latest/?badge=latest)

libmidi is a MIDI library written from scratch with object oriented programming and proper typing in mind, while trying to keep overhead as minimal as possible.

This is supposed to be a replacement to [Mido](https://pypi.org/project/mido/), which seems dead development-wise and it has a log of bugs.

It follows the official MIDI 1.0 specifications

Requires Python 3.8 or greater

## Installation

```sh
pip3 install libmidi
```

## Instructions
```python
# Open a file
from libmidi.types import MidiFile

MidiFile.from_file("midi.mid")
```

Complete documentation at [Read the Docs](https://libmidi.readthedocs.io)

## License

```
#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
```
