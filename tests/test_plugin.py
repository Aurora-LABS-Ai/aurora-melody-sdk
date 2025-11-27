"""
Tests for plugin classes.
"""

import pytest
from aurora_melody_sdk import (
    AuroraPlugin, MidiNote, PluginContext, 
    PluginParameter, ParameterType
)


class TestPluginParameter:
    """Tests for PluginParameter."""
    
    def test_int_parameter(self):
        """Test integer parameter."""
        param = PluginParameter(
            id="num_notes",
            name="Number of Notes",
            param_type=ParameterType.INT,
            default=8,
            min_value=1,
            max_value=64
        )
        
        d = param.to_dict()
        assert d["id"] == "num_notes"
        assert d["name"] == "Number of Notes"
        assert d["type"] == "int"
        assert d["default"] == 8
        assert d["min"] == 1
        assert d["max"] == 64
    
    def test_float_parameter(self):
        """Test float parameter."""
        param = PluginParameter(
            id="length",
            name="Note Length",
            param_type=ParameterType.FLOAT,
            default=0.5,
            min_value=0.125,
            max_value=4.0,
            step=0.125
        )
        
        d = param.to_dict()
        assert d["type"] == "float"
        assert d["step"] == 0.125
    
    def test_choice_parameter(self):
        """Test choice parameter."""
        param = PluginParameter(
            id="scale",
            name="Scale",
            param_type=ParameterType.CHOICE,
            default="Major",
            choices=["Major", "Minor", "Blues"]
        )
        
        d = param.to_dict()
        assert d["type"] == "choice"
        assert d["choices"] == ["Major", "Minor", "Blues"]
    
    def test_bool_parameter(self):
        """Test boolean parameter."""
        param = PluginParameter(
            id="humanize",
            name="Humanize",
            param_type=ParameterType.BOOL,
            default=True
        )
        
        d = param.to_dict()
        assert d["type"] == "bool"
        assert d["default"] == True


class TestPluginContext:
    """Tests for PluginContext."""
    
    def test_from_dict(self):
        """Test creating context from dictionary."""
        data = {
            "tempoBPM": 120.0,
            "playheadPosition": 4.0,
            "notes": [
                {"noteNumber": 60, "startBeat": 0.0, "lengthBeats": 1.0, "velocity": 100}
            ],
            "selectedNoteIds": [1, 2],
            "parameters": {
                "num_notes": 16,
                "scale": "Minor"
            }
        }
        
        ctx = PluginContext.from_dict(data)
        
        assert ctx.tempo_bpm == 120.0
        assert ctx.playhead_position == 4.0
        assert len(ctx.notes) == 1
        assert ctx.notes[0].note_number == 60
    
    def test_get_int_param(self):
        """Test getting integer parameter."""
        ctx = PluginContext(parameters={"num_notes": 16})
        
        assert ctx.get_int_param("num_notes", 8) == 16
        assert ctx.get_int_param("missing", 8) == 8
    
    def test_get_float_param(self):
        """Test getting float parameter."""
        ctx = PluginContext(parameters={"length": 0.25})
        
        assert ctx.get_float_param("length", 0.5) == 0.25
        assert ctx.get_float_param("missing", 0.5) == 0.5
    
    def test_get_str_param(self):
        """Test getting string parameter."""
        ctx = PluginContext(parameters={"scale": "Blues"})
        
        assert ctx.get_str_param("scale", "Major") == "Blues"
        assert ctx.get_str_param("missing", "Major") == "Major"
    
    def test_get_bool_param(self):
        """Test getting boolean parameter."""
        ctx = PluginContext(parameters={"humanize": True})
        
        assert ctx.get_bool_param("humanize", False) == True
        assert ctx.get_bool_param("missing", False) == False


class TestAuroraPlugin:
    """Tests for AuroraPlugin base class."""
    
    def test_concrete_plugin(self):
        """Test creating a concrete plugin."""
        class TestPlugin(AuroraPlugin):
            name = "Test Plugin"
            author = "Test Author"
            version = "1.0.0"
            
            parameters = [
                PluginParameter("test", "Test", ParameterType.INT, 10, 0, 100)
            ]
            
            def generate(self, context):
                return [MidiNote(60, 0.0, 1.0, 100)]
        
        plugin = TestPlugin()
        assert plugin.name == "Test Plugin"
        assert plugin.author == "Test Author"
        
        notes = plugin.generate(PluginContext())
        assert len(notes) == 1
        assert notes[0].note_number == 60
    
    def test_get_parameters_dict(self):
        """Test getting parameters as dictionaries."""
        class TestPlugin(AuroraPlugin):
            name = "Test"
            author = "Test"
            version = "1.0.0"
            
            parameters = [
                PluginParameter("a", "A", ParameterType.INT, 1),
                PluginParameter("b", "B", ParameterType.FLOAT, 0.5),
            ]
            
            def generate(self, context):
                return []
        
        plugin = TestPlugin()
        params = plugin.get_parameters_dict()
        
        assert len(params) == 2
        assert params[0]["id"] == "a"
        assert params[1]["id"] == "b"

