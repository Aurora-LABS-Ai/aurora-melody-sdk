"""
Arpeggiator Plugin for Aurora Melody
=====================================

Generates arpeggios from chord progressions in various styles.
"""

import random
import sys
import os

# Add SDK to path
sdk_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'sdk', 'python')
if sdk_path not in sys.path:
    sys.path.insert(0, sdk_path)

try:
    from aurora_sdk import AuroraPlugin, MidiNote, Chord
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
        MAJOR_7 = [0, 4, 7, 11]
        MINOR_7 = [0, 3, 7, 10]
        DOMINANT_7 = [0, 4, 7, 10]
        SUS4 = [0, 5, 7]


class ArpeggiatorPlugin(AuroraPlugin):
    """
    Generate arpeggios from chords with various patterns.
    """
    
    name = "Arpeggiator"
    author = "Aurora Melody Labs"
    version = "1.0.0"
    description = "Generate arpeggios from chord patterns"
    
    parameters = [
        {
            "id": "root_note",
            "name": "Root Note",
            "type": "int",
            "min": 36,
            "max": 84,
            "default": 48
        },
        {
            "id": "chord_type",
            "name": "Chord Type",
            "type": "choice",
            "choices": ["Major", "Minor", "Major 7", "Minor 7", "Dominant 7", "Sus4"],
            "default": "Major"
        },
        {
            "id": "pattern",
            "name": "Pattern",
            "type": "choice",
            "choices": ["Up", "Down", "Up-Down", "Down-Up", "Random", "Outside-In"],
            "default": "Up"
        },
        {
            "id": "octaves",
            "name": "Octaves",
            "type": "choice",
            "choices": ["1", "2", "3"],
            "default": "2"
        },
        {
            "id": "note_length",
            "name": "Note Length",
            "type": "choice",
            "choices": ["1/32", "1/16", "1/8", "1/4"],
            "default": "1/16"
        },
        {
            "id": "bars",
            "name": "Bars",
            "type": "int",
            "min": 1,
            "max": 8,
            "default": 2
        },
        {
            "id": "velocity_variation",
            "name": "Velocity Variation",
            "type": "int",
            "min": 0,
            "max": 40,
            "default": 15
        }
    ]
    
    def __init__(self):
        self.chord_types = {
            "Major": Chord.MAJOR,
            "Minor": Chord.MINOR,
            "Major 7": Chord.MAJOR_7,
            "Minor 7": Chord.MINOR_7,
            "Dominant 7": Chord.DOMINANT_7,
            "Sus4": Chord.SUS4
        }
        
        self.note_lengths = {
            "1/32": 0.125,
            "1/16": 0.25,
            "1/8": 0.5,
            "1/4": 1.0
        }
    
    def get_arp_pattern(self, chord_notes: list, pattern: str) -> list:
        """Generate note sequence based on pattern."""
        
        if pattern == "Down":
            return list(reversed(chord_notes))
        elif pattern == "Up-Down":
            return chord_notes + list(reversed(chord_notes[1:-1]))
        elif pattern == "Down-Up":
            down = list(reversed(chord_notes))
            return down + chord_notes[1:-1]
        elif pattern == "Random":
            notes = chord_notes.copy()
            random.shuffle(notes)
            return notes
        elif pattern == "Outside-In":
            # Alternates between lowest and highest, moving inward
            result = []
            low = 0
            high = len(chord_notes) - 1
            while low <= high:
                result.append(chord_notes[low])
                if low != high:
                    result.append(chord_notes[high])
                low += 1
                high -= 1
            return result
        else:  # "Up"
            return chord_notes
    
    def generate(self, context):
        """Generate arpeggio notes."""
        
        # Get parameters
        params = context if isinstance(context, dict) else {}
        if hasattr(context, 'parameters'):
            params = context.parameters
        
        root_note = int(params.get('root_note', 48))
        chord_name = params.get('chord_type', 'Major')
        pattern = params.get('pattern', 'Up')
        octaves = int(params.get('octaves', '2'))
        note_length_name = params.get('note_length', '1/16')
        bars = int(params.get('bars', 2))
        velocity_var = int(params.get('velocity_variation', 15))
        
        chord_intervals = self.chord_types.get(chord_name, Chord.MAJOR)
        note_length = self.note_lengths.get(note_length_name, 0.25)
        
        # Get start position
        start_beat = 0.0
        if hasattr(context, 'playhead_position'):
            start_beat = context.playhead_position
        elif isinstance(context, dict):
            start_beat = context.get('playheadPosition', 0.0)
        
        # Build chord notes across octaves
        chord_notes = []
        for octave in range(octaves):
            for interval in chord_intervals:
                note = root_note + interval + (octave * 12)
                if 24 <= note <= 108:
                    chord_notes.append(note)
        
        # Get pattern sequence
        arp_sequence = self.get_arp_pattern(chord_notes, pattern)
        
        if not arp_sequence:
            return []
        
        # Generate notes
        notes = []
        total_beats = bars * 4.0  # 4 beats per bar
        current_beat = start_beat
        idx = 0
        base_velocity = 90
        
        while current_beat < start_beat + total_beats:
            note_num = arp_sequence[idx % len(arp_sequence)]
            
            # Add velocity variation
            vel_offset = random.randint(-velocity_var, velocity_var)
            velocity = max(40, min(127, base_velocity + vel_offset))
            
            # Accent first beat of pattern
            if idx % len(arp_sequence) == 0:
                velocity = min(127, velocity + 15)
            
            notes.append(MidiNote(
                note_number=note_num,
                start_beat=current_beat,
                length_beats=note_length * 0.9,  # Slight gap
                velocity=velocity,
                channel=1
            ))
            
            current_beat += note_length
            idx += 1
        
        return notes


# For testing
if __name__ == "__main__":
    plugin = ArpeggiatorPlugin()
    
    context = {
        'root_note': 48,
        'chord_type': 'Minor 7',
        'pattern': 'Up-Down',
        'octaves': '2',
        'note_length': '1/16',
        'bars': 2,
        'velocity_variation': 10,
        'playheadPosition': 0.0
    }
    
    notes = plugin.generate(context)
    
    print(f"Generated {len(notes)} notes:")
    for i, note in enumerate(notes[:16]):  # Show first 16
        print(f"  {i+1}. Note {note.note_number} at {note.start_beat:.2f}, vel {note.velocity}")
    if len(notes) > 16:
        print(f"  ... and {len(notes) - 16} more")

