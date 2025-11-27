"""
AI Service Plugin base class for Aurora Melody.

Plugin controls EVERYTHING:
- Your endpoint
- Your request format
- Your response format
- Converting to standard MidiNote format

Piano roll only accepts standard MidiNote - plugin handles all conversion.
"""

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import json
import urllib.request

from aurora_melody_sdk.plugin import AuroraPlugin, PluginParameter, ParameterType
from aurora_melody_sdk.note import MidiNote
from aurora_melody_sdk.context import PluginContext


class AIControlType(Enum):
    """UI control types for AI plugins."""
    SLIDER = "slider"
    KNOB = "knob"
    DROPDOWN = "dropdown"
    BUTTON = "button"
    TOGGLE = "toggle"
    INPUT = "input"
    LABEL = "label"


@dataclass
class AIControl:
    """
    UI control definition for AI plugins.
    
    Example::
    
        controls = [
            AIControl("temp", "Temperature", AIControlType.KNOB,
                      default=0.7, min_value=0.1, max_value=1.0),
            AIControl("style", "Style", AIControlType.DROPDOWN,
                      default="Jazz", choices=["Jazz", "Pop"]),
            AIControl("prompt", "Description", AIControlType.INPUT,
                      placeholder="Describe melody..."),
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
    
    def to_dict(self) -> Dict[str, Any]:
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
        return result


class AIServicePlugin(AuroraPlugin):
    """
    Base class for AI-powered melody generation plugins.
    
    YOU control everything:
    - Your endpoint URL
    - Your request format  
    - Your response format
    - Converting response to MidiNote
    
    Aurora Melody only receives standard MidiNote objects.
    
    Example - Simple API::
    
        class MyPlugin(AIServicePlugin):
            name = "My AI"
            endpoint = "https://api.example.com/generate"
            
            controls = [
                AIControl("temp", "Temperature", AIControlType.KNOB, 0.7, 0.1, 1.0),
            ]
            
            def generate(self, context: PluginContext) -> List[MidiNote]:
                # 1. Build YOUR request
                request = {"temperature": context.get_param("temp", 0.7)}
                
                # 2. Call YOUR endpoint
                response = self.call_endpoint(request)
                
                # 3. Parse YOUR response format and return MidiNote
                notes = []
                for n in response["generated_notes"]:
                    notes.append(MidiNote(
                        note_number=n["pitch"],
                        start_beat=n["time"],
                        length_beats=n["duration"],
                        velocity=n["vel"]
                    ))
                return notes
    
    Example - Common AI Format::
    
        class MyPlugin(AIServicePlugin):
            name = "My AI"
            endpoint = "https://api.example.com/generate"
            
            def generate(self, context: PluginContext) -> List[MidiNote]:
                request = self.build_request(context)
                response = self.call_endpoint(request)
                
                # Use helper for common format
                return self.parse_standard_response(response)
    """
    
    # Your endpoint (required)
    endpoint: str = ""
    
    # UI controls
    controls: List[AIControl] = []
    
    # Optional text input
    has_input: bool = False
    input_placeholder: str = ""
    
    # HTTP settings
    request_timeout: int = 30
    headers: Dict[str, str] = {}
    
    @abstractmethod
    def generate(self, context: PluginContext) -> List[MidiNote]:
        """
        Generate notes from your AI service.
        
        YOU are responsible for:
        1. Building the request for YOUR API
        2. Calling YOUR endpoint
        3. Parsing YOUR response format
        4. Returning standard MidiNote objects
        
        Use helper methods:
        - self.call_endpoint(data) - Make HTTP POST request
        - self.parse_standard_response(response) - Parse common format
        """
        pass
    
    def call_endpoint(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP POST request to your endpoint.
        
        Args:
            data: Request payload (will be JSON encoded)
        
        Returns:
            Response as dictionary
        
        Raises:
            Exception: On network or parsing error
        """
        if not self.endpoint:
            raise Exception("No endpoint configured")
        
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)
        
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def parse_standard_response(self, response: Dict[str, Any]) -> List[MidiNote]:
        """
        Parse common AI response format to MidiNote.
        
        Expected format:
        {
            "status": "success",
            "melodies": [
                {
                    "notes": [
                        {"pitch": 60, "start_time": 0, "duration": 0.5, 
                         "velocity": 100, "channel": 0}
                    ]
                }
            ]
        }
        
        Use this helper if your API returns this format,
        or write your own parsing in generate().
        """
        if response.get("status") != "success":
            error = response.get("error", response.get("message", "Unknown error"))
            raise Exception(f"API error: {error}")
        
        notes = []
        for melody in response.get("melodies", []):
            for n in melody.get("notes", []):
                notes.append(MidiNote(
                    note_number=n.get("pitch", 60),
                    start_beat=n.get("start_time", 0.0),
                    length_beats=n.get("duration", 0.5),
                    velocity=n.get("velocity", 100),
                    channel=n.get("channel", 0) + 1  # Convert 0-based to 1-based
                ))
        
        return notes
    
    def build_request(self, context: PluginContext) -> Dict[str, Any]:
        """
        Build request from context parameters.
        Override this or build manually in generate().
        """
        params = {}
        for ctrl in self.controls:
            params[ctrl.id] = context.get_param(ctrl.id, ctrl.default)
        
        if self.has_input:
            params["prompt"] = context.get_param("_input", "")
        
        return params
