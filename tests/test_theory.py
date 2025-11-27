"""
Tests for music theory classes.
"""

import pytest
from aurora_melody_sdk import Scale, Chord, NoteName


class TestScale:
    """Tests for Scale class."""
    
    def test_major_scale(self):
        """Test major scale intervals."""
        notes = Scale.get_notes(60, Scale.MAJOR)
        assert notes == [60, 62, 64, 65, 67, 69, 71]
    
    def test_minor_scale(self):
        """Test minor scale intervals."""
        notes = Scale.get_notes(60, Scale.MINOR)
        assert notes == [60, 62, 63, 65, 67, 68, 70]
    
    def test_pentatonic_major(self):
        """Test pentatonic major scale."""
        notes = Scale.get_notes(60, Scale.PENTATONIC_MAJOR)
        assert notes == [60, 62, 64, 67, 69]
    
    def test_blues_scale(self):
        """Test blues scale."""
        notes = Scale.get_notes(60, Scale.BLUES)
        assert notes == [60, 63, 65, 66, 67, 70]
    
    def test_multiple_octaves(self):
        """Test scale with multiple octaves."""
        notes = Scale.get_notes(60, Scale.MAJOR, octaves=2)
        assert len(notes) == 14
        assert notes[7] == 72  # C5
    
    def test_different_root(self):
        """Test scale with different root."""
        # G major starting at G3 (55)
        notes = Scale.get_notes(55, Scale.MAJOR)
        assert notes[0] == 55
        assert notes[2] == 59  # B


class TestChord:
    """Tests for Chord class."""
    
    def test_major_chord(self):
        """Test major chord."""
        notes = Chord.get_notes(60, Chord.MAJOR)
        assert notes == [60, 64, 67]
    
    def test_minor_chord(self):
        """Test minor chord."""
        notes = Chord.get_notes(60, Chord.MINOR)
        assert notes == [60, 63, 67]
    
    def test_major_7_chord(self):
        """Test major 7th chord."""
        notes = Chord.get_notes(60, Chord.MAJOR_7)
        assert notes == [60, 64, 67, 71]
    
    def test_dominant_7_chord(self):
        """Test dominant 7th chord."""
        notes = Chord.get_notes(60, Chord.DOMINANT_7)
        assert notes == [60, 64, 67, 70]
    
    def test_first_inversion(self):
        """Test first inversion."""
        notes = Chord.get_inversion(60, Chord.MAJOR, 1)
        # First inversion: E G C
        assert notes[0] == 64  # E
        assert notes[1] == 67  # G
        assert notes[2] == 72  # C (octave up)
    
    def test_second_inversion(self):
        """Test second inversion."""
        notes = Chord.get_inversion(60, Chord.MAJOR, 2)
        # Second inversion: G C E
        assert notes[0] == 67  # G
        assert notes[1] == 72  # C
        assert notes[2] == 76  # E


class TestNoteName:
    """Tests for NoteName utility."""
    
    def test_to_midi(self):
        """Test converting note names to MIDI numbers."""
        assert NoteName.to_midi("C4") == 60
        assert NoteName.to_midi("A4") == 69
        assert NoteName.to_midi("C0") == 12
        assert NoteName.to_midi("F#5") == 78
        assert NoteName.to_midi("Bb3") == 58
    
    def test_from_midi(self):
        """Test converting MIDI numbers to note names."""
        assert NoteName.from_midi(60) == "C4"
        assert NoteName.from_midi(69) == "A4"
        assert NoteName.from_midi(78) == "F#5"
    
    def test_transpose(self):
        """Test transposing note names."""
        assert NoteName.transpose("C4", 5) == "F4"
        assert NoteName.transpose("C4", 12) == "C5"

