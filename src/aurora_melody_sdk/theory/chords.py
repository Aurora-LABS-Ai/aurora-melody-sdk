"""
Musical chords for Aurora Melody plugins.
"""

from typing import List


class Chord:
    """
    Common chord types as semitone intervals from root.
    
    Each chord is a list of semitone intervals from the root note.
    For example, MAJOR = [0, 4, 7] means root, major third, perfect fifth.
    
    Example::
    
        from aurora_melody_sdk import Chord
        
        # Get C major chord notes
        c_major = Chord.get_notes(60, Chord.MAJOR)
        # Result: [60, 64, 67]
        
        # Get Am7 chord
        a_minor_7 = Chord.get_notes(57, Chord.MINOR_7)
        # Result: [57, 60, 64, 67]
    """
    
    # Triads
    MAJOR = [0, 4, 7]
    MINOR = [0, 3, 7]
    DIMINISHED = [0, 3, 6]
    AUGMENTED = [0, 4, 8]
    
    # Suspended
    SUS2 = [0, 2, 7]
    SUS4 = [0, 5, 7]
    
    # Seventh chords
    MAJOR_7 = [0, 4, 7, 11]
    MINOR_7 = [0, 3, 7, 10]
    DOMINANT_7 = [0, 4, 7, 10]
    DIMINISHED_7 = [0, 3, 6, 9]
    HALF_DIMINISHED_7 = [0, 3, 6, 10]  # m7b5
    MINOR_MAJOR_7 = [0, 3, 7, 11]
    AUGMENTED_7 = [0, 4, 8, 10]
    AUGMENTED_MAJOR_7 = [0, 4, 8, 11]
    
    # Extended chords
    MAJOR_9 = [0, 4, 7, 11, 14]
    MINOR_9 = [0, 3, 7, 10, 14]
    DOMINANT_9 = [0, 4, 7, 10, 14]
    MAJOR_11 = [0, 4, 7, 11, 14, 17]
    MINOR_11 = [0, 3, 7, 10, 14, 17]
    MAJOR_13 = [0, 4, 7, 11, 14, 17, 21]
    
    # Added tone chords
    ADD9 = [0, 4, 7, 14]
    ADD11 = [0, 4, 7, 17]
    
    # Power chord
    POWER = [0, 7]
    POWER_OCTAVE = [0, 7, 12]
    
    # Other
    SIXTH = [0, 4, 7, 9]
    MINOR_6 = [0, 3, 7, 9]
    
    @classmethod
    def get_notes(cls, root: int, chord_type: List[int]) -> List[int]:
        """
        Get all MIDI note numbers in a chord.
        
        Args:
            root: Root note MIDI number (e.g., 60 for C)
            chord_type: Chord intervals (e.g., Chord.MAJOR)
        
        Returns:
            List of MIDI note numbers in the chord
        
        Example::
        
            # C major chord
            notes = Chord.get_notes(60, Chord.MAJOR)
            # [60, 64, 67]
        """
        return [root + interval for interval in chord_type 
                if 0 <= root + interval <= 127]
    
    @classmethod
    def get_inversion(cls, root: int, chord_type: List[int], 
                      inversion: int = 0) -> List[int]:
        """
        Get chord notes in a specific inversion.
        
        Args:
            root: Root note MIDI number
            chord_type: Chord intervals
            inversion: Inversion number (0 = root position, 1 = first, etc.)
        
        Returns:
            List of MIDI note numbers in the inverted chord
        
        Example::
        
            # C major first inversion (E in bass)
            notes = Chord.get_inversion(60, Chord.MAJOR, 1)
            # [64, 67, 72]
        """
        notes = cls.get_notes(root, chord_type)
        
        for _ in range(inversion % len(notes)):
            notes[0] += 12
            notes = notes[1:] + [notes[0]]
        
        return notes
    
    @classmethod
    def voice_lead(cls, from_chord: List[int], to_root: int, 
                   to_type: List[int]) -> List[int]:
        """
        Voice lead from one chord to another, minimizing movement.
        
        Args:
            from_chord: Previous chord notes
            to_root: Root of target chord
            to_type: Type of target chord
        
        Returns:
            Target chord notes voiced for minimal movement
        """
        if not from_chord:
            return cls.get_notes(to_root, to_type)
        
        # Try all inversions and pick the one with smallest total movement
        best_notes = None
        best_movement = float('inf')
        
        for inv in range(len(to_type)):
            candidate = cls.get_inversion(to_root, to_type, inv)
            
            # Calculate total voice movement
            movement = 0
            for i, note in enumerate(candidate):
                if i < len(from_chord):
                    movement += abs(note - from_chord[i])
                else:
                    movement += 12  # Penalty for extra voices
            
            if movement < best_movement:
                best_movement = movement
                best_notes = candidate
        
        return best_notes or cls.get_notes(to_root, to_type)
    
    @classmethod
    def get_chord_names(cls) -> List[str]:
        """Get list of all available chord names."""
        return [name for name in dir(cls) 
                if not name.startswith('_') 
                and isinstance(getattr(cls, name), list)]

