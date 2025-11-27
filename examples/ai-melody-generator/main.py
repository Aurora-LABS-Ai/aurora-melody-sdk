"""
AI Melody Generator - Example AI Plugin

This plugin demonstrates how to:
1. Define UI controls
2. Call your own endpoint
3. Parse YOUR response format
4. Return standard MidiNote objects

Aurora Melody only receives MidiNote - YOU handle everything else.
"""

from typing import List
from aurora_melody_sdk import (
    AIServicePlugin, AIControl, AIControlType,
    MidiNote, PluginContext
)


class AIGenerator(AIServicePlugin):
    """
    AI-powered melody generator.
    
    YOU control:
    - Your endpoint
    - Your request format
    - Your response parsing
    
    Aurora Melody only sees: List[MidiNote]
    """
    
    name = "AI Melody Generator"
    author = "Aurora Melody Labs"
    version = "1.0.0"
    description = "Generate melodies using AI"
    
    # YOUR endpoint (user never sees this)
    endpoint = "https://api.example.com/generate"
    
    # YOUR headers
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
    }
    
    # UI controls (rendered in Aurora Melody)
    controls = [
        AIControl("temperature", "Temperature", AIControlType.KNOB,
                  default=0.7, min_value=0.1, max_value=1.0, step=0.1),
        AIControl("bars", "Bars", AIControlType.KNOB,
                  default=8, min_value=1, max_value=32, step=1),
        AIControl("style", "Style", AIControlType.DROPDOWN,
                  default="Jazz", choices=["Jazz", "Classical", "Pop", "Electronic"]),
        AIControl("density", "Density", AIControlType.SLIDER,
                  default=5, min_value=1, max_value=10, step=1),
    ]
    
    has_input = True
    input_placeholder = "Describe your melody (optional)..."
    
    def generate(self, context: PluginContext) -> List[MidiNote]:
        """
        Generate notes - YOU control everything here.
        
        1. Build YOUR request format
        2. Call YOUR endpoint
        3. Parse YOUR response format
        4. Return standard MidiNote list
        """
        
        # 1. Build YOUR request (whatever format your API expects)
        request = {
            "temperature": context.get_param("temperature", 0.7),
            "bars": int(context.get_param("bars", 8)),
            "style": context.get_param("style", "Jazz"),
            "density": int(context.get_param("density", 5)),
            "prompt": context.get_param("_input", ""),
            # Add any other data your API needs
            "tempo_bpm": context.tempo_bpm,
        }
        
        # 2. Call YOUR endpoint
        try:
            response = self.call_endpoint(request)
        except Exception as e:
            # Handle error - could show message, use fallback, etc.
            raise Exception(f"Failed to call AI service: {e}")
        
        # 3. Parse YOUR response format
        # YOUR API might return ANY format - you handle it
        
        # Example: If your API returns the standard format
        # {"status": "success", "melodies": [{"notes": [...]}]}
        # You can use the helper:
        # return self.parse_standard_response(response)
        
        # Example: If your API returns a DIFFERENT format,
        # parse it yourself:
        notes = []
        
        # Maybe your API returns: {"generated": [{"p": 60, "t": 0, "d": 0.5}]}
        for item in response.get("generated", response.get("notes", [])):
            # Map YOUR field names to MidiNote
            note = MidiNote(
                note_number=item.get("p", item.get("pitch", 60)),
                start_beat=item.get("t", item.get("start_time", item.get("time", 0.0))),
                length_beats=item.get("d", item.get("duration", item.get("length", 0.5))),
                velocity=item.get("v", item.get("velocity", item.get("vel", 100))),
                channel=item.get("ch", item.get("channel", 0)) + 1
            )
            notes.append(note)
        
        # 4. Return standard MidiNote list
        # Aurora Melody only sees this - doesn't know about your API format
        return notes


# Required: Plugin class for Aurora Melody to instantiate
Plugin = AIGenerator
