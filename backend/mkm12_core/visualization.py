"""
MKM12 Visualization Module

This module provides visualization capabilities for MKM12 analysis results,
including interactive charts, force gauges, and persona activation displays.
"""

from __future__ import annotations
from typing import List, Sequence, Dict, Optional, Tuple
import math
import json
import os
from datetime import datetime

from .model import MKM12Model
from .simulation import SimulationConfig


class MKM12Visualizer:
    """
    Visualization engine for MKM12 analysis results.
    
    This class provides methods to create interactive charts, force gauges,
    and persona displays for MKM12 theory analysis.
    """
    
    # Color scheme for MKM12 forces and modes
    FORCE_COLORS = {
        "K": "#2E86AB",  # Solar force (Blue)
        "L": "#A23B72",  # Lesser Yang force (Purple)
        "S": "#F18F01",  # Lesser Yin force (Orange)
        "M": "#3B7A57",  # Greater Yin force (Green)
    }
    
    MODE_COLORS = {
        "A1": "#2E86AB",  # Solar mode (Blue)
        "A2": "#A23B72",  # Yang mode (Purple)
        "A3": "#F18F01",  # Yin mode (Orange)
    }
    
    def __init__(self, model: MKM12Model):
        """
        Initialize visualizer with MKM12 model.
        
        Args:
            model: MKM12Model instance for visualization
        """
        self.model = model
        self.output_dir = "outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_force_gauge(self, forces: Sequence[float], 
                          save_path: Optional[str] = None) -> str:
        """
        Create a force gauge visualization for the 4 MKM12 forces.
        
        Args:
            forces: Force vector [K, L, S, M]
            save_path: Optional path to save the visualization
            
        Returns:
            HTML string or file path of the visualization
        """
        try:
            from plotly.graph_objects import Figure, Indicator
            from plotly.subplots import make_subplots
            
            # Create subplot for 4 force gauges
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=self.model.get_force_names(),
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}]]
            )
            
            # Add gauge for each force
            force_names = ["K", "L", "S", "M"]
            positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
            
            for i, (force_name, force_value, pos) in enumerate(zip(force_names, forces, positions)):
                fig.add_trace(
                    Indicator(
                        mode="gauge+number+delta",
                        value=force_value,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': force_name},
                        delta={'reference': 0.5},
                        gauge={
                            'axis': {'range': [None, 1.0]},
                            'bar': {'color': self.FORCE_COLORS[force_name]},
                            'steps': [
                                {'range': [0, 0.3], 'color': "lightgray"},
                                {'range': [0.3, 0.7], 'color': "gray"},
                                {'range': [0.7, 1.0], 'color': "darkgray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 0.9
                            }
                        }
                    ),
                    row=pos[0], col=pos[1]
                )
            
            # Update layout
            fig.update_layout(
                title="MKM12 Forces Analysis",
                height=600,
                width=800,
                showlegend=False
            )
            
            # Save or return
            if save_path:
                if not save_path.endswith('.html'):
                    save_path += '.html'
                fig.write_html(save_path)
                return save_path
            else:
                return fig.to_html(include_plotlyjs='cdn')
                
        except ImportError:
            # Fallback to text-based visualization
            return self._create_text_force_gauge(forces, save_path)
    
    def create_persona_chart(self, personas: Sequence[float],
                            save_path: Optional[str] = None) -> str:
        """
        Create a persona activation chart for the 3 MKM12 modes.
        
        Args:
            personas: Persona activation vector [A1, A2, A3]
            save_path: Optional path to save the visualization
            
        Returns:
            HTML string or file path of the visualization
        """
        try:
            from plotly.graph_objects import Figure, Bar
            
            # Create bar chart
            fig = Figure(data=[
                Bar(
                    x=self.model.get_mode_names(),
                    y=personas,
                    marker_color=[self.MODE_COLORS[f"A{i+1}"] for i in range(3)]
                )
            ])
            
            # Update layout
            fig.update_layout(
                title="MKM12 Persona Activation",
                xaxis_title="Persona Modes",
                yaxis_title="Activation Level",
                yaxis_range=[0, 1],
                height=400,
                width=600
            )
            
            # Save or return
            if save_path:
                if not save_path.endswith('.html'):
                    save_path += '.html'
                fig.write_html(save_path)
                return save_path
            else:
                return fig.to_html(include_plotlyjs='cdn')
                
        except ImportError:
            # Fallback to text-based visualization
            return self._create_text_persona_chart(personas, save_path)
    
    def create_dynamics_plot(self, simulation_result: Dict[str, List],
                            save_path: Optional[str] = None) -> str:
        """
        Create a dynamics plot showing forces and modes over time.
        
        Args:
            simulation_result: Result from MKM12Simulator.simulate()
            save_path: Optional path to save the visualization
            
        Returns:
            HTML string or file path of the visualization
        """
        try:
            from plotly.subplots import make_subplots
            from plotly.graph_objects import Scatter
            
            t = simulation_result['t']
            x = simulation_result['x']
            u = simulation_result['u']
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=("MKM12 Forces", "MKM12 Modes")
            )
            
            # Plot forces
            force_names = ["K", "L", "S", "M"]
            for i, force_name in enumerate(force_names):
                fig.add_trace(
                    Scatter(
                        x=t,
                        y=[row[i] for row in x],
                        name=force_name,
                        line=dict(color=self.FORCE_COLORS[force_name])
                    ),
                    row=1, col=1
                )
            
            # Plot modes
            mode_names = ["A1", "A2", "A3"]
            for i, mode_name in enumerate(mode_names):
                fig.add_trace(
                    Scatter(
                        x=t,
                        y=[row[i] for row in u],
                        name=mode_name,
                        line=dict(color=self.MODE_COLORS[mode_name], dash="dash")
                    ),
                    row=2, col=1
                )
            
            # Update layout
            fig.update_layout(
                title="MKM12 Dynamics Over Time",
                height=600,
                width=900,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_yaxes(title_text="Forces", row=1, col=1)
            fig.update_yaxes(title_text="Modes", row=2, col=1)
            
            # Save or return
            if save_path:
                if not save_path.endswith('.html'):
                    save_path += '.html'
                fig.write_html(save_path)
                return save_path
            else:
                return fig.to_html(include_plotlyjs='cdn')
                
        except ImportError:
            # Fallback to CSV export
            return self._export_simulation_csv(simulation_result, save_path)
    
    def create_digital_fingerprint_visualization(self, 
                                               forces: Sequence[float],
                                               personas: Sequence[float],
                                               save_path: Optional[str] = None) -> str:
        """
        Create a digital fingerprint visualization based on MKM12 data.
        
        Args:
            forces: Force vector [K, L, S, M]
            personas: Persona activation vector [A1, A2, A3]
            save_path: Optional path to save the visualization
            
        Returns:
            HTML string or file path of the visualization
        """
        try:
            from plotly.graph_objects import Figure, Scatter, Layout
            
            # Create a unique pattern based on forces and personas
            # This is a simplified version - can be enhanced with more complex algorithms
            t = list(range(100))
            pattern = []
            
            for i in t:
                # Create a complex pattern using forces and personas
                k_factor = forces[0] * math.sin(i * 0.1)
                l_factor = forces[1] * math.cos(i * 0.15)
                s_factor = forces[2] * math.sin(i * 0.2)
                m_factor = forces[3] * math.cos(i * 0.25)
                
                # Combine with persona influences
                a1_influence = personas[0] * math.sin(i * 0.05)
                a2_influence = personas[1] * math.cos(i * 0.08)
                a3_influence = personas[2] * math.sin(i * 0.12)
                
                # Create unique fingerprint value
                fingerprint_value = (
                    k_factor + l_factor + s_factor + m_factor +
                    a1_influence + a2_influence + a3_influence
                ) / 7.0
                
                pattern.append(fingerprint_value)
            
            # Create the visualization
            fig = Figure(data=[
                Scatter(
                    x=t,
                    y=pattern,
                    mode='lines',
                    name='Digital Fingerprint',
                    line=dict(color='#FF6B6B', width=2)
                )
            ])
            
            # Update layout
            fig.update_layout(
                title="MKM12 Digital Fingerprint",
                xaxis_title="Pattern Index",
                yaxis_title="Fingerprint Value",
                height=400,
                width=700,
                showlegend=True
            )
            
            # Save or return
            if save_path:
                if not save_path.endswith('.html'):
                    save_path += '.html'
                fig.write_html(save_path)
                return save_path
            else:
                return fig.to_html(include_plotlyjs='cdn')
                
        except ImportError:
            # Fallback to text-based visualization
            return self._create_text_fingerprint(forces, personas, save_path)
    
    def _create_text_force_gauge(self, forces: Sequence[float], 
                                save_path: Optional[str] = None) -> str:
        """Fallback text-based force gauge visualization."""
        force_names = ["K (Solar)", "L (Lesser Yang)", "S (Lesser Yin)", "M (Greater Yin)"]
        
        output = "MKM12 Forces Analysis\n"
        output += "=" * 30 + "\n\n"
        
        for i, (name, value) in enumerate(zip(force_names, forces)):
            bar_length = int(value * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            output += f"{name}: {value:.3f}\n{bar}\n\n"
        
        if save_path:
            if not save_path.endswith('.txt'):
                save_path += '.txt'
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(output)
            return save_path
        
        return output
    
    def _create_text_persona_chart(self, personas: Sequence[float],
                                  save_path: Optional[str] = None) -> str:
        """Fallback text-based persona chart visualization."""
        mode_names = ["A1 (Solar Mode)", "A2 (Yang Mode)", "A3 (Yin Mode)"]
        
        output = "MKM12 Persona Activation\n"
        output += "=" * 30 + "\n\n"
        
        for name, value in zip(mode_names, personas):
            bar_length = int(value * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            output += f"{name}: {value:.3f}\n{bar}\n\n"
        
        if save_path:
            if not save_path.endswith('.txt'):
                save_path += '.txt'
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(output)
            return save_path
        
        return output
    
    def _export_simulation_csv(self, simulation_result: Dict[str, List],
                              save_path: Optional[str] = None) -> str:
        """Export simulation results to CSV format."""
        if not save_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(self.output_dir, f"mkm12_simulation_{timestamp}.csv")
        
        if not save_path.endswith('.csv'):
            save_path += '.csv'
        
        t = simulation_result['t']
        x = simulation_result['x']
        u = simulation_result['u']
        
        with open(save_path, 'w', newline='', encoding='utf-8') as f:
            f.write("Time,K,L,S,M,A1,A2,A3\n")
            for i in range(len(t)):
                f.write(f"{t[i]:.3f},{x[i][0]:.6f},{x[i][1]:.6f},{x[i][2]:.6f},{x[i][3]:.6f},"
                       f"{u[i][0]:.6f},{u[i][1]:.6f},{u[i][2]:.6f}\n")
        
        return save_path
    
    def _create_text_fingerprint(self, forces: Sequence[float],
                                personas: Sequence[float],
                                save_path: Optional[str] = None) -> str:
        """Fallback text-based digital fingerprint visualization."""
        output = "MKM12 Digital Fingerprint\n"
        output += "=" * 30 + "\n\n"
        
        output += "Force Values:\n"
        force_names = ["K", "L", "S", "M"]
        for name, value in zip(force_names, forces):
            output += f"  {name}: {value:.6f}\n"
        
        output += "\nPersona Activations:\n"
        mode_names = ["A1", "A2", "A3"]
        for name, value in zip(mode_names, personas):
            output += f"  {name}: {value:.6f}\n"
        
        output += "\nFingerprint Hash: "
        # Create a simple hash-like representation
        combined = sum(forces) + sum(personas)
        hash_value = int(combined * 1000000) % 1000000
        output += f"{hash_value:06d}\n"
        
        if save_path:
            if not save_path.endswith('.txt'):
                save_path += '.txt'
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(output)
            return save_path
        
        return output


# Convenience functions for quick visualization
def visualize_forces(model: MKM12Model, forces: Sequence[float], 
                    save_path: Optional[str] = None) -> str:
    """Quick function to visualize MKM12 forces."""
    visualizer = MKM12Visualizer(model)
    return visualizer.create_force_gauge(forces, save_path)


def visualize_personas(model: MKM12Model, personas: Sequence[float],
                      save_path: Optional[str] = None) -> str:
    """Quick function to visualize MKM12 personas."""
    visualizer = MKM12Visualizer(model)
    return visualizer.create_persona_chart(personas, save_path)


def visualize_dynamics(model: MKM12Model, simulation_result: Dict[str, List],
                      save_path: Optional[str] = None) -> str:
    """Quick function to visualize MKM12 dynamics."""
    visualizer = MKM12Visualizer(model)
    return visualizer.create_dynamics_plot(simulation_result, save_path)
