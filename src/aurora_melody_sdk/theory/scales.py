"""
Musical scales for Aurora Melody plugins.
"""

from typing import List


class Scale:
    """
    Common musical scales as semitone intervals from root.
    
    Each scale is a list of semitone intervals from the root note.
    For example, MAJOR = [0, 2, 4, 5, 7, 9, 11] means:
    - Root (0)
    - Major 2nd (+2 semitones)
    - Major 3rd (+4 semitones)
    - Perfect 4th (+5 semitones)
    - etc.
    
    Example::
    
        from aurora_melody_sdk import Scale
        
        # Get C major scale notes
        c_major_notes = Scale.get_notes(60, Scale.MAJOR)
        # Result: [60, 62, 64, 65, 67, 69, 71]
        
        # Get notes across 2 octaves
        two_octaves = Scale.get_notes(48, Scale.PENTATONIC_MINOR, octaves=2)
    """
    
    # Major modes
    MAJOR = [0, 2, 4, 5, 7, 9, 11]
    IONIAN = MAJOR  # Same as major
    
    # Minor scales
    MINOR = [0, 2, 3, 5, 7, 8, 10]
    NATURAL_MINOR = MINOR
    AEOLIAN = MINOR
    HARMONIC_MINOR = [0, 2, 3, 5, 7, 8, 11]
    MELODIC_MINOR = [0, 2, 3, 5, 7, 9, 11]  # Ascending form
    
    # Pentatonic scales
    PENTATONIC_MAJOR = [0, 2, 4, 7, 9]
    PENTATONIC_MINOR = [0, 3, 5, 7, 10]
    
    # Blues scale
    BLUES = [0, 3, 5, 6, 7, 10]
    
    # Church modes
    DORIAN = [0, 2, 3, 5, 7, 9, 10]
    PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
    LYDIAN = [0, 2, 4, 6, 7, 9, 11]
    MIXOLYDIAN = [0, 2, 4, 5, 7, 9, 10]
    LOCRIAN = [0, 1, 3, 5, 6, 8, 10]
    
    # Other scales
    CHROMATIC = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    WHOLE_TONE = [0, 2, 4, 6, 8, 10]
    DIMINISHED = [0, 2, 3, 5, 6, 8, 9, 11]  # Half-whole
    AUGMENTED = [0, 3, 4, 7, 8, 11]
    
    # Japanese scales
    HIRAJOSHI = [0, 2, 3, 7, 8]
    IN_SEN = [0, 1, 5, 7, 10]
    
    # Other ethnic scales
    HUNGARIAN_MINOR = [0, 2, 3, 6, 7, 8, 11]
    SPANISH = [0, 1, 4, 5, 7, 8, 10]
    ARABIC = [0, 1, 4, 5, 7, 8, 11]
    
    @classmethod
    def get_notes(cls, root: int, scale: List[int], octaves: int = 1) -> List[int]:
        """
        Get all MIDI note numbers in a scale.
        
        Args:
            root: Root note MIDI number (e.g., 60 for C4)
            scale: Scale intervals (e.g., Scale.MAJOR)
            octaves: Number of octaves to generate (default 1)
        
        Returns:
            List of MIDI note numbers in the scale
        
        Example::
        
            # C major scale in one octave
            notes = Scale.get_notes(60, Scale.MAJOR)
            # [60, 62, 64, 65, 67, 69, 71]
            
            # A minor pentatonic in two octaves
            notes = Scale.get_notes(57, Scale.PENTATONIC_MINOR, octaves=2)
        """
        notes = []
        for octave in range(octaves):
            for interval in scale:
                note = root + interval + (octave * 12)
                if 0 <= note <= 127:
                    notes.append(note)
        return notes
    
    @classmethod
    def is_in_scale(cls, note: int, root: int, scale: List[int]) -> bool:
        """
        Check if a note is in a given scale.
        
        Args:
            note: MIDI note number to check
            root: Root note of the scale
            scale: Scale intervals
        
        Returns:
            True if the note is in the scale
        """
        interval = (note - root) % 12
        return interval in scale
    
    @classmethod
    def nearest_scale_note(cls, note: int, root: int, scale: List[int]) -> int:
        """
        Find the nearest note in the scale.
        
        Args:
            note: MIDI note to find nearest for
            root: Root note of the scale
            scale: Scale intervals
        
        Returns:
            Nearest MIDI note number in the scale
        """
        # Get scale notes in the same octave area
        base = (note // 12) * 12 + (root % 12)
        scale_notes = cls.get_notes(base - 12, scale, octaves=3)
        
        if not scale_notes:
            return note
        
        return min(scale_notes, key=lambda x: abs(x - note))
    
    @classmethod
    def get_scale_names(cls) -> List[str]:
        """Get list of all available scale names."""
        return [name for name in dir(cls) 
                if not name.startswith('_') 
                and isinstance(getattr(cls, name), list)]

