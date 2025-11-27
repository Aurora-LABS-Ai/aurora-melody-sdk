"""
AI Melody Generator - Example AI Service Plugin

This demonstrates how to create an AI-powered melody generator
that connects to an external AI service.

The plugin uses Aurora Melody's built-in musical controls:
- Key (C, C#, D, etc.)
- Scale (Major, Minor, Blues, etc.)
- Style (Jazz, Classical, Pop, etc.)
- Length, Density, Creativity
- Tempo
- Prompt (text description)

You just need to:
1. Set your endpoint URL
2. Optionally customize prepare_request() and parse_response()
"""

from aurora_melody_sdk import (
    AIServicePlugin, AIRequest, AIResponse,
    MidiNote, ConnectionType, PluginParameter, ParameterType
)


class AIGenerator(AIServicePlugin):
    """
    AI-powered melody generator.
    
    Connects to an external AI service to generate melodies
    based on musical parameters and optional text prompts.
    """
    
    name = "AI Melody Generator"
    author = "Aurora Melody Labs"
    version = "1.0.0"
    description = "Generate melodies using AI"
    
    # Your AI service endpoint
    # Change this to your actual endpoint
    endpoint = "https://api.example.com/generate"
    
    # Connection settings
    connection_type = ConnectionType.HTTP_POST
    request_timeout = 30
    
    # Custom HTTP headers (e.g., for authentication)
    headers = {
        "Authorization": "Bearer YOUR_API_KEY_HERE",
        "X-Client": "Aurora-Melody-SDK",
    }
    
    # Additional parameters beyond built-in musical controls
    extra_parameters = [
        PluginParameter(
            id="model",
            name="AI Model",
            param_type=ParameterType.CHOICE,
            default="melody-v1",
            choices=["melody-v1", "melody-v2", "experimental"],
            description="Which AI model to use for generation"
        ),
        PluginParameter(
            id="temperature",
            name="Temperature",
            param_type=ParameterType.FLOAT,
            default=0.7,
            min_value=0.1,
            max_value=1.0,
            step=0.1,
            description="Higher = more creative/random"
        ),
    ]
    
    def prepare_request(self, request: AIRequest) -> dict:
        """
        Customize the request before sending to your AI service.
        
        This is where you transform Aurora Melody's standard request
        into whatever format your AI service expects.
        """
        # Start with the standard request data
        data = request.to_dict()
        
        # Add custom parameters
        data["model"] = request.custom.get("model", "melody-v1")
        data["temperature"] = request.custom.get("temperature", 0.7)
        
        # Transform to your API's expected format if needed
        # Example: Your API might expect different field names
        api_request = {
            "musical_key": data["key"],
            "scale_type": data["scale"],
            "genre": data["style"],
            "bars": data["length_bars"],
            "note_density": data["density"] / 10.0,  # Normalize to 0-1
            "creativity_level": data["creativity"] / 10.0,
            "bpm": data["tempo_bpm"],
            "description": data["prompt"],
            "context_notes": data["existing_notes"],
            "model_version": data["model"],
            "sampling_temperature": data["temperature"],
        }
        
        return api_request
    
    def parse_response(self, response: dict) -> AIResponse:
        """
        Parse the response from your AI service.
        
        Transform your API's response format into Aurora Melody's
        standard AIResponse format.
        """
        # Check for errors
        if not response.get("success", True):
            return AIResponse(
                success=False,
                error=response.get("error", "Unknown error from AI service")
            )
        
        # Parse notes from your API's format
        notes = []
        
        # Example: Your API returns notes in its own format
        for item in response.get("generated_notes", response.get("notes", [])):
            # Handle different possible formats
            if isinstance(item, dict):
                note = MidiNote(
                    # Your API might use different field names
                    note_number=item.get("pitch", item.get("noteNumber", 60)),
                    start_beat=item.get("time", item.get("startBeat", 0.0)),
                    length_beats=item.get("duration", item.get("lengthBeats", 0.5)),
                    velocity=item.get("velocity", 100),
                    channel=item.get("channel", 1)
                )
                notes.append(note)
        
        return AIResponse(
            notes=notes,
            success=True,
            metadata={
                "model_used": response.get("model", "unknown"),
                "generation_time_ms": response.get("generation_time", 0),
            }
        )


# The plugin class that Aurora Melody will instantiate
# Must be named 'Plugin' or match the class name in manifest
Plugin = AIGenerator

