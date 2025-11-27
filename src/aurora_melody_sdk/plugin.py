"""
Base plugin class for Aurora Melody plugins.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from enum import Enum

from aurora_melody_sdk.note import MidiNote
from aurora_melody_sdk.context import PluginContext


class ParameterType(Enum):
    """Types of plugin parameters."""
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"
    CHOICE = "choice"


@dataclass
class PluginParameter:
    """
    Definition of a plugin parameter for the UI.
    
    Use this to define parameters that users can adjust in Aurora Melody.
    
    Attributes:
        id: Unique identifier for the parameter
        name: Display name shown in UI
        param_type: Type of parameter (int, float, bool, choice, string)
        default: Default value
        min_value: Minimum value (for int/float)
        max_value: Maximum value (for int/float)
        step: Step increment (for int/float)
        choices: List of choices (for choice type)
        description: Optional description/tooltip
    
    Example::
    
        parameters = [
            PluginParameter(
                id="num_notes",
                name="Number of Notes",
                param_type=ParameterType.INT,
                default=8,
                min_value=1,
                max_value=64
            ),
            PluginParameter(
                id="scale",
                name="Scale",
                param_type=ParameterType.CHOICE,
                default="Major",
                choices=["Major", "Minor", "Pentatonic"]
            ),
        ]
    """
    
    id: str
    name: str
    param_type: ParameterType = ParameterType.INT
    default: Any = 0
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    choices: List[str] = field(default_factory=list)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "id": self.id,
            "name": self.name,
            "type": self.param_type.value,
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
        if self.description:
            result["description"] = self.description
        
        return result


class AuroraPlugin(ABC):
    """
    Base class for Aurora Melody plugins.
    
    To create a plugin, subclass AuroraPlugin and implement the generate() method.
    
    Required Attributes:
        name: Display name of the plugin
        author: Plugin author name
        version: Version string (e.g., "1.0.0")
    
    Optional Attributes:
        description: Brief description of what the plugin does
        parameters: List of PluginParameter for UI controls
    
    Example::
    
        from aurora_melody_sdk import AuroraPlugin, MidiNote, Scale
        
        class MyMelodyGenerator(AuroraPlugin):
            name = "My Melody Generator"
            author = "Your Name"
            version = "1.0.0"
            description = "Generates random melodies in a chosen scale"
            
            parameters = [
                PluginParameter("num_notes", "Notes", ParameterType.INT, 8, 1, 32),
                PluginParameter("scale", "Scale", ParameterType.CHOICE, "Major",
                               choices=["Major", "Minor", "Blues"]),
            ]
            
            def generate(self, context):
                notes = []
                num = context.get_int_param("num_notes", 8)
                scale_name = context.get_str_param("scale", "Major")
                
                scale = getattr(Scale, scale_name.upper(), Scale.MAJOR)
                scale_notes = Scale.get_notes(60, scale, octaves=2)
                
                import random
                start = context.playhead_position
                for i in range(num):
                    notes.append(MidiNote(
                        note_number=random.choice(scale_notes),
                        start_beat=start + i * 0.5,
                        length_beats=0.5,
                        velocity=random.randint(70, 100)
                    ))
                
                return notes
    """
    
    # Required metadata (override in subclass)
    name: str = "Unnamed Plugin"
    author: str = "Unknown"
    version: str = "1.0.0"
    
    # Optional metadata
    description: str = ""
    parameters: List[Union[PluginParameter, Dict[str, Any]]] = []
    
    def __init__(self):
        """Initialize the plugin. Called once when loaded."""
        pass
    
    def on_load(self) -> None:
        """
        Called when the plugin is loaded into Aurora Melody.
        
        Override to perform initialization tasks.
        """
        pass
    
    def on_unload(self) -> None:
        """
        Called when the plugin is unloaded from Aurora Melody.
        
        Override to perform cleanup tasks.
        """
        pass
    
    def on_parameter_changed(self, param_id: str, value: Any) -> None:
        """
        Called when a parameter value changes.
        
        Args:
            param_id: ID of the changed parameter
            value: New value
        """
        pass
    
    @abstractmethod
    def generate(self, context: Union[PluginContext, Dict[str, Any]]) -> List[MidiNote]:
        """
        Generate MIDI notes based on the current context.
        
        This is the main method you must implement!
        
        Args:
            context: PluginContext or dictionary containing:
                - notes: Existing notes in piano roll
                - selectedNoteIds: IDs of selected notes
                - tempoBPM: Current tempo
                - playheadPosition: Current playhead position
                - parameters: User parameter values
        
        Returns:
            List of MidiNote objects to add to the piano roll
        
        Example::
        
            def generate(self, context):
                notes = []
                
                # Get parameters
                if isinstance(context, dict):
                    ctx = PluginContext.from_dict(context)
                else:
                    ctx = context
                
                # Generate notes
                for i in range(8):
                    notes.append(MidiNote(60 + i, i * 0.5, 0.5, 100))
                
                return notes
        """
        pass
    
    def get_parameters_dict(self) -> List[Dict[str, Any]]:
        """Get parameters as list of dictionaries."""
        result = []
        for param in self.parameters:
            if isinstance(param, PluginParameter):
                result.append(param.to_dict())
            elif isinstance(param, dict):
                result.append(param)
        return result
    
    def _normalize_context(self, context: Union[PluginContext, Dict[str, Any]]) -> PluginContext:
        """Convert context to PluginContext if needed."""
        if isinstance(context, PluginContext):
            return context
        return PluginContext.from_dict(context)

