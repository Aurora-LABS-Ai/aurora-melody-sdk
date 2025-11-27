"""
AI Service Plugin base class for Aurora Melody.

SDK controls everything - developers define:
- Endpoint URL (internal, not shown to user)
- UI controls (sliders, knobs, buttons, input boxes)
- All request/response handling
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from aurora_melody_sdk.plugin import AuroraPlugin, PluginParameter, ParameterType
from aurora_melody_sdk.note import MidiNote


class AIControlType(Enum):
    """UI control types for AI plugins."""
    SLIDER = "slider"           # Horizontal slider with value
    KNOB = "knob"              # Rotary knob
    DROPDOWN = "dropdown"       # Dropdown selector
    BUTTON = "button"          # Push button
    TOGGLE = "toggle"          # On/Off toggle
    INPUT = "input"            # Text input box
    LABEL = "label"            # Display label (read-only)


@dataclass
class AIControl:
    """
    Definition of a UI control for AI plugins.
    
    Developers use this to define what controls appear in the AI panel.
    
    Attributes:
        id: Unique identifier for the control
        name: Display label
        control_type: Type of control (slider, knob, dropdown, etc.)
        default: Default value
        min_value: Minimum value (for slider/knob)
        max_value: Maximum value (for slider/knob)
        step: Step increment (for slider/knob)
        choices: List of choices (for dropdown)
        placeholder: Placeholder text (for input)
        description: Tooltip/help text
        row: Row position (for layout, 0-based)
        width: Width in grid units (1-4, default 1)
    
    Example::
    
        controls = [
            AIControl("tempo", "Tempo", AIControlType.KNOB, 120, 60, 200),
            AIControl("style", "Style", AIControlType.DROPDOWN, "Jazz",
                     choices=["Jazz", "Classical", "Pop"]),
            AIControl("prompt", "Description", AIControlType.INPUT,
                     placeholder="Describe your melody..."),
        ]
    """
    id: str
    name: str
    control_type: AIControlType
    default: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    choices: List[str] = field(default_factory=list)
    placeholder: str = ""
    description: str = ""
    row: int = 0
    width: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for manifest."""
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.control_type.value,
            "default": self.default,
        }
        
        if self.min_value is not None:
            result["min"] = self.min_value
        if self.max_value is not None:
            result["max"] = self.max_value
        if self.step is not None:
            result["step"] = self.step
        if self.choices:
            result["choices"] = self.choices
        if self.placeholder:
            result["placeholder"] = self.placeholder
        if self.description:
            result["description"] = self.description
        if self.row > 0:
            result["row"] = self.row
        if self.width != 1:
            result["width"] = self.width
        
        return result


@dataclass 
class AIResponse:
    """
    Standard response format from AI melody generation.
    
    Expected JSON format from your endpoint:
    {
        "status": "success",
        "request_id": "uuid-string",
        "timestamp": "ISO-timestamp",
        "melodies": [
            {
                "id": "melody-id",
                "notes": [
                    {"pitch": 60, "start_time": 0, "duration": 0.5, "velocity": 100, "channel": 0},
                    ...
                ]
            }
        ]
    }
    """
    notes: List[MidiNote] = field(default_factory=list)
    success: bool = True
    error: str = ""
    request_id: str = ""
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'AIResponse':
        """
        Parse response from AI service.
        
        Expects format:
        {
            "status": "success",
            "request_id": "...",
            "melodies": [{"notes": [...]}]
        }
        """
        # Check status
        status = data.get("status", "error")
        if status != "success":
            return cls(
                success=False,
                error=data.get("error", data.get("message", "Unknown error")),
                request_id=data.get("request_id", "")
            )
        
        # Parse notes from melodies array
        notes = []
        melodies = data.get("melodies", [])
        
        for melody in melodies:
            for note_data in melody.get("notes", []):
                note = MidiNote(
                    note_number=note_data.get("pitch", 60),
                    start_beat=note_data.get("start_time", 0.0),
                    length_beats=note_data.get("duration", 0.5),
                    velocity=note_data.get("velocity", 100),
                    channel=note_data.get("channel", 0) + 1  # Convert 0-based to 1-based
                )
                notes.append(note)
        
        return cls(
            notes=notes,
            success=True,
            request_id=data.get("request_id", "")
        )


