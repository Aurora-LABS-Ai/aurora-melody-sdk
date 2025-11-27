# Aurora Melody SDK

A professional Python SDK for creating melody generation plugins for **Aurora Melody** - the hardware-style piano roll.

## Features

- Simple Python API for generating MIDI notes
- Built-in music theory (scales, chords, note names)
- Hardware-style UI controls (sliders, dropdowns)
- Utility functions for pattern generation
- CLI tool for packaging plugins

## Installation

```bash
pip install aurora-melody-sdk
```

Or install from source:

```bash
git clone https://github.com/aurora-melody/sdk.git
cd aurora-melody-sdk
pip install -e .
```

## Quick Start

Create a simple melody generator plugin:

```python
from aurora_melody_sdk import (
    AuroraPlugin, MidiNote, Scale,
    PluginParameter, ParameterType
)
import random

class MyMelodyGenerator(AuroraPlugin):
    name = "My Melody Generator"
    author = "Your Name"
    version = "1.0.0"
    description = "Generates random melodies"
    
    # Define UI parameters (optional)
    parameters = [
        PluginParameter(
            id="num_notes",
            name="Number of Notes",
            param_type=ParameterType.INT,
            default=8,
            min_value=1,
            max_value=64
        ),
        PluginParameter(
            id="scale",
            name="Scale",
            param_type=ParameterType.CHOICE,
            default="Major",
            choices=["Major", "Minor", "Blues", "Pentatonic"]
        ),
    ]
    
    def generate(self, context):
        notes = []
        
        # Get parameter values from UI
        num_notes = context.get_int_param("num_notes", 8)
        scale_name = context.get_str_param("scale", "Major")
        
        # Get scale notes
        scale = getattr(Scale, scale_name.upper(), Scale.MAJOR)
        scale_notes = Scale.get_notes(60, scale, octaves=2)
        
        # Generate notes
        start = context.playhead_position
        for i in range(num_notes):
            notes.append(MidiNote(
                note_number=random.choice(scale_notes),
                start_beat=start + i * 0.5,
                length_beats=0.5,
                velocity=random.randint(70, 100)
            ))
        
        return notes
```

## Creating a Plugin

### 1. Create Plugin Folder

```
my-plugin/
  manifest.json
  main.py
  icon.png (optional)
```

### 2. Create manifest.json

```json
{
  "id": "com.yourname.my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "description": "Does something amazing",
  "entry": "main.py",
  "icon": "icon.png",
  "tags": ["melody", "generator"],
  "hasUI": true,
  "parameters": [
    {
      "id": "num_notes",
      "name": "Number of Notes",
      "type": "int",
      "default": 8,
      "min": 1,
      "max": 64
    },
    {
      "id": "scale",
      "name": "Scale",
      "type": "choice",
      "default": "Major",
      "choices": ["Major", "Minor", "Blues", "Pentatonic"]
    }
  ]
}
```

### 3. Create main.py

```python
from aurora_melody_sdk import AuroraPlugin, MidiNote

class MyPlugin(AuroraPlugin):
    name = "My Plugin"
    author = "Your Name"
    version = "1.0.0"
    
    def generate(self, context):
        # Generate your notes here
        return [MidiNote(60, 0.0, 1.0, 100)]
```

### 4. Package the Plugin

```bash
aurora-pack ./my-plugin
# Creates: my-plugin.aml
```

### 5. Install in Aurora Melody

Drag the `.aml` file into Aurora Melody!

---

## Plugin Parameters (UI Controls)

Define parameters in your manifest.json or as class attributes. Aurora Melody renders these as hardware-style controls.

### Parameter Types

| Type | UI Control | Description |
|------|-----------|-------------|
| `int` | Slider with LCD readout | Integer values with min/max |
| `float` | Slider with LCD readout | Decimal values with min/max |
| `bool` | Toggle switch | On/Off values |
| `choice` | Dropdown selector | Select from predefined options |
| `string` | Text input | Free-form text entry |

### manifest.json Format

```json
{
  "parameters": [
    {
      "id": "unique_id",
      "name": "Display Name",
      "type": "int|float|bool|choice|string",
      "default": 8,
      "min": 1,
      "max": 100,
      "step": 1,
      "choices": ["Option1", "Option2"],
      "description": "Tooltip text"
    }
  ]
}
```

### Python Class Format

