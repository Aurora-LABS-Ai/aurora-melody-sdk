"""
Random Melody Generator Plugin for Aurora Melody
=================================================

This example plugin generates random melodies based on
musical scales and configurable parameters.
"""

import random
import sys
import os

# Add SDK to path (for standalone testing)
sdk_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src', 'sdk', 'python')
if sdk_path not in sys.path:
    sys.path.insert(0, sdk_path)

try:
    from aurora_sdk import AuroraPlugin, MidiNote, Scale, random_walk
except ImportError:
    # Fallback minimal implementation for when SDK is not available
    class MidiNote:
        def __init__(self, note_number=60, start_beat=0.0, length_beats=1.0, velocity=100, channel=1):
            self.note_number = note_number
            self.start_beat = start_beat
            self.length_beats = length_beats
            self.velocity = velocity
            self.channel = channel
    
    class AuroraPlugin:
        pass
    
    class Scale:
        MAJOR = [0, 2, 4, 5, 7, 9, 11]
        MINOR = [0, 2, 3, 5, 7, 8, 10]
        PENTATONIC_MAJOR = [0, 2, 4, 7, 9]
        PENTATONIC_MINOR = [0, 3, 5, 7, 10]
        BLUES = [0, 3, 5, 6, 7, 10]


class RandomMelodyGenerator(AuroraPlugin):
    """
    Generates random melodies based on musical scales.
    
    Parameters:
    - num_notes: Number of notes to generate (4-64)
    - root_note: Root note of the scale (C4 = 60)
    - scale_type: Musical scale to use
    - note_length: Base note length in beats
    - velocity_range: Min/max velocity
    """
    
    name = "Random Melody Generator"
    author = "Aurora Melody Labs"
    version = "1.0.0"
    description = "Generate random melodies using musical scales"
    
    # Plugin parameters (shown in UI)
    parameters = [
        {
            "id": "num_notes",
            "name": "Number of Notes",
            "type": "int",
            "min": 4,
            "max": 64,
            "default": 16
        },
        {
            "id": "root_note",
            "name": "Root Note",
            "type": "int",
            "min": 36,
            "max": 84,
            "default": 60
        },
        {
            "id": "scale_type",
            "name": "Scale",
            "type": "choice",
            "choices": ["Major", "Minor", "Pentatonic Major", "Pentatonic Minor", "Blues"],
            "default": "Major"
        },
        {
            "id": "note_length",
            "name": "Note Length",
            "type": "choice",
            "choices": ["1/16", "1/8", "1/4", "1/2"],
            "default": "1/8"
        },
        {
            "id": "velocity_min",
            "name": "Min Velocity",
            "type": "int",
            "min": 1,
            "max": 127,
            "default": 70
        },
        {
            "id": "velocity_max",
            "name": "Max Velocity",
            "type": "int",
            "min": 1,
            "max": 127,
            "default": 100
        }
    ]
    
    def __init__(self):
        self.scales = {
            "Major": Scale.MAJOR,
            "Minor": Scale.MINOR,
            "Pentatonic Major": Scale.PENTATONIC_MAJOR,
            "Pentatonic Minor": Scale.PENTATONIC_MINOR,
            "Blues": Scale.BLUES
        }
        
        self.note_lengths = {
            "1/16": 0.25,
            "1/8": 0.5,
            "1/4": 1.0,
            "1/2": 2.0
        }
    
    def generate(self, context):
        """Generate random melody notes."""
        
        # Get parameters (with defaults)
        params = context if isinstance(context, dict) else {}
        if hasattr(context, 'parameters'):
            params = context.parameters
        
        num_notes = int(params.get('num_notes', 16))
        root_note = int(params.get('root_note', 60))
        scale_name = params.get('scale_type', 'Major')
        note_length_name = params.get('note_length', '1/8')
        velocity_min = int(params.get('velocity_min', 70))
        velocity_max = int(params.get('velocity_max', 100))
        
        # Get scale and note length
        scale = self.scales.get(scale_name, Scale.MAJOR)
        note_length = self.note_lengths.get(note_length_name, 0.5)
        
        # Get starting position (playhead or 0)
        start_beat = 0.0
        if hasattr(context, 'playhead_position'):
            start_beat = context.playhead_position
        elif isinstance(context, dict):
            start_beat = context.get('playheadPosition', 0.0)
        
        # Build scale notes across multiple octaves
        scale_notes = []
        for octave in range(-1, 3):
            for interval in scale:
                note = root_note + interval + (octave * 12)
                if 36 <= note <= 96:  # Keep in reasonable range
                    scale_notes.append(note)
        
        if not scale_notes:
            scale_notes = [root_note]
        
        # Generate melody using random walk
        notes = []
        current_note_idx = len(scale_notes) // 2  # Start in middle of range
        
        for i in range(num_notes):
            # Random walk: move up, down, or stay
            step = random.choice([-2, -1, -1, 0, 0, 1, 1, 2])
            current_note_idx = max(0, min(len(scale_notes) - 1, current_note_idx + step))
            
            note_number = scale_notes[current_note_idx]
            velocity = random.randint(velocity_min, velocity_max)
            
            # Occasionally add slight timing variation
            beat_offset = start_beat + (i * note_length)
            
            # Occasionally vary note length
            actual_length = note_length
            if random.random() < 0.2:  # 20% chance of different length
                actual_length = note_length * random.choice([0.5, 1.5, 2.0])
            
            notes.append(MidiNote(
                note_number=note_number,
                start_beat=beat_offset,
                length_beats=actual_length,
                velocity=velocity,
                channel=1
            ))
        
        return notes


# For testing the plugin standalone
if __name__ == "__main__":
    plugin = RandomMelodyGenerator()
    
    # Create a mock context
    context = {
        'num_notes': 8,
        'root_note': 60,
        'scale_type': 'Pentatonic Minor',
        'note_length': '1/8',
        'velocity_min': 80,
        'velocity_max': 100,
        'playheadPosition': 0.0
    }
    
    notes = plugin.generate(context)
    
    print(f"Generated {len(notes)} notes:")
    for note in notes:
        print(f"  Note {note.note_number} at beat {note.start_beat:.2f}, "
              f"length {note.length_beats:.2f}, velocity {note.velocity}")