class AIServicePlugin(AuroraPlugin):
    """
    Base class for AI-powered melody generation plugins.
    
    The SDK controls everything - you define:
    - endpoint: Your AI service URL (hidden from user)
    - controls: UI elements (sliders, knobs, dropdowns, inputs)
    - Request/response handling
    
    Example::
    
        from aurora_melody_sdk import AIServicePlugin, AIControl, AIControlType
        
        class MyAIPlugin(AIServicePlugin):
            name = "My AI Generator"
            author = "Your Name"
            version = "1.0.0"
            
            # Your endpoint (not shown to user)
            endpoint = "https://api.myservice.com/generate"
            
            # Define UI controls
            controls = [
                AIControl("temperature", "Temperature", AIControlType.KNOB,
                         default=0.7, min_value=0.1, max_value=1.0, step=0.1),
                AIControl("style", "Style", AIControlType.DROPDOWN,
                         default="Jazz", choices=["Jazz", "Pop", "Classical"]),
                AIControl("bars", "Bars", AIControlType.SLIDER,
                         default=8, min_value=1, max_value=32),
            ]
            
            # Optional: Add text input
            has_input = True
            input_placeholder = "Describe your melody..."
            
            def build_request(self, params: dict) -> dict:
                '''Build request for your API.'''
                return {
                    "temperature": params.get("temperature", 0.7),
                    "style": params.get("style", "Jazz"),
                    "bars": params.get("bars", 8),
                    "prompt": params.get("_input", ""),  # Text input value
                }
    
    manifest.json Format::
    
        {
            "id": "com.company.my-ai-plugin",
            "name": "My AI Generator",
            "type": "ai",
            "entry": "main.py",
            "endpoint": "https://api.myservice.com/generate",
            "controls": [
                {"id": "temperature", "name": "Temperature", "type": "knob",
                 "default": 0.7, "min": 0.1, "max": 1.0},
                {"id": "style", "name": "Style", "type": "dropdown",
                 "default": "Jazz", "choices": ["Jazz", "Pop", "Classical"]}
            ],
            "hasInput": true,
            "inputPlaceholder": "Describe your melody..."
        }
    """
    
    # Your AI service endpoint (hidden from user)
    endpoint: str = ""
    
    # UI controls defined by developer
    controls: List[AIControl] = []
    
    # Optional text input
    has_input: bool = False
    input_placeholder: str = "Enter description..."
    
    # Request settings
    request_timeout: int = 30
    headers: Dict[str, str] = {}
    
    def generate(self, context) -> List[MidiNote]:
        """
        Main generation method called by Aurora Melody.
        
        1. Extracts parameters from context
        2. Calls build_request() for you to customize
        3. Sends to endpoint
        4. Parses response using standard format
        """
        # Get parameters from context
        if hasattr(context, 'parameters'):
            params = dict(context.parameters)
        elif isinstance(context, dict):
            params = context.get('parameters', {})
        else:
            params = {}
        
        # Build request
        request_data = self.build_request(params)
        
        # Send to endpoint
        response_data = self._send_request(request_data)
        
        # Parse response
        response = AIResponse.from_api_response(response_data)
        
        if not response.success:
            raise Exception(response.error)
        
        return response.notes
    
    def build_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build the request payload for your AI service.
        
        Override this to customize how parameters are sent to your API.
        
        Args:
            params: Dictionary of parameter values from UI controls
                   Text input value is in params["_input"]
        
        Returns:
            Dictionary to send to your endpoint
        """
        # Default: send all parameters as-is
        return params
    
    def get_controls_dict(self) -> List[Dict[str, Any]]:
        """Get controls as list of dictionaries for manifest."""
        return [c.to_dict() for c in self.controls]
    
    def _send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to endpoint."""
        import urllib.request
        import json
        
        if not self.endpoint:
            return {"status": "error", "error": "No endpoint configured"}
        
        try:
            headers = {"Content-Type": "application/json"}
            headers.update(self.headers)
            
            req = urllib.request.Request(
                self.endpoint,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=self.request_timeout) as response:
                return json.loads(response.read().decode('utf-8'))
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
