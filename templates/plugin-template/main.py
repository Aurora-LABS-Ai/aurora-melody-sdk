"""
Aurora Melody Plugin Template
=============================

This is a template for creating Aurora Melody plugins.
Replace this docstring with your plugin description.

Quick Start:
1. Rename the class below to your plugin name
2. Update the name, author, version attributes
3. Implement the generate() method
4. Test locally with: python main.py
5. Package with: python aurora-pack.py ./your-plugin-folder

For full documentation, see: https://github.com/aurora-melody/sdk
"""

# =============================================================================
# Imports
# =============================================================================

import random
from typing import List, Dict, Any


# =============================================================================
# Aurora SDK Classes (fallback if SDK not available)
# =============================================================================

class MidiNote:
    """
    Represents a MIDI note.
    
    Attributes:
        note_number: MIDI note (0-127, 60=C4)
        start_beat: Start position in beats
        length_beats: Duration in beats
        velocity: Note velocity (0-127)
        channel: MIDI channel (1-16)
    """
    def __init__(self, 
                 note_number: int = 60, 
                 start_beat: float = 0.0, 
                 length_beats: float = 1.0, 
                 velocity: int = 100, 
                 channel: int = 1):
        self.note_number = note_number
        self.start_beat = start_beat
        self.length_beats = length_beats
        self.velocity = velocity
        self.channel = channel


class AuroraPlugin:
    """Base class for Aurora Melody plugins."""
    pass


# =============================================================================
# Your Plugin Class
# =============================================================================

class MyPlugin(AuroraPlugin):
    """
    Your Plugin Description Here
    
    Explain what your plugin does and how to use it.
    """
    
    # =========================================================================
    # Plugin Metadata (REQUIRED)
    # =========================================================================
    
    name = "My Plugin"
    author = "Your Name"
    version = "1.0.0"
    description = "Does something amazing with MIDI notes"
    
    # =========================================================================
    # Plugin Parameters (OPTIONAL)
    # These will appear in the plugin UI
    # =========================================================================
    
    parameters = [
        # Integer parameter
        {
            "id": "num_notes",
            "name": "Number of Notes",
            "type": "int",
            "min": 1,
            "max": 64,
            "default": 8
        },
        # Choice parameter (dropdown)
        {
            "id": "mode",
            "name": "Mode",
            "type": "choice",
            "choices": ["Option A", "Option B", "Option C"],
            "default": "Option A"
        },
        # Float parameter
        {
            "id": "density",
            "name": "Note Density",
            "type": "float",
            "min": 0.0,
            "max": 1.0,
            "default": 0.5
        }
    ]
    
    # =========================================================================
    # Helper Methods (OPTIONAL)
    # =========================================================================
    
    def __init__(self):
        """Initialize your plugin. Called once when loaded."""
        # Add any initialization code here
        pass
    
    def on_load(self):
        """Called when the plugin is loaded into Aurora Melody."""
        pass
    
    def on_unload(self):
        """Called when the plugin is unloaded."""
        pass
    
    # =========================================================================
    # Main Generation Method (REQUIRED)
    # =========================================================================
    
    def generate(self, context) -> List[MidiNote]:
        """
        Generate MIDI notes based on the current piano roll state.
        
        This is the main method you must implement!
        
        Args:
            context: Dictionary or object containing:
                - notes: List of existing notes in piano roll
                - selectedNoteIds: IDs of selected notes
                - tempoBPM: Current tempo
                - playheadPosition: Current playhead position in beats
                - parameters: User-defined parameter values
        
        Returns:
            List of MidiNote objects to add to the piano roll
        """
        
        # ---------------------------------------------------------------------
        # 1. Get parameters from context
        # ---------------------------------------------------------------------
        
        params = context if isinstance(context, dict) else {}
        if hasattr(context, 'parameters'):
            params = context.parameters
        
        num_notes = int(params.get('num_notes', 8))
        mode = params.get('mode', 'Option A')
        density = float(params.get('density', 0.5))
        
        # Get playhead position (where to start generating)
        start_beat = 0.0
        if hasattr(context, 'playhead_position'):
            start_beat = context.playhead_position
        elif isinstance(context, dict):
            start_beat = context.get('playheadPosition', 0.0)
        
        # ---------------------------------------------------------------------
        # 2. Generate your notes
        # ---------------------------------------------------------------------
        
        notes = []
        
        for i in range(num_notes):
            # Example: Generate random notes on C major scale
            scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
            
            note_number = random.choice(scale)
            velocity = random.randint(70, 100)
            note_length = 0.5 if density > 0.5 else 1.0
            
            notes.append(MidiNote(
                note_number=note_number,
                start_beat=start_beat + (i * note_length),
                length_beats=note_length * 0.9,
                velocity=velocity,
                channel=1
            ))
        
        # ---------------------------------------------------------------------
        # 3. Return generated notes
        # ---------------------------------------------------------------------
        
        return notes


# =============================================================================
# Local Testing
# =============================================================================

if __name__ == "__main__":
    """
    Test your plugin locally without Aurora Melody.
    
    Run with: python main.py
    """
    
    print("Testing plugin...")
    
    # Create plugin instance
    plugin = MyPlugin()
    
    # Create mock context (simulates what Aurora sends)
    mock_context = {
        'notes': [],
        'selectedNoteIds': [],
        'tempoBPM': 120.0,
        'playheadPosition': 0.0,
        'parameters': {
            'num_notes': 8,
            'mode': 'Option A',
            'density': 0.5
        }
    }
    
    # Generate notes
    notes = plugin.generate(mock_context)
    
    # Print results
    print(f"\nGenerated {len(notes)} notes:")
    print("-" * 50)
    
    for i, note in enumerate(notes):
        print(f"  {i+1}. Note {note.note_number:3d} | "
              f"Beat {note.start_beat:6.2f} | "
              f"Length {note.length_beats:.2f} | "
              f"Velocity {note.velocity:3d}")
    
    print("-" * 50)
    print("Plugin test complete!")

