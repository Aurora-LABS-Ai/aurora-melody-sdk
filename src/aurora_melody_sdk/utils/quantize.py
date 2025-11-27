"""
Quantization utilities for Aurora Melody plugins.
"""

from typing import List

from aurora_melody_sdk.note import MidiNote


def quantize_beat(beat: float, resolution: float = 0.25) -> float:
    """
    Quantize a beat position to the nearest grid line.
    
    Args:
        beat: Beat position to quantize
        resolution: Grid resolution in beats (default 0.25 = 16th notes)
    
    Returns:
        Quantized beat position
    
    Example::
    
        from aurora_melody_sdk import quantize_beat
        
        # Quantize to 16th notes
        q = quantize_beat(1.37, 0.25)  # Returns 1.25
        
        # Quantize to 8th notes
        q = quantize_beat(1.37, 0.5)   # Returns 1.5
    
    Common resolutions:
        - 0.0625 = 1/64 notes
        - 0.125 = 1/32 notes
        - 0.25 = 1/16 notes
        - 0.5 = 1/8 notes
        - 1.0 = 1/4 notes (quarter notes)
        - 2.0 = 1/2 notes
        - 4.0 = whole notes
    """
    if resolution <= 0:
        return beat
    return round(beat / resolution) * resolution


def quantize_notes(
    notes: List[MidiNote],
    resolution: float = 0.25,
    quantize_length: bool = False,
) -> List[MidiNote]:
    """
    Quantize a list of notes to a grid.
    
    Args:
        notes: List of MidiNote objects
        resolution: Grid resolution in beats
        quantize_length: If True, also quantize note lengths
    
    Returns:
        List of quantized MidiNote objects
    
    Example::
    
        from aurora_melody_sdk import quantize_notes
        
        # Quantize notes to 16th note grid
        quantized = quantize_notes(notes, 0.25)
        
        # Quantize both position and length
        quantized = quantize_notes(notes, 0.25, quantize_length=True)
    """
    result = []
    
    for note in notes:
        new_start = quantize_beat(note.start_beat, resolution)
        
        if quantize_length:
            new_length = max(resolution, quantize_beat(note.length_beats, resolution))
        else:
            new_length = note.length_beats
        
        result.append(MidiNote(
            note_number=note.note_number,
            start_beat=new_start,
            length_beats=new_length,
            velocity=note.velocity,
            channel=note.channel
        ))
    
    return result


def humanize(
    notes: List[MidiNote],
    timing_variance: float = 0.02,
    velocity_variance: int = 10,
    length_variance: float = 0.0,
) -> List[MidiNote]:
    """
    Add human-like variations to notes.
    
    Args:
        notes: List of MidiNote objects
        timing_variance: Maximum timing offset in beats
        velocity_variance: Maximum velocity offset
        length_variance: Maximum length offset in beats
    
    Returns:
        List of humanized MidiNote objects
    
    Example::
    
        from aurora_melody_sdk.utils import humanize
        
        # Add subtle timing and velocity variations
        humanized = humanize(notes, timing_variance=0.02, velocity_variance=8)
    """
    import random
    
    result = []
    
    for note in notes:
        # Random timing offset
        timing_offset = random.uniform(-timing_variance, timing_variance)
        new_start = max(0.0, note.start_beat + timing_offset)
        
        # Random velocity offset
        vel_offset = random.randint(-velocity_variance, velocity_variance)
        new_velocity = max(1, min(127, note.velocity + vel_offset))
        
        # Random length offset
        length_offset = random.uniform(-length_variance, length_variance)
        new_length = max(0.01, note.length_beats + length_offset)
        
        result.append(MidiNote(
            note_number=note.note_number,
            start_beat=new_start,
            length_beats=new_length,
            velocity=new_velocity,
            channel=note.channel
        ))
    
    return result


def remove_overlaps(notes: List[MidiNote], mode: str = "truncate") -> List[MidiNote]:
    """
    Remove overlapping notes.
    
    Args:
        notes: List of MidiNote objects
        mode: "truncate" to shorten earlier notes, "remove" to delete overlaps
    
    Returns:
        List of MidiNote objects without overlaps
    """
    if not notes:
        return []
    
    # Sort by start time, then by note number
    sorted_notes = sorted(notes, key=lambda n: (n.start_beat, n.note_number))
    
    result = []
    
    # Group by note number
    note_groups = {}
    for note in sorted_notes:
        if note.note_number not in note_groups:
            note_groups[note.note_number] = []
        note_groups[note.note_number].append(note)
    
    # Process each note number separately
    for note_num, group in note_groups.items():
        prev_note = None
        
        for note in group:
            if prev_note is None:
                result.append(note)
                prev_note = note
            elif note.start_beat >= prev_note.end_beat:
                # No overlap
                result.append(note)
                prev_note = note
            elif mode == "truncate":
                # Truncate previous note
                new_length = note.start_beat - prev_note.start_beat
                if new_length > 0.01:
                    # Find and update the previous note in result
                    for i, r in enumerate(result):
                        if r is prev_note:
                            result[i] = MidiNote(
                                note_number=prev_note.note_number,
                                start_beat=prev_note.start_beat,
                                length_beats=new_length,
                                velocity=prev_note.velocity,
                                channel=prev_note.channel
                            )
                            break
                result.append(note)
                prev_note = note
            # mode == "remove": skip overlapping note
    
    return sorted(result, key=lambda n: n.start_beat)

