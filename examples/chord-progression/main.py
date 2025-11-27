"""
Chord Progression Builder for Aurora Melody
============================================

Generates common chord progressions in different keys and styles.
"""

import random
import sys
import os

# Add SDK to path
sdk_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'sdk', 'python')
if sdk_path not in sys.path:
    sys.path.insert(0, sdk_path)

try:
    from aurora_sdk import AuroraPlugin, MidiNote, Chord, Scale
except ImportError:
    class MidiNote:
        def __init__(self, note_number=60, start_beat=0.0, length_beats=1.0, velocity=100, channel=1):
            self.note_number = note_number
            self.start_beat = start_beat
            self.length_beats = length_beats
            self.velocity = velocity
            self.channel = channel
    
    class AuroraPlugin:
        pass
    
    class Chord:
        MAJOR = [0, 4, 7]
        MINOR = [0, 3, 7]
        DIMINISHED = [0, 3, 6]
        MAJOR_7 = [0, 4, 7, 11]
        MINOR_7 = [0, 3, 7, 10]
        DOMINANT_7 = [0, 4, 7, 10]


class ChordProgressionPlugin(AuroraPlugin):
    """
    Generate chord progressions using common patterns.
    """
    
    name = "Chord Progression Builder"
    author = "Aurora Melody Labs"
    version = "1.0.0"
    description = "Generate chord progressions in various styles"
    
    # Common progressions (scale degrees, 1-indexed)
    PROGRESSIONS = {
        "Pop (I-V-vi-IV)": [(1, "major"), (5, "major"), (6, "minor"), (4, "major")],
        "Jazz (ii-V-I)": [(2, "minor7"), (5, "dom7"), (1, "major7")],
        "Blues (I-IV-I-V)": [(1, "dom7"), (4, "dom7"), (1, "dom7"), (5, "dom7")],
        "Rock (I-IV-V)": [(1, "major"), (4, "major"), (5, "major")],
        "Sad (vi-IV-I-V)": [(6, "minor"), (4, "major"), (1, "major"), (5, "major")],
        "Epic (I-III-IV-iv)": [(1, "major"), (3, "major"), (4, "major"), (4, "minor")],
        "Funk (I-I-IV-I)": [(1, "dom7"), (1, "dom7"), (4, "dom7"), (1, "dom7")],
        "Classical (I-IV-V-I)": [(1, "major"), (4, "major"), (5, "major"), (1, "major")],
        "Dorian (i-IV-i-V)": [(1, "minor"), (4, "major"), (1, "minor"), (5, "major")],
        "Random": None  # Special case
    }
    
    # Scale degrees to semitone offsets (major scale)
    SCALE_DEGREES = {1: 0, 2: 2, 3: 4, 4: 5, 5: 7, 6: 9, 7: 11}
    
    parameters = [
        {
            "id": "key",
            "name": "Key",
            "type": "choice",
            "choices": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
            "default": "C"
        },
        {
            "id": "octave",
            "name": "Octave",
            "type": "int",
            "min": 2,
            "max": 5,
            "default": 3
        },
        {
            "id": "progression",
            "name": "Progression",
            "type": "choice",
            "choices": list(PROGRESSIONS.keys()),
            "default": "Pop (I-V-vi-IV)"
        },
        {
            "id": "chord_duration",
            "name": "Chord Duration",
            "type": "choice",
            "choices": ["1 bar", "2 bars", "Half bar"],
            "default": "1 bar"
        },
        {
            "id": "style",
            "name": "Style",
            "type": "choice",
            "choices": ["Block", "Broken", "Power (5ths only)"],
            "default": "Block"
        },
        {
            "id": "inversions",
            "name": "Use Inversions",
            "type": "choice",
            "choices": ["No", "Yes"],
            "default": "No"
        },
        {
            "id": "repeats",
            "name": "Repeats",
            "type": "int",
            "min": 1,
            "max": 4,
            "default": 2
        }
    ]
    
    def __init__(self):
        self.note_names = {
            "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5,
            "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
        }
        
        self.chord_intervals = {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "major7": [0, 4, 7, 11],
            "minor7": [0, 3, 7, 10],
            "dom7": [0, 4, 7, 10],
            "dim": [0, 3, 6],
            "aug": [0, 4, 8],
            "sus4": [0, 5, 7],
            "power": [0, 7]  # Power chord
        }
    
    def get_chord_notes(self, root: int, chord_type: str, inversion: int = 0) -> list:
        """Get MIDI notes for a chord."""
        intervals = self.chord_intervals.get(chord_type, self.chord_intervals["major"])
        
        notes = [root + i for i in intervals]
        
        # Apply inversion
        if inversion > 0 and len(notes) > 1:
            for _ in range(inversion % len(notes)):
                notes[0] += 12
                notes = notes[1:] + [notes[0]]
        
        return notes
    
    def generate_random_progression(self) -> list:
        """Generate a random chord progression."""
        progressions = [
            [(1, "major"), (4, "major"), (5, "major"), (1, "major")],
            [(1, "minor"), (4, "minor"), (5, "minor"), (1, "minor")],
            [(1, "major"), (6, "minor"), (4, "major"), (5, "major")],
            [(2, "minor"), (5, "major"), (1, "major"), (6, "minor")],
            [(1, "major"), (5, "major"), (6, "minor"), (3, "minor")],
        ]
        return random.choice(progressions)
    
    def generate(self, context):
        """Generate chord progression notes."""
        
        # Get parameters
        params = context if isinstance(context, dict) else {}
        if hasattr(context, 'parameters'):
            params = context.parameters
        
        key_name = params.get('key', 'C')
        octave = int(params.get('octave', 3))
        progression_name = params.get('progression', 'Pop (I-V-vi-IV)')
        chord_duration_name = params.get('chord_duration', '1 bar')
        style = params.get('style', 'Block')
        use_inversions = params.get('inversions', 'No') == 'Yes'
        repeats = int(params.get('repeats', 2))
        
        # Convert key to MIDI root
        key_offset = self.note_names.get(key_name, 0)
        root_midi = (octave + 1) * 12 + key_offset  # C3 = 48
        
        # Get progression
        if progression_name == "Random":
            progression = self.generate_random_progression()
        else:
            progression = self.PROGRESSIONS.get(progression_name, self.PROGRESSIONS["Pop (I-V-vi-IV)"])
        
        # Chord duration in beats
        duration_map = {"1 bar": 4.0, "2 bars": 8.0, "Half bar": 2.0}
        chord_beats = duration_map.get(chord_duration_name, 4.0)
        
        # Get start position
        start_beat = 0.0
        if hasattr(context, 'playhead_position'):
            start_beat = context.playhead_position
        elif isinstance(context, dict):
            start_beat = context.get('playheadPosition', 0.0)
        
        # Generate notes
        notes = []
        current_beat = start_beat
        
        for repeat in range(repeats):
            last_notes = None
            
            for i, (degree, chord_type) in enumerate(progression):
                # Get chord root
                degree_offset = self.SCALE_DEGREES.get(degree, 0)
                chord_root = root_midi + degree_offset
                
                # Choose inversion for smooth voice leading
                inversion = 0
                if use_inversions and last_notes:
                    # Find inversion closest to last chord
                    best_inv = 0
                    best_dist = float('inf')
                    for inv in range(3):
                        test_notes = self.get_chord_notes(chord_root, chord_type, inv)
                        dist = abs(sum(test_notes) / len(test_notes) - sum(last_notes) / len(last_notes))
                        if dist < best_dist:
                            best_dist = dist
                            best_inv = inv
                    inversion = best_inv
                
                # Get chord notes
                if style == "Power (5ths only)":
                    chord_notes = self.get_chord_notes(chord_root, "power", 0)
                else:
                    chord_notes = self.get_chord_notes(chord_root, chord_type, inversion)
                
                last_notes = chord_notes
                
                if style == "Block":
                    # All notes at once
                    for note_num in chord_notes:
                        notes.append(MidiNote(
                            note_number=note_num,
                            start_beat=current_beat,
                            length_beats=chord_beats * 0.95,
                            velocity=random.randint(75, 90),
                            channel=1
                        ))
                
                elif style == "Broken":
                    # Arpeggiate the chord
                    note_len = chord_beats / len(chord_notes)
                    for j, note_num in enumerate(chord_notes):
                        notes.append(MidiNote(
                            note_number=note_num,
                            start_beat=current_beat + (j * note_len),
                            length_beats=note_len * 0.9,
                            velocity=random.randint(70, 85),
                            channel=1
                        ))
                
                else:  # Power chords
                    for note_num in chord_notes:
                        notes.append(MidiNote(
                            note_number=note_num,
                            start_beat=current_beat,
                            length_beats=chord_beats * 0.95,
                            velocity=random.randint(85, 100),
                            channel=1
                        ))
                
                current_beat += chord_beats
        
        return notes


# For testing
if __name__ == "__main__":
    plugin = ChordProgressionPlugin()
    
    context = {
        'key': 'C',
        'octave': 3,
        'progression': 'Pop (I-V-vi-IV)',
        'chord_duration': '1 bar',
        'style': 'Block',
        'inversions': 'Yes',
        'repeats': 2,
        'playheadPosition': 0.0
    }
    
    notes = plugin.generate(context)
    
    print(f"Generated {len(notes)} notes:")
    for note in notes:
        print(f"  Note {note.note_number} at beat {note.start_beat:.1f}, "
              f"length {note.length_beats:.2f}, vel {note.velocity}")