```python
from aurora_melody_sdk import AuroraPlugin, PluginParameter, ParameterType

class MyPlugin(AuroraPlugin):
    parameters = [
        # Integer slider
        PluginParameter(
            id="num_notes",
            name="Number of Notes",
            param_type=ParameterType.INT,
            default=8,
            min_value=1,
            max_value=64,
            step=1,
            description="How many notes to generate"
        ),
        
        # Float slider
        PluginParameter(
            id="note_length",
            name="Note Length",
            param_type=ParameterType.FLOAT,
            default=0.5,
            min_value=0.125,
            max_value=4.0,
            step=0.125,
            description="Length of each note in beats"
        ),
        
        # Dropdown choice
        PluginParameter(
            id="scale",
            name="Scale",
            param_type=ParameterType.CHOICE,
            default="Major",
            choices=["Major", "Minor", "Blues", "Pentatonic", "Dorian", "Mixolydian"],
            description="Musical scale to use"
        ),
        
        # Boolean toggle
        PluginParameter(
            id="humanize",
            name="Humanize",
            param_type=ParameterType.BOOL,
            default=True,
            description="Add human-like timing variations"
        ),
        
        # String input
        PluginParameter(
            id="pattern",
            name="Pattern",
            param_type=ParameterType.STRING,
            default="1-2-3-4",
            description="Custom note pattern"
        ),
    ]
```

### Accessing Parameters in generate()

```python
def generate(self, context):
    # Get integer parameter
    num_notes = context.get_int_param("num_notes", 8)
    
    # Get float parameter
    note_length = context.get_float_param("note_length", 0.5)
    
    # Get string/choice parameter
    scale_name = context.get_str_param("scale", "Major")
    
    # Get boolean parameter
    humanize = context.get_bool_param("humanize", True)
    
    # Get any parameter with auto-conversion
    pattern = context.parameters.get("pattern", "1-2-3-4")
```

---

## API Reference

### MidiNote

Represents a MIDI note:

```python
note = MidiNote(
    note_number=60,      # MIDI note (60 = C4)
    start_beat=0.0,      # Start position in beats
    length_beats=1.0,    # Duration in beats
    velocity=100,        # Velocity (0-127)
    channel=1            # MIDI channel (1-16)
)

# Properties
note.note_name          # "C4"
note.end_beat           # 1.0 (start + length)

# Methods
note.transpose(5)       # New note 5 semitones up
note.shift(4.0)         # New note 4 beats later
note.to_dict()          # Convert to dictionary
```

### Scale

Musical scales:

```python
from aurora_melody_sdk import Scale

# Available scales
Scale.MAJOR              # [0, 2, 4, 5, 7, 9, 11]
Scale.MINOR              # [0, 2, 3, 5, 7, 8, 10]
Scale.HARMONIC_MINOR     # [0, 2, 3, 5, 7, 8, 11]
Scale.MELODIC_MINOR      # [0, 2, 3, 5, 7, 9, 11]
Scale.PENTATONIC_MAJOR   # [0, 2, 4, 7, 9]
Scale.PENTATONIC_MINOR   # [0, 3, 5, 7, 10]
Scale.BLUES              # [0, 3, 5, 6, 7, 10]
Scale.DORIAN             # [0, 2, 3, 5, 7, 9, 10]
Scale.PHRYGIAN           # [0, 1, 3, 5, 7, 8, 10]
Scale.LYDIAN             # [0, 2, 4, 6, 7, 9, 11]
Scale.MIXOLYDIAN         # [0, 2, 4, 5, 7, 9, 10]
Scale.LOCRIAN            # [0, 1, 3, 5, 6, 8, 10]
Scale.WHOLE_TONE         # [0, 2, 4, 6, 8, 10]
Scale.CHROMATIC          # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

# Get scale notes starting from root
notes = Scale.get_notes(60, Scale.MAJOR)           # [60, 62, 64, 65, 67, 69, 71]
notes = Scale.get_notes(60, Scale.BLUES, octaves=2) # Two octaves
```

### Chord

Musical chords:

```python
from aurora_melody_sdk import Chord

# Available chords
Chord.MAJOR              # [0, 4, 7]
Chord.MINOR              # [0, 3, 7]
Chord.DIMINISHED         # [0, 3, 6]
Chord.AUGMENTED          # [0, 4, 8]
Chord.MAJOR_7            # [0, 4, 7, 11]
Chord.MINOR_7            # [0, 3, 7, 10]
Chord.DOMINANT_7         # [0, 4, 7, 10]
Chord.DIMINISHED_7       # [0, 3, 6, 9]
Chord.HALF_DIMINISHED_7  # [0, 3, 6, 10]
Chord.SUS2               # [0, 2, 7]
Chord.SUS4               # [0, 5, 7]
Chord.ADD9               # [0, 4, 7, 14]
Chord.MAJOR_9            # [0, 4, 7, 11, 14]
Chord.MINOR_9            # [0, 3, 7, 10, 14]

# Get chord notes
notes = Chord.get_notes(60, Chord.MAJOR)           # [60, 64, 67]
notes = Chord.get_notes(60, Chord.DOMINANT_7)      # [60, 64, 67, 70]

# Get chord inversion
notes = Chord.get_inversion(60, Chord.MAJOR, 1)    # First inversion [64, 67, 72]
notes = Chord.get_inversion(60, Chord.MAJOR, 2)    # Second inversion [67, 72, 76]
```

