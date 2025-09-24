"""
MKM12 Core Mathematical Model

This module implements the core MKM12 mathematical theory model
for analyzing human behavioral patterns through 4 forces and 3 modes.

The model is based on continuous-time nonlinear state-space dynamics:
dx/dt = A x + B u + N(x, u) - γ x

where:
- x: 4-dimensional state vector [K, L, S, M] (4 forces)
- u: 3-dimensional mode vector [A1, A2, A3] (3 modes)
- A: 4x4 linear interaction matrix
- B: 4x3 control/coupling matrix
- N(x, u): nonlinear conversion and saturation terms
- γ: damping/regularization coefficient
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence, Tuple, Optional
import math
import numpy as np
from typing_extensions import TypeAlias

# Type aliases for better code readability
Vector4: TypeAlias = List[float]
Vector3: TypeAlias = List[float]
Matrix44: TypeAlias = List[List[float]]
Matrix43: TypeAlias = List[List[float]]


def matvec44(A: Matrix44, v: Sequence[float]) -> Vector4:
    """Matrix-vector multiplication for 4x4 matrix."""
    return [sum(aij * vj for aij, vj in zip(ai, v)) for ai in A]


def matvec43(B: Matrix43, v: Sequence[float]) -> Vector4:
    """Matrix-vector multiplication for 4x3 matrix."""
    return [sum(bij * vj for bij, vj in zip(bi, v)) for bi in B]


def vec_add4(a: Sequence[float], b: Sequence[float]) -> Vector4:
    """Vector addition for 4-dimensional vectors."""
    return [ai + bi for ai, bi in zip(a, b)]


def vec_scale4(v: Sequence[float], s: float) -> Vector4:
    """Vector scaling for 4-dimensional vectors."""
    return [s * vi for vi in v]


@dataclass
class MKM12Params:
    """
    Configuration parameters for MKM12 model.
    
    Attributes:
        A: 4x4 linear interaction matrix among forces K, L, S, M
        B: 4x3 control/coupling matrix for mode inputs
        alpha: Global nonlinearity strength (default: 0.8)
        beta: Cross-mode conversion gain (default: 0.4)
        gamma: Damping/regularization coefficient (default: 0.2)
    """
    A: Matrix44
    B: Matrix43
    alpha: float = 0.8
    beta: float = 0.4
    gamma: float = 0.2

    def __post_init__(self):
        """Validate matrix dimensions after initialization."""
        if len(self.A) != 4 or any(len(row) != 4 for row in self.A):
            raise ValueError("Matrix A must be 4x4")
        if len(self.B) != 4 or any(len(row) != 3 for row in self.B):
            raise ValueError("Matrix B must be 4x3")


class MKM12Model:
    """
    Continuous-time nonlinear state-space model for MKM12 dynamics.
    
    This model represents the interaction between 4 fundamental forces
    (K: Solar, L: Lesser Yang, S: Lesser Yin, M: Greater Yin)
    and 3 behavioral modes (A1, A2, A3).
    
    The dynamics are governed by:
    dx/dt = A x + B u + N(x, u) - γ x
    
    where N encodes nonlinear conversions, saturations, and stabilizers.
    """
    
    # Force names for better readability
    FORCE_NAMES = ["K (Solar)", "L (Lesser Yang)", "S (Lesser Yin)", "M (Greater Yin)"]
    MODE_NAMES = ["A1 (Solar Mode)", "A2 (Yang Mode)", "A3 (Yin Mode)"]
    
    def __init__(self, params: MKM12Params):
        """
        Initialize MKM12 model with parameters.
        
        Args:
            params: MKM12Params object containing model configuration
        """
        self.params = params
        self._validate()
    
    def _validate(self) -> None:
        """Validate model parameters."""
        if len(self.params.A) != 4 or any(len(row) != 4 for row in self.params.A):
            raise ValueError("Matrix A must be 4x4")
        if len(self.params.B) != 4 or any(len(row) != 3 for row in self.params.B):
            raise ValueError("Matrix B must be 4x3")
    
    @staticmethod
    def default() -> "MKM12Model":
        """
        Create MKM12 model with default parameters.
        
        Returns:
            MKM12Model instance with pre-configured parameters
        """
        # A encodes baseline couplings among K, L, S, M
        A: Matrix44 = [
            [-0.10,  0.15,  0.05,  0.00],  # dK/dt depends weakly on L and S
            [ 0.10, -0.20, -0.05,  0.00],  # dL/dt decays with leakage to S
            [ 0.00,  0.20, -0.15,  0.10],  # dS/dt fueled by L, decays to M
            [ 0.00,  0.00,  0.10, -0.12],  # dM/dt fueled by S
        ]
        
        # B maps modes [A1, A2, A3] into the forces
        B: Matrix43 = [
            [0.5,  0.1,  0.0],   # A1 energizes K mostly
            [0.1,  0.4,  0.1],   # A2 stabilizes L
            [0.0,  0.2,  0.5],   # A3 brightens S
            [0.0,  0.0,  0.3],   # A3 also lifts M
        ]
        
        return MKM12Model(MKM12Params(A=A, B=B))
    
    def nonlinear_terms(self, x: Sequence[float], u: Sequence[float]) -> Vector4:
        """
        Calculate nonlinear terms for the model.
        
        Args:
            x: State vector [K, L, S, M]
            u: Mode vector [A1, A2, A3]
            
        Returns:
            Nonlinear contribution vector [nK, nL, nS, nM]
        """
        K, L, S, M = x
        alpha = self.params.alpha
        beta = self.params.beta
        
        # Saturation of each force (resource boundedness)
        sat0 = math.tanh(x[0])
        sat1 = math.tanh(x[1])
        sat2 = math.tanh(x[2])
        
        # Conversion dynamics: K catalyzes L -> S and S -> M
        conv_L_to_S = alpha * math.tanh(K) * max(L, 0.0)
        conv_S_to_M = alpha * math.tanh(K) * max(S, 0.0)
        
        # Cross-mode shaping: modes reshape conversions
        mode_weight = 1.0 + beta * math.tanh(u[2] - u[1])  # A3 vs A2 balance
        conv_L_to_S *= mode_weight
        conv_S_to_M *= mode_weight
        
        # Assemble nonlinear vector field contributions
        nK = -0.05 * sat0 + 0.03 * (sat2 - sat1)
        nL = -conv_L_to_S
        nS = conv_L_to_S - conv_S_to_M
        nM = conv_S_to_M
        
        return [nK, nL, nS, nM]
    
    def drift(self, t: float, x: Sequence[float], u: Sequence[float]) -> Vector4:
        """
        Calculate the drift term for the model.
        
        Args:
            t: Current time
            x: State vector [K, L, S, M]
            u: Mode vector [A1, A2, A3]
            
        Returns:
            Drift vector dx/dt
        """
        A = self.params.A
        B = self.params.B
        gamma = self.params.gamma
        
        linear = vec_add4(matvec44(A, x), matvec43(B, u))
        nonlinear = self.nonlinear_terms(x, u)
        
        return vec_add4(linear, vec_add4(nonlinear, vec_scale4(x, -gamma)))
    
    def persona_activation(self, x: Sequence[float], temperature: float = 1.0) -> Vector3:
        """
        Map forces to mode activations as soft attention over [A1, A2, A3].
        
        Args:
            x: State vector [K, L, S, M]
            temperature: Temperature parameter for softmax (default: 1.0)
            
        Returns:
            Mode activation probabilities [A1, A2, A3]
        """
        t = max(1e-6, temperature)
        
        # Calculate logits for each mode
        logits = [
            1.2 * x[0],        # A1 ~ K (Solar force)
            1.0 * x[1],        # A2 ~ L (Lesser Yang force)
            0.7 * x[2] + 0.6 * x[3],  # A3 ~ S + M (Lesser + Greater Yin)
        ]
        
        # Apply temperature scaling
        logits = [lv / t for lv in logits]
        
        # Numerical stability for softmax
        m = max(logits)
        logits = [lv - m for lv in logits]
        
        # Calculate softmax probabilities
        expv = [math.exp(lv) for lv in logits]
        s = sum(expv) + 1e-12
        probs = [ev / s for ev in expv]
        
        return probs
    
    def get_force_names(self) -> List[str]:
        """Get human-readable names for the forces."""
        return self.FORCE_NAMES.copy()
    
    def get_mode_names(self) -> List[str]:
        """Get human-readable names for the modes."""
        return self.MODE_NAMES.copy()
    
    def analyze_stability(self, x: Sequence[float]) -> Tuple[bool, float]:
        """
        Analyze the stability of the current state.
        
        Args:
            x: State vector [K, L, S, M]
            
        Returns:
            Tuple of (is_stable, stability_score)
        """
        # Simple stability metric based on force magnitudes
        force_magnitudes = [abs(f) for f in x]
        max_force = max(force_magnitudes)
        avg_force = sum(force_magnitudes) / len(force_magnitudes)
        
        # Stability score: lower is more stable
        stability_score = max_force - avg_force
        
        # Consider stable if no force is too dominant
        is_stable = stability_score < 0.5
        
        return is_stable, stability_score
