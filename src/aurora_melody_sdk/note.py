"""
MIDI Note representation for Aurora Melody plugins.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class MidiNote:
    """
    Represents a single MIDI note.
    
    This is the primary data structure for representing musical notes
    in Aurora Melody plugins.
    
    Attributes:
        note_number: MIDI note number (0-127). 60 = Middle C (C4).
        start_beat: Start position in beats from the beginning.
        length_beats: Duration of the note in beats.
        velocity: Note velocity/loudness (0-127). 100 is a good default.
        channel: MIDI channel (1-16). Default is 1.
    
    Example::
    
        # Create a middle C, quarter note at beat 0
        note = MidiNote(
            note_number=60,
            start_beat=0.0,
            length_beats=1.0,
            velocity=100
        )
        
        # Create a C major chord
        c_major = [
            MidiNote(60, 0.0, 2.0, 90),  # C
            MidiNote(64, 0.0, 2.0, 85),  # E
            MidiNote(67, 0.0, 2.0, 80),  # G
        ]
    
    Note Mapping::
    
        C4 = 60 (Middle C)
        A4 = 69 (Concert A, 440Hz)
        C0 = 12
        C5 = 72
    """
    
    note_number: int = 60
    start_beat: float = 0.0
    length_beats: float = 1.0
    velocity: int = 100
    channel: int = 1
    
    def __post_init__(self):
        """Validate note values after initialization."""
        self.note_number = max(0, min(127, int(self.note_number)))
        self.start_beat = max(0.0, float(self.start_beat))
        self.length_beats = max(0.01, float(self.length_beats))
        self.velocity = max(1, min(127, int(self.velocity)))
        self.channel = max(1, min(16, int(self.channel)))
    
    @property
    def end_beat(self) -> float:
        """Get the end position of the note in beats."""
        return self.start_beat + self.length_beats
    
    @property
    def octave(self) -> int:
        """Get the octave number (C4 = octave 4)."""
        return (self.note_number // 12) - 1
    
    @property
    def pitch_class(self) -> int:
        """Get the pitch class (0-11, where 0 = C)."""
        return self.note_number % 12
    
    @property
    def note_name(self) -> str:
        """Get the note name with octave (e.g., 'C4', 'F#5')."""
        names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return f"{names[self.pitch_class]}{self.octave}"
    
    def transpose(self, semitones: int) -> 'MidiNote':
        """
        Create a transposed copy of this note.
        
        Args:
            semitones: Number of semitones to transpose (positive = up, negative = down)
        
        Returns:
            New MidiNote transposed by the specified amount
        """
        return MidiNote(
            note_number=max(0, min(127, self.note_number + semitones)),
            start_beat=self.start_beat,
            length_beats=self.length_beats,
            velocity=self.velocity,
            channel=self.channel
        )
    
    def shift(self, beats: float) -> 'MidiNote':
        """
        Create a time-shifted copy of this note.
        
        Args:
            beats: Number of beats to shift (positive = later, negative = earlier)
        
        Returns:
            New MidiNote shifted by the specified amount
        """
        return MidiNote(
            note_number=self.note_number,
            start_beat=max(0.0, self.start_beat + beats),
            length_beats=self.length_beats,
            velocity=self.velocity,
            channel=self.channel
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for JSON serialization.
        
        Returns:
            Dictionary with camelCase keys for Aurora Melody compatibility
        """
        return {
            "noteNumber": self.note_number,
            "startBeat": self.start_beat,
            "lengthBeats": self.length_beats,
            "velocity": self.velocity,
            "channel": self.channel
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MidiNote':
        """
        Create MidiNote from dictionary.
        
        Args:
            data: Dictionary with note data (supports both camelCase and snake_case)
        
        Returns:
            New MidiNote instance
        """
        return cls(
            note_number=data.get('noteNumber', data.get('note_number', 60)),
            start_beat=data.get('startBeat', data.get('start_beat', 0.0)),
            length_beats=data.get('lengthBeats', data.get('length_beats', 1.0)),
            velocity=data.get('velocity', 100),
            channel=data.get('channel', 1)
        )
    
    @classmethod
    def from_name(cls, name: str, start_beat: float = 0.0, 
                  length_beats: float = 1.0, velocity: int = 100) -> 'MidiNote':
        """
        Create MidiNote from note name.
        
        Args:
            name: Note name like 'C4', 'F#5', 'Bb3'
            start_beat: Start position in beats
            length_beats: Duration in beats
            velocity: Note velocity
        
        Returns:
            New MidiNote instance
        
        Example::
        
            note = MidiNote.from_name('C4', 0.0, 1.0, 100)
        """
        from aurora_melody_sdk.theory.notes import NoteName
        return cls(
            note_number=NoteName.to_midi(name),
            start_beat=start_beat,
            length_beats=length_beats,
            velocity=velocity
        )
    
    def __repr__(self) -> str:
        return f"MidiNote({self.note_name}, beat={self.start_beat:.2f}, len={self.length_beats:.2f}, vel={self.velocity})"

