"""
Note name utilities for Aurora Melody plugins.
"""

from typing import Optional


class NoteName:
    """
    Utilities for converting between note names and MIDI numbers.
    
    Example::
    
        from aurora_melody_sdk import NoteName
        
        # Convert note name to MIDI
        midi = NoteName.to_midi("C4")  # 60
        midi = NoteName.to_midi("F#5") # 78
        midi = NoteName.to_midi("Bb3") # 58
        
        # Convert MIDI to note name
        name = NoteName.from_midi(60)  # "C4"
        name = NoteName.from_midi(69)  # "A4"
    """
    
    # Note name to pitch class mapping
    NOTE_TO_PC = {
        'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
    }
    
    # Pitch class to note name (using sharps)
    PC_TO_NOTE_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Pitch class to note name (using flats)
    PC_TO_NOTE_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    
    @classmethod
    def to_midi(cls, note_name: str, default_octave: int = 4) -> int:
        """
        Convert a note name to MIDI note number.
        
        Args:
            note_name: Note name like "C4", "F#5", "Bb3", "D"
            default_octave: Octave to use if not specified in name
        
        Returns:
            MIDI note number (0-127)
        
        Example::
        
            NoteName.to_midi("C4")   # 60
            NoteName.to_midi("A4")   # 69 (concert A)
            NoteName.to_midi("F#5")  # 78
            NoteName.to_midi("Bb3")  # 58
            NoteName.to_midi("C")    # 60 (uses default octave 4)
        """
        if not note_name:
            return 60
        
        note_name = note_name.strip()
        
        # Parse note letter
        note = note_name[0].upper()
        if note not in cls.NOTE_TO_PC:
            return 60
        
        pitch_class = cls.NOTE_TO_PC[note]
        remaining = note_name[1:]
        
        # Parse accidentals
        modifier = 0
        while remaining and remaining[0] in '#bsf':
            char = remaining[0]
            if char in ['#', 's']:  # Sharp
                modifier += 1
            elif char in ['b', 'f']:  # Flat
                modifier -= 1
            remaining = remaining[1:]
        
        pitch_class = (pitch_class + modifier) % 12
        
        # Parse octave
        if remaining:
            try:
                octave = int(remaining)
            except ValueError:
                octave = default_octave
        else:
            octave = default_octave
        
        # Calculate MIDI number
        midi = (octave + 1) * 12 + pitch_class
        return max(0, min(127, midi))
    
    @classmethod
    def from_midi(cls, midi_number: int, use_flats: bool = False) -> str:
        """
        Convert a MIDI note number to note name.
        
        Args:
            midi_number: MIDI note number (0-127)
            use_flats: If True, use flat notation (Bb instead of A#)
        
        Returns:
            Note name with octave (e.g., "C4", "F#5")
        
        Example::
        
            NoteName.from_midi(60)              # "C4"
            NoteName.from_midi(69)              # "A4"
            NoteName.from_midi(70, use_flats=True)  # "Bb4"
            NoteName.from_midi(70, use_flats=False) # "A#4"
        """
        midi_number = max(0, min(127, int(midi_number)))
        
        octave = (midi_number // 12) - 1
        pitch_class = midi_number % 12
        
        if use_flats:
            note_name = cls.PC_TO_NOTE_FLAT[pitch_class]
        else:
            note_name = cls.PC_TO_NOTE_SHARP[pitch_class]
        
        return f"{note_name}{octave}"
    
    @classmethod
    def get_pitch_class(cls, midi_number: int) -> int:
        """
        Get pitch class (0-11) from MIDI number.
        
        Args:
            midi_number: MIDI note number
        
        Returns:
            Pitch class (0 = C, 1 = C#, etc.)
        """
        return midi_number % 12
    
    @classmethod
    def get_octave(cls, midi_number: int) -> int:
        """
        Get octave from MIDI number.
        
        Args:
            midi_number: MIDI note number
        
        Returns:
            Octave number (C4 = octave 4)
        """
        return (midi_number // 12) - 1
    
    @classmethod
    def transpose(cls, note_name: str, semitones: int) -> str:
        """
        Transpose a note by semitones.
        
        Args:
            note_name: Note name to transpose
            semitones: Number of semitones (positive = up)
        
        Returns:
            Transposed note name
        """
        midi = cls.to_midi(note_name)
        return cls.from_midi(midi + semitones)
    
    @classmethod
    def interval(cls, note1: str, note2: str) -> int:
        """
        Get interval in semitones between two notes.
        
        Args:
            note1: First note name
            note2: Second note name
        
        Returns:
            Interval in semitones (positive if note2 is higher)
        """
        return cls.to_midi(note2) - cls.to_midi(note1)

