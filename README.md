# libmidi

[![PyPi version](https://img.shields.io/pypi/v/libmidi)](https://pypi.org/project/libmidi/)

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

## License

```
#
# Copyright (C) 2022 Sebastiano Barezzi
#
# SPDX-License-Identifier: LGPL-3.0-or-later
#
```
