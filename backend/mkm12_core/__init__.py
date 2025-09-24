"""
MKM12 Core Library for eno-health-helper

This module provides the core MKM12 mathematical theory model
for analyzing human behavioral patterns through 4 forces and 3 modes.

Classes:
    MKM12Model: Core mathematical model for MKM12 dynamics
    MKM12Params: Configuration parameters for the model
    MKM12Simulator: Simulation engine for MKM12 dynamics
    MKM12Visualizer: Visualization tools for MKM12 analysis

Functions:
    analyze_persona: Analyze persona activation from force data
    simulate_dynamics: Simulate MKM12 dynamics over time
    generate_digital_fingerprint: Create digital fingerprint from MKM12 data
"""

from .model import MKM12Model, MKM12Params
from .simulation import MKM12Simulator, SimulationConfig
from .visualization import MKM12Visualizer
from .utils import analyze_persona, generate_digital_fingerprint

__version__ = "1.0.0"
__author__ = "MKM Lab"
__all__ = [
    "MKM12Model",
    "MKM12Params", 
    "MKM12Simulator",
    "MKM12Visualizer",
    "analyze_persona",
    "generate_digital_fingerprint"
]
