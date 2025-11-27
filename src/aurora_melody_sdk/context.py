"""
Plugin execution context for Aurora Melody plugins.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from aurora_melody_sdk.note import MidiNote


@dataclass
class PluginContext:
    """
    Context passed to plugins containing the current piano roll state.
    
    When Aurora Melody executes your plugin, it passes a PluginContext
    containing information about the current state of the piano roll,
    including existing notes, selection, tempo, and user parameters.
    
    Attributes:
        notes: List of existing notes in the piano roll
        selected_note_ids: IDs of currently selected notes
        tempo_bpm: Current tempo in beats per minute
        time_signature: Tuple of (numerator, denominator)
        view_range: Tuple of (start_beat, end_beat) for visible range
        note_range: Tuple of (low_note, high_note) MIDI note numbers
        playhead_position: Current playhead position in beats
        parameters: User-defined plugin parameter values
    
    Example::
    
        def generate(self, context: PluginContext):
            # Get the tempo
            bpm = context.tempo_bpm
            
            # Start generating from playhead
            start = context.playhead_position
            
            # Access user parameters
            num_notes = context.parameters.get('num_notes', 8)
            
            # Get existing notes
            for note in context.notes:
                print(f"Existing: {note.note_name}")
    """
    
    notes: List[MidiNote] = field(default_factory=list)
    selected_note_ids: List[int] = field(default_factory=list)
    tempo_bpm: float = 120.0
    time_signature: tuple = (4, 4)
    view_range: tuple = (0.0, 16.0)
    note_range: tuple = (0, 127)
    playhead_position: float = 0.0
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def beats_per_bar(self) -> float:
        """Get number of beats per bar based on time signature."""
        return float(self.time_signature[0])
    
    @property
    def view_start(self) -> float:
        """Get the start of the visible range in beats."""
        return self.view_range[0]
    
    @property
    def view_end(self) -> float:
        """Get the end of the visible range in beats."""
        return self.view_range[1]
    
    @property
    def view_length(self) -> float:
        """Get the length of the visible range in beats."""
        return self.view_range[1] - self.view_range[0]
    
    def get_selected_notes(self) -> List[MidiNote]:
        """
        Get the notes that are currently selected.
        
        Returns:
            List of selected MidiNote objects
        """
        # Note: This requires notes to have an 'id' attribute
        return [n for n in self.notes 
                if hasattr(n, 'id') and n.id in self.selected_note_ids]
    
    def get_notes_in_range(self, start_beat: float, end_beat: float) -> List[MidiNote]:
        """
        Get notes that overlap with the given time range.
        
        Args:
            start_beat: Start of range in beats
            end_beat: End of range in beats
        
        Returns:
            List of notes that overlap the range
        """
        return [n for n in self.notes 
                if n.start_beat < end_beat and n.end_beat > start_beat]
    
    def get_notes_at_beat(self, beat: float) -> List[MidiNote]:
        """
        Get notes that are sounding at a specific beat.
        
        Args:
            beat: Position in beats
        
        Returns:
            List of notes sounding at that position
        """
        return [n for n in self.notes 
                if n.start_beat <= beat < n.end_beat]
    
    def get_param(self, key: str, default: Any = None) -> Any:
        """
        Get a parameter value with a default.
        
        Args:
            key: Parameter name
            default: Default value if not set
        
        Returns:
            Parameter value or default
        """
        return self.parameters.get(key, default)
    
    def get_int_param(self, key: str, default: int = 0) -> int:
        """Get a parameter as integer."""
        return int(self.parameters.get(key, default))
    
    def get_float_param(self, key: str, default: float = 0.0) -> float:
        """Get a parameter as float."""
        return float(self.parameters.get(key, default))
    
    def get_str_param(self, key: str, default: str = "") -> str:
        """Get a parameter as string."""
        return str(self.parameters.get(key, default))
    
    def get_bool_param(self, key: str, default: bool = False) -> bool:
        """Get a parameter as boolean."""
        val = self.parameters.get(key, default)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ('true', '1', 'yes', 'on')
        return bool(val)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginContext':
        """
        Create PluginContext from dictionary (as received from Aurora Melody).
        
        Args:
            data: Dictionary with context data
        
        Returns:
            New PluginContext instance
        """
        notes = [MidiNote.from_dict(n) if isinstance(n, dict) else n 
                 for n in data.get('notes', [])]
        
        return cls(
            notes=notes,
            selected_note_ids=data.get('selectedNoteIds', []),
            tempo_bpm=data.get('tempoBPM', 120.0),
            time_signature=(
                data.get('timeSignatureNum', 4),
                data.get('timeSignatureDenom', 4)
            ),
            view_range=(
                data.get('viewStartBeat', 0.0),
                data.get('viewEndBeat', 16.0)
            ),
            note_range=(
                data.get('viewLowNote', 0),
                data.get('viewHighNote', 127)
            ),
            playhead_position=data.get('playheadPosition', 0.0),
            parameters=data.get('parameters', {})
        )

