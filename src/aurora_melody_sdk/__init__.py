"""
Aurora Melody SDK
==================

A Python SDK for creating melody generation plugins for Aurora Melody.

Quick Start::

    from aurora_melody_sdk import AuroraPlugin, MidiNote, Scale, Chord, ParameterType, PluginParameter

    class MyPlugin(AuroraPlugin):
        name = "My Plugin"
        author = "Your Name"
        version = "1.0.0"
        
        parameters = [
            PluginParameter("notes", "Number of Notes", ParameterType.INT, 8, 1, 32),
            PluginParameter("scale", "Scale", ParameterType.CHOICE, "Major",
                           choices=["Major", "Minor", "Blues", "Pentatonic"]),
        ]
        
        def generate(self, context):
            notes = []
            num = context.get_int_param("notes", 8)
            for i in range(num):
                notes.append(MidiNote(
                    note_number=60 + i,
                    start_beat=i * 0.5,
                    length_beats=0.5,
                    velocity=100
                ))
            return notes

For more information, visit: https://github.com/aurora-melody/sdk
"""

__version__ = "1.0.0"
__author__ = "Aurora Melody Labs"

# Core classes
from aurora_melody_sdk.note import MidiNote
from aurora_melody_sdk.context import PluginContext
from aurora_melody_sdk.plugin import AuroraPlugin, PluginParameter, ParameterType

# AI Service Plugin
from aurora_melody_sdk.ai_plugin import (
    AIServicePlugin, AIControl, AIControlType
)

# Music theory
from aurora_melody_sdk.theory import Scale, Chord, NoteName

# Utilities
from aurora_melody_sdk.utils import random_walk, arpeggiate, quantize_beat, humanize

__all__ = [
    # Version
    "__version__",
    # Core
    "AuroraPlugin",
    "MidiNote",
    "PluginContext",
    "PluginParameter",
    "ParameterType",
    # AI Service
    "AIServicePlugin",
    "AIControl",
    "AIControlType",
    # Theory
    "Scale",
    "Chord",
    "NoteName",
    # Utils
    "random_walk",
    "arpeggiate",
    "quantize_beat",
    "humanize",
]

