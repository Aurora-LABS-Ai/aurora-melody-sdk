"""
Tests for utility functions.
"""

import pytest
from aurora_melody_sdk import (
    MidiNote, Scale, Chord,
    random_walk, arpeggiate, quantize_beat, humanize
)
from aurora_melody_sdk.utils import quantize_notes, remove_overlaps


class TestQuantize:
    """Tests for quantization functions."""
    
    def test_quantize_beat_16th(self):
        """Test quantizing to 16th notes."""
        assert quantize_beat(1.37, 0.25) == 1.25
        assert quantize_beat(1.13, 0.25) == 1.25
        assert quantize_beat(1.0, 0.25) == 1.0
    
    def test_quantize_beat_8th(self):
        """Test quantizing to 8th notes."""
        assert quantize_beat(1.37, 0.5) == 1.5
        assert quantize_beat(1.2, 0.5) == 1.0
    
    def test_quantize_beat_quarter(self):
        """Test quantizing to quarter notes."""
        assert quantize_beat(1.6, 1.0) == 2.0
        assert quantize_beat(0.4, 1.0) == 0.0
    
    def test_quantize_notes(self):
        """Test quantizing a list of notes."""
        notes = [
            MidiNote(60, 0.13, 0.5, 100),
            MidiNote(62, 0.87, 0.5, 100),
        ]
        quantized = quantize_notes(notes, 0.25)
        
        assert quantized[0].start_beat == 0.25
        assert quantized[1].start_beat == 0.75


class TestRandomWalk:
    """Tests for random_walk function."""
    
    def test_basic_random_walk(self):
        """Test basic random walk generation."""
        notes = random_walk(start_note=60, num_notes=8)
        
        assert len(notes) == 8
        assert all(isinstance(n, MidiNote) for n in notes)
    
    def test_random_walk_with_scale(self):
        """Test random walk with scale."""
        notes = random_walk(
            start_note=60,
            num_notes=16,
            scale=Scale.PENTATONIC_MAJOR,
            root=60
        )
        
        # Function generates across 10 octaves for range, so use wide range
        scale_notes = Scale.get_notes(0, Scale.PENTATONIC_MAJOR, octaves=10)
        for note in notes:
            # Check note is in scale (any octave)
            note_in_octave = note.note_number % 12
            scale_intervals = [n % 12 for n in scale_notes]
            assert note_in_octave in scale_intervals


class TestArpeggiate:
    """Tests for arpeggiate function."""
    
    def test_up_pattern(self):
        """Test upward arpeggio."""
        chord = Chord.get_notes(60, Chord.MAJOR)
        notes = arpeggiate(chord, pattern="up", total_beats=2.0)
        
        assert len(notes) > 0
        # Check ascending order within first cycle
        for i in range(min(len(chord) - 1, len(notes) - 1)):
            assert notes[i].note_number <= notes[i + 1].note_number
    
    def test_down_pattern(self):
        """Test downward arpeggio."""
        chord = Chord.get_notes(60, Chord.MAJOR)
        notes = arpeggiate(chord, pattern="down", total_beats=2.0)
        
        assert len(notes) > 0


class TestHumanize:
    """Tests for humanize function."""
    
    def test_humanize_preserves_count(self):
        """Test that humanize preserves note count."""
        notes = [MidiNote(60 + i, i * 0.5, 0.5, 100) for i in range(8)]
        humanized = humanize(notes, timing_variance=0.02, velocity_variance=5)
        
        assert len(humanized) == len(notes)
    
    def test_humanize_changes_values(self):
        """Test that humanize actually modifies values."""
        notes = [MidiNote(60, 0.5, 0.5, 100)]
        
        # Run multiple times, at least one should differ
        found_difference = False
        for _ in range(10):
            humanized = humanize(notes, timing_variance=0.1, velocity_variance=20)
            if (humanized[0].start_beat != 0.5 or 
                humanized[0].velocity != 100):
                found_difference = True
                break
        
        assert found_difference


class TestRemoveOverlaps:
    """Tests for remove_overlaps function."""
    
    def test_no_overlaps(self):
        """Test with non-overlapping notes."""
        notes = [
            MidiNote(60, 0.0, 0.5, 100),
            MidiNote(60, 0.5, 0.5, 100),
            MidiNote(60, 1.0, 0.5, 100),
        ]
        result = remove_overlaps(notes)
        assert len(result) == 3
    
    def test_with_overlaps(self):
        """Test truncation of overlapping notes."""
        notes = [
            MidiNote(60, 0.0, 1.0, 100),  # Overlaps with next
            MidiNote(60, 0.5, 1.0, 100),
        ]
        result = remove_overlaps(notes, mode="truncate")
        
        # First note should be truncated
        assert result[0].length_beats == 0.5
        assert result[1].start_beat == 0.5

