"""
AI Service Plugin base class for Aurora Melody.

Use this to create AI-powered melody generation plugins that connect
to external AI services (HTTP/WebSocket).
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

from aurora_melody_sdk.plugin import AuroraPlugin, PluginParameter, ParameterType
from aurora_melody_sdk.note import MidiNote


class ConnectionType(Enum):
    """Type of connection to AI service."""
    HTTP_POST = "http_post"
    HTTP_GET = "http_get"
    WEBSOCKET = "websocket"


@dataclass
class AIRequest:
    """
    Standard request format for AI melody generation.
    
    Aurora Melody sends this to your AI endpoint.
    
    Attributes:
        key: Musical key (C, C#, D, etc.)
        scale: Scale name (Major, Minor, Blues, etc.)
        style: Musical style (Jazz, Classical, Pop, etc.)
        length_bars: Number of bars to generate
        density: Note density (1-10)
        creativity: Creativity level (1-10)
        tempo_bpm: Tempo in beats per minute
        prompt: Optional text description
        existing_notes: Current notes in piano roll
        playhead_position: Current playhead position in beats
        custom: Additional custom parameters from plugin
    """
    key: str = "C"
    scale: str = "Major"
    style: str = "Classical"
    length_bars: int = 8
    density: int = 5
    creativity: int = 5
    tempo_bpm: int = 120
    prompt: str = ""
    existing_notes: List[Dict[str, Any]] = field(default_factory=list)
    playhead_position: float = 0.0
    custom: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "key": self.key,
            "scale": self.scale,
            "style": self.style,
            "length_bars": self.length_bars,
            "density": self.density,
            "creativity": self.creativity,
            "tempo_bpm": self.tempo_bpm,
            "prompt": self.prompt,
            "existing_notes": self.existing_notes,
            "playhead_position": self.playhead_position,
            "custom": self.custom,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIRequest':
        """Create from dictionary."""
        return cls(
            key=data.get("key", "C"),
            scale=data.get("scale", "Major"),
            style=data.get("style", "Classical"),
            length_bars=data.get("length_bars", 8),
            density=data.get("density", 5),
            creativity=data.get("creativity", 5),
            tempo_bpm=data.get("tempo_bpm", 120),
            prompt=data.get("prompt", ""),
            existing_notes=data.get("existing_notes", []),
            playhead_position=data.get("playhead_position", 0.0),
            custom=data.get("custom", {}),
        )


@dataclass
class AIResponse:
    """
    Standard response format from AI melody generation.
    
    Your AI endpoint should return this format.
    
    Attributes:
        notes: List of generated notes
        success: Whether generation succeeded
        error: Error message if failed
        metadata: Optional metadata about the generation
    """
    notes: List[MidiNote] = field(default_factory=list)
    success: bool = True
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "notes": [n.to_dict() for n in self.notes],
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIResponse':
        """Create from dictionary."""
        notes = []
        for n in data.get("notes", []):
            if isinstance(n, dict):
                notes.append(MidiNote.from_dict(n))
            elif isinstance(n, MidiNote):
                notes.append(n)
        
        return cls(
            notes=notes,
            success=data.get("success", True),
            error=data.get("error", ""),
            metadata=data.get("metadata", {}),
        )


class AIServicePlugin(AuroraPlugin):
    """
    Base class for AI-powered melody generation plugins.
    
    Extend this class to create plugins that connect to external AI services.
    Aurora Melody provides built-in musical controls (key, scale, style, etc.)
    that are automatically sent to your endpoint.
    
    Required Attributes:
        name: Display name of your AI plugin
        author: Your name/organization
        version: Version string
        endpoint: URL of your AI service (HTTP or WebSocket)
    
    Optional Attributes:
        connection_type: HTTP_POST (default), HTTP_GET, or WEBSOCKET
        extra_parameters: Additional parameters beyond built-in ones
        request_timeout: Timeout in seconds (default 30)
        headers: Custom HTTP headers
    
    Example::
    
        from aurora_melody_sdk import AIServicePlugin, ConnectionType
        
        class MyAIPlugin(AIServicePlugin):
            name = "GPT Melody Generator"
            author = "My Company"
            version = "1.0.0"
            endpoint = "https://api.myservice.com/generate"
            connection_type = ConnectionType.HTTP_POST
            
            # Optional: Add custom parameters
            extra_parameters = [
                PluginParameter("model", "AI Model", ParameterType.CHOICE,
                               default="gpt-4", choices=["gpt-4", "gpt-3.5"]),
                PluginParameter("temperature", "Temperature", ParameterType.FLOAT,
                               default=0.7, min_value=0.0, max_value=1.0),
            ]
            
            # Optional: Transform request before sending
            def prepare_request(self, request: AIRequest) -> Dict[str, Any]:
                data = request.to_dict()
                # Add your API-specific fields
                data["api_key"] = "your-key"
                return data
            
            # Optional: Transform response after receiving
            def parse_response(self, response: Dict[str, Any]) -> AIResponse:
                # Parse your API-specific response format
                notes = []
                for item in response.get("generated_melody", []):
                    notes.append(MidiNote(
                        note_number=item["pitch"],
                        start_beat=item["time"],
                        length_beats=item["duration"],
                        velocity=item.get("velocity", 100)
                    ))
                return AIResponse(notes=notes)
    
    manifest.json Format::
    
        {
            "id": "com.mycompany.gpt-melody",
            "name": "GPT Melody Generator",
            "version": "1.0.0",
            "author": "My Company",
            "description": "AI-powered melody generation using GPT",
            "type": "ai",
            "entry": "main.py",
            "endpoint": "https://api.myservice.com/generate",
            "connectionType": "http_post",
            "requestTimeout": 30,
            "headers": {
                "Authorization": "Bearer YOUR_API_KEY"
            },
            "extraParameters": [
                {
                    "id": "model",
                    "name": "AI Model",
                    "type": "choice",
                    "default": "gpt-4",
                    "choices": ["gpt-4", "gpt-3.5"]
                }
            ]
        }
    """
    
    # Required: Your AI service endpoint
    endpoint: str = ""
    
    # Connection settings
    connection_type: ConnectionType = ConnectionType.HTTP_POST
    request_timeout: int = 30
    headers: Dict[str, str] = {}
    
    # Additional parameters beyond built-in musical controls
    extra_parameters: List[PluginParameter] = []
    
    def __init__(self):
        super().__init__()
        # AI plugins use built-in parameters + extra_parameters
        self.parameters = self.extra_parameters
    
    def generate(self, context) -> List[MidiNote]:
        """
        Generate notes using the AI service.
        
        This method is called by Aurora Melody. It:
        1. Builds an AIRequest from the context
        2. Calls prepare_request() for customization
        3. Sends to the endpoint
        4. Calls parse_response() to get notes
        
        You typically don't need to override this method.
        Override prepare_request() and parse_response() instead.
        """
        # Build request from context
        request = self._build_request(context)
        
        # Let subclass customize
        request_data = self.prepare_request(request)
        
        # Send to endpoint (Aurora Melody handles this)
        # The response will be passed to parse_response()
        
        # For standalone testing, we can make the request ourselves
        response_data = self._send_request(request_data)
        
        # Parse response
        response = self.parse_response(response_data)
        
        if not response.success:
            raise Exception(response.error)
        
        return response.notes
    
    def prepare_request(self, request: AIRequest) -> Dict[str, Any]:
        """
        Customize the request before sending to your AI service.
        
        Override this to add API keys, transform data, etc.
        
        Args:
            request: The AIRequest with all musical parameters
        
        Returns:
            Dictionary to send to your endpoint
        """
        return request.to_dict()
    
    def parse_response(self, response: Dict[str, Any]) -> AIResponse:
        """
        Parse the response from your AI service.
        
        Override this to handle your API's response format.
        
        Args:
            response: Raw response dictionary from your endpoint
        
        Returns:
            AIResponse with generated notes
        """
        return AIResponse.from_dict(response)
    
    def _build_request(self, context) -> AIRequest:
        """Build AIRequest from plugin context."""
        # Context comes from Aurora Melody with musical parameters
        if hasattr(context, 'parameters'):
            params = context.parameters
        elif isinstance(context, dict):
            params = context.get('parameters', {})
        else:
            params = {}
        
        # Extract existing notes
        existing_notes = []
        if hasattr(context, 'notes'):
            for note in context.notes:
                if isinstance(note, MidiNote):
                    existing_notes.append(note.to_dict())
                elif isinstance(note, dict):
                    existing_notes.append(note)
        
        return AIRequest(
            key=params.get("key", "C"),
            scale=params.get("scale", "Major"),
            style=params.get("style", "Classical"),
            length_bars=params.get("length_bars", 8),
            density=params.get("density", 5),
            creativity=params.get("creativity", 5),
            tempo_bpm=params.get("tempo_bpm", getattr(context, 'tempo_bpm', 120)),
            prompt=params.get("prompt", ""),
            existing_notes=existing_notes,
            playhead_position=getattr(context, 'playhead_position', 0.0),
            custom={k: v for k, v in params.items() 
                   if k not in ["key", "scale", "style", "length_bars", 
                               "density", "creativity", "tempo_bpm", "prompt"]},
        )
    
    def _send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send request to endpoint.
        
        This is a fallback for standalone testing.
        Aurora Melody handles the actual HTTP/WebSocket communication.
        """
        import urllib.request
        import json
        
        if not self.endpoint:
            return {"success": False, "error": "No endpoint configured"}
        
        try:
            headers = {"Content-Type": "application/json"}
            headers.update(self.headers)
            
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST' if self.connection_type == ConnectionType.HTTP_POST else 'GET'
            )
            
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        
        except Exception as e:
            return {"success": False, "error": str(e)}

