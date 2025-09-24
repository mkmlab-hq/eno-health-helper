"""
MKM12 API Endpoints

This module provides API endpoints for MKM12 theory analysis,
including persona analysis, digital fingerprint generation,
and personalized advice generation.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging

# Import MKM12 core library
try:
    from mkm12_core import (
        MKM12Model, MKM12Simulator, MKM12Visualizer,
        analyze_persona, generate_digital_fingerprint,
        create_mkm12_narrative, validate_mkm12_data
    )
    MKM12_AVAILABLE = True
except ImportError:
    MKM12_AVAILABLE = False
    logging.warning("MKM12 core library not available")

router = APIRouter(prefix="/mkm12", tags=["MKM12 Analysis"])


# Request/Response Models
class BiometricData(BaseModel):
    """Biometric data input for MKM12 analysis."""
    heart_rate: float = Field(..., ge=40, le=200, description="Heart rate (BPM)")
    heart_rate_variability: float = Field(..., ge=0, le=100, description="HRV (ms)")
    voice_amplitude: float = Field(..., ge=0, le=1, description="Voice amplitude (0-1)")
    voice_frequency: float = Field(..., ge=80, le=400, description="Voice frequency (Hz)")
    breathing_rate: float = Field(..., ge=8, le=30, description="Breathing rate (breaths/min)")
    stress_level: float = Field(..., ge=0, le=1, description="Stress level (0-1)")


class MKM12AnalysisRequest(BaseModel):
    """Request for MKM12 persona analysis."""
    biometric_data: BiometricData
    temperature: float = Field(default=1.0, ge=0.1, le=5.0, description="Analysis temperature")
    user_id: Optional[str] = Field(None, description="User identifier")


class MKM12AnalysisResponse(BaseModel):
    """Response from MKM12 persona analysis."""
    success: bool
    forces: Dict[str, float]
    personas: Dict[str, float]
    analysis: Dict[str, Any]
    digital_fingerprint: Optional[str] = None
    narrative: Optional[Dict[str, str]] = None
    error: Optional[str] = None


class DigitalFingerprintRequest(BaseModel):
    """Request for digital fingerprint generation."""
    forces: List[float] = Field(..., min_items=4, max_items=4, description="MKM12 forces [K, L, S, M]")
    personas: List[float] = Field(..., min_items=3, max_items=3, description="MKM12 personas [A1, A2, A3]")
    user_id: Optional[str] = Field(None, description="User identifier")


class DigitalFingerprintResponse(BaseModel):
    """Response from digital fingerprint generation."""
    success: bool
    fingerprint_hash: str
    pattern_data: List[float]
    metadata: Dict[str, Any]
    error: Optional[str] = None


class PersonalizedAdviceRequest(BaseModel):
    """Request for personalized advice generation."""
    forces: List[float] = Field(..., min_items=4, max_items=4, description="MKM12 forces [K, L, S, M]")
    personas: List[float] = Field(..., min_items=3, max_items=3, description="MKM12 personas [A1, A2, A3]")
    language: str = Field(default="ko", pattern="^(ko|en)$", description="Language for advice (ko/en)")
    context: Optional[str] = Field(None, description="Additional context for advice")


class PersonalizedAdviceResponse(BaseModel):
    """Response from personalized advice generation."""
    success: bool
    advice: Dict[str, Any]
    recommendations: List[str]
    overall_assessment: str
    error: Optional[str] = None


# Utility Functions
def _convert_biometric_to_forces(biometric: BiometricData) -> List[float]:
    """
    Convert biometric data to MKM12 forces.
    
    This is a simplified conversion algorithm that maps biometric
    measurements to the 4 MKM12 forces (K, L, S, M).
    """
    # Normalize biometric data to 0-1 range
    hr_norm = (biometric.heart_rate - 40) / (200 - 40)
    hrv_norm = biometric.heart_rate_variability / 100
    voice_amp_norm = biometric.voice_amplitude
    voice_freq_norm = (biometric.voice_frequency - 80) / (400 - 80)
    breathing_norm = (biometric.breathing_rate - 8) / (30 - 8)
    stress_norm = biometric.stress_level
    
    # Map to MKM12 forces using weighted combinations
    # K (Solar force): Energy and vitality
    K = (0.4 * hr_norm + 0.3 * voice_amp_norm + 0.3 * (1 - stress_norm))
    
    # L (Lesser Yang force): Stability and balance
    L = (0.5 * hrv_norm + 0.3 * breathing_norm + 0.2 * (1 - stress_norm))
    
    # S (Lesser Yin force): Emotional expression
    S = (0.4 * voice_freq_norm + 0.4 * voice_amp_norm + 0.2 * stress_norm)
    
    # M (Greater Yin force): Wisdom and reflection
    M = (0.5 * hrv_norm + 0.3 * (1 - stress_norm) + 0.2 * breathing_norm)
    
    # Ensure values are in [0, 1] range
    forces = [max(0.0, min(1.0, f)) for f in [K, L, S, M]]
    
    return forces


def _validate_mkm12_input(forces: List[float], personas: List[float]) -> bool:
    """Validate MKM12 input data."""
    if not MKM12_AVAILABLE:
        return False
    
    try:
        is_valid, errors = validate_mkm12_data(forces, personas)
        if not is_valid:
            logging.warning(f"MKM12 validation errors: {errors}")
        return is_valid
    except Exception as e:
        logging.error(f"MKM12 validation failed: {e}")
        return False


# API Endpoints
@router.post("/analyze/persona", response_model=MKM12AnalysisResponse)
async def analyze_persona_endpoint(request: MKM12AnalysisRequest):
    """
    Analyze biometric data and return MKM12 persona analysis.
    
    This endpoint converts biometric measurements to MKM12 forces,
    calculates persona activations, and provides comprehensive analysis.
    """
    if not MKM12_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="MKM12 analysis service is currently unavailable"
        )
    
    try:
        # Convert biometric data to MKM12 forces
        forces = _convert_biometric_to_forces(request.biometric_data)
        
        # Perform MKM12 analysis
        analysis_result = analyze_persona(forces, request.temperature)
        
        # Generate digital fingerprint
        fingerprint = generate_digital_fingerprint(
            forces, 
            list(analysis_result["personas"].values()),
            request.user_id
        )
        
        # Create narrative
        narrative = create_mkm12_narrative(analysis_result, "ko")
        
        return MKM12AnalysisResponse(
            success=True,
            forces=analysis_result["forces"],
            personas=analysis_result["personas"],
            analysis=analysis_result["analysis"],
            digital_fingerprint=fingerprint["pattern_hash"],
            narrative=narrative
        )
        
    except Exception as e:
        logging.error(f"Persona analysis failed: {e}")
        return MKM12AnalysisResponse(
            success=False,
            forces={},
            personas={},
            analysis={},
            error=f"Analysis failed: {str(e)}"
        )


@router.post("/generate/digital-fingerprint", response_model=DigitalFingerprintResponse)
async def generate_digital_fingerprint_endpoint(request: DigitalFingerprintRequest):
    """
    Generate a digital fingerprint based on MKM12 data.
    
    This endpoint creates a unique digital fingerprint that can be used
    for user identification, NFT generation, and personalized experiences.
    """
    if not MKM12_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="MKM12 fingerprint service is currently unavailable"
        )
    
    try:
        # Validate input data
        if not _validate_mkm12_input(request.forces, request.personas):
            raise ValueError("Invalid MKM12 data")
        
        # Generate digital fingerprint
        fingerprint = generate_digital_fingerprint(
            request.forces,
            request.personas,
            request.user_id
        )
        
        return DigitalFingerprintResponse(
            success=True,
            fingerprint_hash=fingerprint["pattern_hash"],
            pattern_data=fingerprint["pattern_data"],
            metadata=fingerprint["metadata"]
        )
        
    except Exception as e:
        logging.error(f"Digital fingerprint generation failed: {e}")
        return DigitalFingerprintResponse(
            success=False,
            fingerprint_hash="",
            pattern_data=[],
            metadata={},
            error=f"Generation failed: {str(e)}"
        )


@router.post("/get/personalized-advice", response_model=PersonalizedAdviceResponse)
async def get_personalized_advice_endpoint(request: PersonalizedAdviceRequest):
    """
    Generate personalized advice based on MKM12 analysis.
    
    This endpoint provides customized recommendations and insights
    based on the user's current MKM12 state.
    """
    if not MKM12_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="MKM12 advice service is currently unavailable"
        )
    
    try:
        # Validate input data
        if not _validate_mkm12_input(request.forces, request.personas):
            raise ValueError("Invalid MKM12 data")
        
        # Create narrative with advice
        narrative = create_mkm12_narrative(
            {
                "forces": {f"Force_{i}": v for i, v in enumerate(request.forces)},
                "personas": {f"A{i+1}": v for i, v in enumerate(request.personas)},
                "analysis": {"dominant_persona": "A1"}  # Placeholder
            },
            request.language
        )
        
        return PersonalizedAdviceResponse(
            success=True,
            advice=narrative,
            recommendations=narrative.get("recommendations", []),
            overall_assessment=narrative.get("overall", "")
        )
        
    except Exception as e:
        logging.error(f"Personalized advice generation failed: {e}")
        return PersonalizedAdviceResponse(
            success=False,
            advice={},
            recommendations=[],
            overall_assessment="",
            error=f"Advice generation failed: {str(e)}"
        )


@router.get("/status")
async def get_mkm12_status():
    """Get MKM12 service status and capabilities."""
    return {
        "service": "MKM12 Analysis API",
        "status": "available" if MKM12_AVAILABLE else "unavailable",
        "version": "1.0.0",
        "capabilities": [
            "Persona analysis from biometric data",
            "Digital fingerprint generation",
            "Personalized advice generation",
            "Multi-language support (Korean/English)"
        ],
        "mkm12_theory": {
            "forces": ["K (Solar)", "L (Lesser Yang)", "S (Lesser Yin)", "M (Greater Yin)"],
            "personas": ["A1 (Solar Mode)", "A2 (Yang Mode)", "A3 (Yin Mode)"],
            "mathematical_model": "Continuous-time nonlinear state-space dynamics"
        }
    }


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for MKM12 API."""
    return {
        "status": "healthy",
        "mkm12_available": MKM12_AVAILABLE,
        "timestamp": "2025-01-01T00:00:00Z"
    }
