"""
Tests for MidiNote class.
"""

import pytest
from aurora_melody_sdk import MidiNote


class TestMidiNote:
    """Tests for MidiNote."""
    
    def test_create_note(self):
        """Test basic note creation."""
        note = MidiNote(60, 0.0, 1.0, 100)
        assert note.note_number == 60
        assert note.start_beat == 0.0
        assert note.length_beats == 1.0
        assert note.velocity == 100
        assert note.channel == 1
    
    def test_note_with_channel(self):
        """Test note with custom channel."""
        note = MidiNote(64, 1.0, 0.5, 80, channel=10)
        assert note.channel == 10
    
    def test_note_name(self):
        """Test note_name property."""
        note = MidiNote(60, 0.0, 1.0, 100)
        assert note.note_name == "C4"
        
        note = MidiNote(69, 0.0, 1.0, 100)
        assert note.note_name == "A4"
    
    def test_end_beat(self):
        """Test end_beat property."""
        note = MidiNote(60, 2.0, 1.5, 100)
        assert note.end_beat == 3.5
    
    def test_transpose(self):
        """Test transpose method."""
        note = MidiNote(60, 0.0, 1.0, 100)
        transposed = note.transpose(5)
        
        assert transposed.note_number == 65
        assert transposed.start_beat == note.start_beat
        assert transposed.length_beats == note.length_beats
        assert transposed.velocity == note.velocity
    
    def test_shift(self):
        """Test shift method."""
        note = MidiNote(60, 0.0, 1.0, 100)
        shifted = note.shift(4.0)
        
        assert shifted.start_beat == 4.0
        assert shifted.note_number == note.note_number
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        note = MidiNote(60, 0.0, 1.0, 100, channel=1)
        d = note.to_dict()
        
        assert d["noteNumber"] == 60
        assert d["startBeat"] == 0.0
        assert d["lengthBeats"] == 1.0
        assert d["velocity"] == 100
        assert d["channel"] == 1
    
    def test_from_dict(self):
        """Test creating note from dictionary."""
        d = {
            "noteNumber": 64,
            "startBeat": 2.0,
            "lengthBeats": 0.5,
            "velocity": 90,
            "channel": 2
        }
        note = MidiNote.from_dict(d)
        
        assert note.note_number == 64
        assert note.start_beat == 2.0
        assert note.length_beats == 0.5
        assert note.velocity == 90
        assert note.channel == 2