### NoteName

Note name utilities:

```python
from aurora_melody_sdk import NoteName

NoteName.to_midi("C4")      # 60
NoteName.to_midi("F#5")     # 78
NoteName.to_midi("Bb3")     # 58
NoteName.from_midi(60)      # "C4"
NoteName.from_midi(78)      # "F#5"
NoteName.transpose("C4", 5) # "F4"
```

### PluginContext

Context passed to your `generate()` method:

```python
def generate(self, context):
    # Existing notes in piano roll
    for note in context.notes:
        print(f"{note.note_name} at {note.start_beat}")
    
    # IDs of selected notes
    selected = context.selected_note_ids
    
    # Current playhead position (beats)
    start = context.playhead_position
    
    # Current tempo (BPM)
    bpm = context.tempo_bpm
    
    # User parameters
    num = context.get_int_param("num_notes", 8)
    scale = context.get_str_param("scale", "Major")
    length = context.get_float_param("note_length", 0.5)
    humanize = context.get_bool_param("humanize", True)
```

---

## Utility Functions

### random_walk

Generate a melody using random walk algorithm:

```python
from aurora_melody_sdk import random_walk, Scale

notes = random_walk(
    start_note=60,           # Starting MIDI note
    num_notes=16,            # Number of notes to generate
    scale=Scale.MAJOR,       # Scale to use
    root=60,                 # Scale root
    step_range=(-3, 3),      # Max interval in scale degrees
    start_beat=0.0,          # Starting beat position
    note_length=0.5,         # Note duration
    velocity_range=(70, 100) # Velocity range
)
```

### arpeggiate

Create arpeggio patterns from chord notes:

```python
from aurora_melody_sdk import arpeggiate, Chord

chord_notes = Chord.get_notes(60, Chord.MAJOR)

notes = arpeggiate(
    notes=chord_notes,       # Notes to arpeggiate
    pattern="up",            # "up", "down", "updown", "downup", "random"
    total_beats=4.0,         # Total duration
    note_length=0.25,        # Individual note length
    start_beat=0.0,          # Starting position
    velocity=100             # Note velocity
)
```

### quantize_beat / quantize_notes

Snap notes to grid:

```python
from aurora_melody_sdk import quantize_beat, quantize_notes

# Single beat value
q = quantize_beat(1.37, 0.25)  # Returns 1.25 (16th notes)

# Common resolutions:
# 0.0625 = 1/64 notes
# 0.125 = 1/32 notes
# 0.25 = 1/16 notes
# 0.5 = 1/8 notes
# 1.0 = 1/4 notes

# Quantize list of notes
quantized = quantize_notes(notes, resolution=0.25, quantize_length=True)
```

### humanize

Add human-like timing variations:

```python
from aurora_melody_sdk import humanize

humanized = humanize(
    notes=notes,
    timing_variance=0.02,    # Max timing offset in beats
    velocity_variance=10,    # Max velocity offset
    length_variance=0.01     # Max length offset
)
```

---

## Command Line Tools

### aurora-pack

Package plugins into `.aml` files:

```bash
# Basic usage
aurora-pack ./my-plugin

# Specify output location
aurora-pack ./my-plugin -o ./dist/my-plugin.aml

# Quiet mode (no output)
aurora-pack ./my-plugin -q

# Show help
aurora-pack --help
```

---

## Examples

See the `examples/` folder for complete plugin examples:

| Plugin | Description |
|--------|-------------|
| **random-melody** | Random melody generator with scale selection |
| **arpeggiator** | Chord arpeggiator with pattern options |
| **chord-progression** | Chord progression builder |

---

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Format Code

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Links

- [GitHub Repository](https://github.com/aurora-melody/sdk)
- [Issue Tracker](https://github.com/aurora-melody/sdk/issues)
- [Documentation](https://github.com/aurora-melody/sdk#readme)
