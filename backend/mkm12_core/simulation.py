"""
MKM12 Simulation Engine

This module provides simulation capabilities for MKM12 dynamics
using numerical integration methods and configurable parameters.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, Sequence, List, Optional, Tuple
import math
import random
import time

from .model import MKM12Model


@dataclass
class SimulationConfig:
    """
    Configuration for MKM12 simulation.
    
    Attributes:
        t0: Start time (default: 0.0)
        t1: End time (default: 50.0)
        dt: Time step (default: 0.05)
        temperature: Temperature for persona activation (default: 1.0)
        noise_std: Standard deviation of noise (default: 0.0)
        max_steps: Maximum number of simulation steps (default: 10000)
    """
    t0: float = 0.0
    t1: float = 50.0
    dt: float = 0.05
    temperature: float = 1.0
    noise_std: float = 0.0
    max_steps: int = 10000


class MKM12Simulator:
    """
    Simulation engine for MKM12 dynamics.
    
    This class provides methods to simulate MKM12 model behavior
    over time using various numerical integration methods.
    """
    
    def __init__(self, model: MKM12Model):
        """
        Initialize simulator with MKM12 model.
        
        Args:
            model: MKM12Model instance to simulate
        """
        self.model = model
        self.simulation_history: List[Dict] = []
    
    def _vec_add(self, a: Sequence[float], b: Sequence[float]) -> List[float]:
        """Vector addition."""
        return [ai + bi for ai, bi in zip(a, b)]
    
    def _vec_scale(self, v: Sequence[float], s: float) -> List[float]:
        """Vector scaling."""
        return [s * vi for vi in v]
    
    def rk4_step(self, f: Callable[[float, Sequence[float]], Sequence[float]], 
                 t: float, x: Sequence[float], h: float) -> List[float]:
        """
        Perform one step of 4th order Runge-Kutta integration.
        
        Args:
            f: Function that returns dx/dt
            t: Current time
            x: Current state
            h: Time step
            
        Returns:
            Next state after time step h
        """
        k1 = list(f(t, x))
        k2 = list(f(t + 0.5 * h, self._vec_add(x, self._vec_scale(k1, 0.5 * h))))
        k3 = list(f(t + 0.5 * h, self._vec_add(x, self._vec_scale(k2, 0.5 * h))))
        k4 = list(f(t + h, self._vec_add(x, self._vec_scale(k3, h))))
        
        # RK4 formula: x(t+h) = x(t) + (h/6) * (k1 + 2*k2 + 2*k3 + k4)
        incr = self._vec_scale(
            self._vec_add(
                self._vec_add(k1, self._vec_scale(k2, 2.0)),
                self._vec_add(self._vec_scale(k3, 2.0), k4)
            ), 
            h / 6.0
        )
        
        return self._vec_add(list(x), incr)
    
    def simulate(self, 
                x0: Optional[Sequence[float]] = None,
                mode_schedule: Optional[Callable[[float, Sequence[float]], Sequence[float]]] = None,
                cfg: SimulationConfig = SimulationConfig()) -> Dict[str, List]:
        """
        Simulate MKM12 dynamics over time.
        
        Args:
            x0: Initial state vector [K, L, S, M] (default: [0.5, 0.6, 0.2, 0.1])
            mode_schedule: Function that returns mode vector u(t, x) (default: auto)
            cfg: Simulation configuration
            
        Returns:
            Dictionary containing simulation results:
            - 't': List of time points
            - 'x': List of state vectors [K, L, S, M]
            - 'u': List of mode vectors [A1, A2, A3]
            - 'metadata': Simulation metadata
        """
        # Set initial state
        if x0 is None:
            x: List[float] = [0.5, 0.6, 0.2, 0.1]  # Default initial state
        else:
            x = list(x0)
        
        t = cfg.t0
        n_steps = min(int(math.ceil((cfg.t1 - cfg.t0) / cfg.dt)), cfg.max_steps)
        
        # Initialize result arrays
        times: List[float] = [0.0] * (n_steps + 1)
        xs: List[List[float]] = [[0.0, 0.0, 0.0, 0.0] for _ in range(n_steps + 1)]
        us: List[List[float]] = [[0.0, 0.0, 0.0] for _ in range(n_steps + 1)]
        
        def input_u(time: float, state: Sequence[float]) -> List[float]:
            """Calculate mode input vector."""
            if mode_schedule is not None:
                u = list(mode_schedule(time, state))
            else:
                u = list(self.model.persona_activation(state, temperature=cfg.temperature))
            
            # Add noise if specified
            if cfg.noise_std > 0:
                u = [ui + random.gauss(0.0, cfg.noise_std) for ui in u]
                # Re-normalize as probabilities
                u = [max(0.0, ui) for ui in u]
                s = sum(u)
                u = [ui / s for ui in u] if s > 1e-12 else [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
            
            return u
        
        # Store initial conditions
        times[0] = t
        xs[0] = list(x)
        us[0] = input_u(t, x)
        
        # Define the system function for RK4
        def f(time: float, state: Sequence[float]) -> List[float]:
            u = input_u(time, state)
            return list(self.model.drift(time, state, u))
        
        # Main simulation loop
        start_time = time.time()
        for i in range(1, n_steps + 1):
            x = self.rk4_step(f, t, x, cfg.dt)
            t = cfg.t0 + i * cfg.dt
            
            times[i] = t
            xs[i] = list(x)
            us[i] = input_u(t, x)
        
        simulation_time = time.time() - start_time
        
        # Prepare metadata
        metadata = {
            "simulation_time": simulation_time,
            "n_steps": n_steps,
            "dt": cfg.dt,
            "temperature": cfg.temperature,
            "noise_std": cfg.noise_std,
            "model_params": {
                "alpha": self.model.params.alpha,
                "beta": self.model.params.beta,
                "gamma": self.model.params.gamma
            }
        }
        
        # Store simulation in history
        result = {"t": times, "x": xs, "u": us, "metadata": metadata}
        self.simulation_history.append(result)
        
        return result
    
    def simulate_scenario(self, 
                         scenario_name: str,
                         x0: Sequence[float],
                         duration: float = 30.0,
                         **kwargs) -> Dict[str, List]:
        """
        Simulate a specific scenario with predefined parameters.
        
        Args:
            scenario_name: Name of the scenario
            x0: Initial state vector
            duration: Simulation duration
            **kwargs: Additional simulation parameters
            
        Returns:
            Simulation results
        """
        cfg = SimulationConfig(
            t0=0.0,
            t1=duration,
            dt=kwargs.get('dt', 0.05),
            temperature=kwargs.get('temperature', 1.0),
            noise_std=kwargs.get('noise_std', 0.0)
        )
        
        result = self.simulate(x0, cfg=cfg)
        result['scenario'] = scenario_name
        result['initial_state'] = x0
        
        return result
    
    def get_simulation_history(self) -> List[Dict]:
        """Get list of all simulations performed."""
        return self.simulation_history.copy()
    
    def clear_history(self) -> None:
        """Clear simulation history."""
        self.simulation_history.clear()
    
    def analyze_trajectory(self, result: Dict[str, List]) -> Dict[str, float]:
        """
        Analyze simulation trajectory for key metrics.
        
        Args:
            result: Simulation result from simulate() method
            
        Returns:
            Dictionary of analysis metrics
        """
        t = result['t']
        x = result['x']
        u = result['u']
        
        # Calculate average forces over time
        avg_forces = {
            'K': sum(row[0] for row in x) / len(x),
            'L': sum(row[1] for row in x) / len(x),
            'S': sum(row[2] for row in x) / len(x),
            'M': sum(row[3] for row in x) / len(x)
        }
        
        # Calculate average modes over time
        avg_modes = {
            'A1': sum(row[0] for row in u) / len(u),
            'A2': sum(row[1] for row in u) / len(u),
            'A3': sum(row[2] for row in u) / len(u)
        }
        
        # Calculate stability metrics
        final_state = x[-1]
        is_stable, stability_score = self.model.analyze_stability(final_state)
        
        # Calculate energy metrics
        total_energy = sum(sum(f**2 for f in row) for row in x) / len(x)
        
        return {
            'avg_forces': avg_forces,
            'avg_modes': avg_modes,
            'final_state': final_state,
            'is_stable': is_stable,
            'stability_score': stability_score,
            'total_energy': total_energy,
            'duration': t[-1] - t[0],
            'n_steps': len(t)
        }


# Convenience function for quick simulation
def simulate_mkm12(model: MKM12Model,
                   x0: Optional[Sequence[float]] = None,
                   mode_schedule: Optional[Callable[[float, Sequence[float]], Sequence[float]]] = None,
                   cfg: SimulationConfig = SimulationConfig()) -> Dict[str, List]:
    """
    Convenience function to simulate MKM12 dynamics.
    
    Args:
        model: MKM12Model instance
        x0: Initial state vector
        mode_schedule: Mode schedule function
        cfg: Simulation configuration
        
    Returns:
        Simulation results
    """
    simulator = MKM12Simulator(model)
    return simulator.simulate(x0, mode_schedule, cfg)
