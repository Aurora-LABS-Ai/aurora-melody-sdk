"""
Melody generation utilities for Aurora Melody plugins.
"""

import random
from typing import List, Optional

from aurora_melody_sdk.note import MidiNote
from aurora_melody_sdk.theory.scales import Scale


def random_walk(
    start_note: int = 60,
    num_notes: int = 16,
    step_size: int = 2,
    scale: Optional[List[int]] = None,
    root: int = 60,
    start_beat: float = 0.0,
    note_length: float = 0.5,
    velocity_range: tuple = (70, 100),
) -> List[MidiNote]:
    """
    Generate a random walk melody.
    
    Creates a sequence of notes that moves randomly up or down,
    optionally constrained to a scale.
    
    Args:
        start_note: Starting MIDI note number
        num_notes: Number of notes to generate
        step_size: Maximum step size in scale degrees (or semitones if no scale)
        scale: Optional scale intervals to constrain notes
        root: Root note for the scale
        start_beat: Starting beat position
        note_length: Length of each note in beats
        velocity_range: Tuple of (min, max) velocity
    
    Returns:
        List of MidiNote objects
    
    Example::
    
        from aurora_melody_sdk import random_walk, Scale
        
        # Random walk in C major
        notes = random_walk(
            start_note=60,
            num_notes=16,
            step_size=2,
            scale=Scale.MAJOR,
            root=60
        )
        
        # Free random walk (chromatic)
        notes = random_walk(start_note=60, num_notes=8)
    """
    notes = []
    
    # Build scale notes if provided
    if scale:
        scale_notes = Scale.get_notes(root % 12, scale, octaves=10)
        # Filter to reasonable range
        scale_notes = [n for n in scale_notes if 24 <= n <= 108]
        if not scale_notes:
            scale_notes = [start_note]
        
        # Find nearest scale note to start
        current_idx = min(range(len(scale_notes)), 
                         key=lambda i: abs(scale_notes[i] - start_note))
    else:
        current_note = start_note
    
    for i in range(num_notes):
        if scale:
            # Move by scale degrees
            step = random.randint(-step_size, step_size)
            current_idx = max(0, min(len(scale_notes) - 1, current_idx + step))
            note_number = scale_notes[current_idx]
        else:
            # Move by semitones
            step = random.randint(-step_size, step_size)
            current_note = max(24, min(108, current_note + step))
            note_number = current_note
        
        velocity = random.randint(velocity_range[0], velocity_range[1])
        
        notes.append(MidiNote(
            note_number=note_number,
            start_beat=start_beat + (i * note_length),
            length_beats=note_length * 0.9,
            velocity=velocity
        ))
    
    return notes


def arpeggiate(
    chord_notes: List[int],
    pattern: str = "up",
    start_beat: float = 0.0,
    total_beats: float = 4.0,
    note_length: float = 0.25,
    velocity_range: tuple = (70, 100),
) -> List[MidiNote]:
    """
    Create an arpeggio pattern from chord notes.
    
    Args:
        chord_notes: List of MIDI note numbers in the chord
        pattern: Pattern type - "up", "down", "updown", "downup", "random"
        start_beat: Starting beat position
        total_beats: Total duration to fill
        note_length: Length of each note in beats
        velocity_range: Tuple of (min, max) velocity
    
    Returns:
        List of MidiNote objects forming the arpeggio
    
    Example::
    
        from aurora_melody_sdk import arpeggiate, Chord
        
        # Arpeggiate a C major chord going up
        c_major = Chord.get_notes(60, Chord.MAJOR)
        notes = arpeggiate(c_major, pattern="up", total_beats=4.0)
        
        # Up-down pattern
        notes = arpeggiate(c_major, pattern="updown")
    """
    if not chord_notes:
        return []
    
    # Create pattern sequence
    if pattern == "down":
        sequence = list(reversed(chord_notes))
    elif pattern == "updown":
        sequence = chord_notes + list(reversed(chord_notes[1:-1] if len(chord_notes) > 2 else []))
    elif pattern == "downup":
        sequence = list(reversed(chord_notes)) + chord_notes[1:-1] if len(chord_notes) > 2 else list(reversed(chord_notes))
    elif pattern == "random":
        sequence = chord_notes.copy()
        random.shuffle(sequence)
    else:  # "up" or default
        sequence = chord_notes.copy()
    
    if not sequence:
        sequence = chord_notes
    
    # Generate notes
    notes = []
    current_beat = start_beat
    idx = 0
    
    while current_beat < start_beat + total_beats:
        note_number = sequence[idx % len(sequence)]
        velocity = random.randint(velocity_range[0], velocity_range[1])
        
        # Accent first beat of pattern
        if idx % len(sequence) == 0:
            velocity = min(127, velocity + 10)
        
        actual_length = min(note_length, start_beat + total_beats - current_beat)
        
        notes.append(MidiNote(
            note_number=note_number,
            start_beat=current_beat,
            length_beats=actual_length * 0.9,
            velocity=velocity
        ))
        
        current_beat += note_length
        idx += 1
    
    return notes


def sequence_chords(
    chord_progression: List[tuple],
    start_beat: float = 0.0,
    beats_per_chord: float = 4.0,
    style: str = "block",
    velocity_range: tuple = (70, 90),
) -> List[MidiNote]:
    """
    Generate a chord progression.
    
    Args:
        chord_progression: List of (root, chord_type) tuples
        start_beat: Starting beat position
        beats_per_chord: Duration of each chord in beats
        style: "block" for simultaneous, "broken" for arpeggiated
        velocity_range: Tuple of (min, max) velocity
    
    Returns:
        List of MidiNote objects
    
    Example::
    
        from aurora_melody_sdk import sequence_chords, Chord
        
        # I-IV-V-I progression in C
        progression = [
            (60, Chord.MAJOR),  # C
            (65, Chord.MAJOR),  # F
            (67, Chord.MAJOR),  # G
            (60, Chord.MAJOR),  # C
        ]
        notes = sequence_chords(progression, beats_per_chord=4.0)
    """
    from aurora_melody_sdk.theory.chords import Chord
    
    notes = []
    current_beat = start_beat
    
    for root, chord_type in chord_progression:
        chord_notes = Chord.get_notes(root, chord_type)
        
        if style == "broken":
            # Arpeggiate the chord
            arp_notes = arpeggiate(
                chord_notes,
                pattern="up",
                start_beat=current_beat,
                total_beats=beats_per_chord,
                note_length=beats_per_chord / len(chord_notes),
                velocity_range=velocity_range
            )
            notes.extend(arp_notes)
        else:
            # Block chord
            for note_num in chord_notes:
                velocity = random.randint(velocity_range[0], velocity_range[1])
                notes.append(MidiNote(
                    note_number=note_num,
                    start_beat=current_beat,
                    length_beats=beats_per_chord * 0.95,
                    velocity=velocity
                ))
        
        current_beat += beats_per_chord
    
    return notes

