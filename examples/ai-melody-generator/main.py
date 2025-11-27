"""
AI Melody Generator - Example AI Service Plugin

This demonstrates how to create an AI-powered melody generator.
The plugin defines:
- endpoint: Your AI service URL (hidden from user)
- controls: UI elements (sliders, knobs, dropdowns)
- How to build requests and parse responses
"""

from aurora_melody_sdk import (
    AIServicePlugin, AIControl, AIControlType, AIResponse, MidiNote
)


class AIGenerator(AIServicePlugin):
    """
    AI-powered melody generator.
    
    The SDK handles everything:
    - UI is dynamically generated from manifest.json
    - Endpoint is hidden from user
    - Request/response handling is standardized
    """
    
    name = "AI Melody Generator"
    author = "Aurora Melody Labs"
    version = "1.0.0"
    description = "Generate melodies using AI"
    
    # Your AI service endpoint (hidden from user, defined in manifest.json)
    endpoint = "https://api.example.com/generate"
    
    # HTTP headers for your API
    headers = {
        "Authorization": "Bearer YOUR_API_KEY",
        "Content-Type": "application/json"
    }
    
    # UI controls defined in manifest.json, but you can also define them here:
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
    
    # Enable text input
    has_input = True
    input_placeholder = "Describe your melody..."
    
    def build_request(self, params: dict) -> dict:
        """
        Build request payload for your AI service.
        
        params contains values from UI controls + "_input" for text input.
        """
        return {
            "temperature": params.get("temperature", 0.7),
            "bars": int(params.get("bars", 8)),
            "style": params.get("style", "Jazz"),
            "density": int(params.get("density", 5)),
            "prompt": params.get("_input", ""),  # Text input value
        }


# The plugin class that Aurora Melody will instantiate
Plugin = AIGenerator
