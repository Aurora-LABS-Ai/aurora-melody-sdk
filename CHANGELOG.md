# Changelog

All notable changes to Aurora Melody SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added

- Initial release of Aurora Melody SDK
- `AuroraPlugin` base class for creating plugins
- `MidiNote` class for representing MIDI notes
- `PluginContext` for accessing piano roll state
- `PluginParameter` and `ParameterType` for UI controls

#### Music Theory
- `Scale` class with 14 built-in scales (Major, Minor, Blues, Pentatonic, etc.)
- `Chord` class with 14 chord types (Major, Minor, 7ths, Sus, etc.)
- `NoteName` utility for MIDI/note name conversion

#### Utilities
- `random_walk()` - Generate melodies using random walk algorithm
- `arpeggiate()` - Create arpeggio patterns from chords
- `quantize_beat()` - Snap beats to grid
- `quantize_notes()` - Quantize note lists
- `humanize()` - Add human-like timing variations
- `remove_overlaps()` - Clean up overlapping notes

#### CLI Tools
- `aurora-pack` command for packaging plugins into `.aml` files

#### Examples
- `random-melody` - Random melody generator
- `arpeggiator` - Chord arpeggiator with patterns
- `chord-progression` - Chord progression builder

### Plugin Parameter Types
- `INT` - Integer slider with min/max/step
- `FLOAT` - Float slider with min/max/step
- `BOOL` - Toggle switch
- `CHOICE` - Dropdown selector
- `STRING` - Text input

---

## Future Plans

- [ ] MIDI file export utilities
- [ ] More pattern generators
- [ ] AI-assisted melody generation
- [ ] Real-time parameter modulation

