"""
MKM12 Utility Functions

This module provides utility functions for MKM12 analysis,
including persona analysis, digital fingerprint generation,
and narrative creation based on MKM12 theory.
"""

from __future__ import annotations
from typing import List, Sequence, Dict, Optional, Tuple, Any
import math
import hashlib
import json
import random
from datetime import datetime

from .model import MKM12Model
from .simulation import MKM12Simulator, SimulationConfig


def analyze_persona(forces: Sequence[float], 
                   temperature: float = 1.0) -> Dict[str, Any]:
    """
    Analyze persona activation from MKM12 force data.
    
    Args:
        forces: Force vector [K, L, S, M]
        temperature: Temperature parameter for softmax
        
    Returns:
        Dictionary containing persona analysis results
    """
    # Create a temporary model for analysis
    model = MKM12Model.default()
    
    # Calculate persona activations
    personas = model.persona_activation(forces, temperature)
    
    # Determine dominant persona
    dominant_idx = personas.index(max(personas))
    dominant_persona = f"A{dominant_idx + 1}"
    
    # Calculate persona balance
    persona_balance = 1.0 - max(personas) + min(personas)
    
    # Analyze force distribution
    force_sum = sum(forces)
    force_balance = 1.0 - (max(forces) - min(forces)) / max(force_sum, 1e-6)
    
    # Determine overall state
    if force_balance > 0.7 and persona_balance > 0.6:
        overall_state = "Balanced"
    elif force_balance < 0.3 or persona_balance < 0.3:
        overall_state = "Unbalanced"
    else:
        overall_state = "Moderate"
    
    return {
        "forces": {
            "K": forces[0],
            "L": forces[1], 
            "S": forces[2],
            "M": forces[3]
        },
        "personas": {
            "A1": personas[0],
            "A2": personas[1],
            "A3": personas[2]
        },
        "analysis": {
            "dominant_persona": dominant_persona,
            "persona_balance": persona_balance,
            "force_balance": force_balance,
            "overall_state": overall_state,
            "temperature": temperature
        }
    }


def generate_digital_fingerprint(forces: Sequence[float],
                                personas: Sequence[float],
                                user_id: Optional[str] = None,
                                timestamp: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Generate a digital fingerprint based on MKM12 data.
    
    Args:
        forces: Force vector [K, L, S, M]
        personas: Persona activation vector [A1, A2, A3]
        user_id: Optional user identifier
        timestamp: Optional timestamp for the fingerprint
        
    Returns:
        Dictionary containing digital fingerprint data
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    # Create unique pattern based on forces and personas
    pattern_data = []
    for i in range(100):
        # Complex pattern generation using trigonometric functions
        k_factor = forces[0] * math.sin(i * 0.1)
        l_factor = forces[1] * math.cos(i * 0.15)
        s_factor = forces[2] * math.sin(i * 0.2)
        m_factor = forces[3] * math.cos(i * 0.25)
        
        # Persona influences
        a1_influence = personas[0] * math.sin(i * 0.05)
        a2_influence = personas[1] * math.cos(i * 0.08)
        a3_influence = personas[2] * math.sin(i * 0.12)
        
        # Combined fingerprint value
        fingerprint_value = (
            k_factor + l_factor + s_factor + m_factor +
            a1_influence + a2_influence + a3_influence
        ) / 7.0
        
        pattern_data.append(fingerprint_value)
    
    # Generate hash from pattern
    pattern_str = "".join([f"{x:.6f}" for x in pattern_data])
    pattern_hash = hashlib.sha256(pattern_str.encode()).hexdigest()
    
    # Create fingerprint metadata
    fingerprint = {
        "pattern_data": pattern_data,
        "pattern_hash": pattern_hash,
        "metadata": {
            "forces": list(forces),
            "personas": list(personas),
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            "version": "1.0"
        }
    }
    
    return fingerprint


def create_mkm12_narrative(analysis_result: Dict[str, Any],
                          language: str = "ko") -> Dict[str, str]:
    """
    Create narrative descriptions based on MKM12 analysis.
    
    Args:
        analysis_result: Result from analyze_persona()
        language: Language for narrative (ko/en)
        
    Returns:
        Dictionary containing narrative texts
    """
    if language == "ko":
        return _create_korean_narrative(analysis_result)
    else:
        return _create_english_narrative(analysis_result)


def _create_korean_narrative(analysis_result: Dict[str, Any]) -> Dict[str, str]:
    """Create Korean narrative based on MKM12 analysis."""
    
    forces = analysis_result["forces"]
    personas = analysis_result["personas"]
    analysis = analysis_result["analysis"]
    
    # Force descriptions
    force_descriptions = {
        "K": f"태양적 힘(K)이 {forces['K']:.1%}로 활성화되어 있습니다.",
        "L": f"소양적 힘(L)이 {forces['L']:.1%}로 활성화되어 있습니다.",
        "S": f"소음적 힘(S)이 {forces['S']:.1%}로 활성화되어 있습니다.",
        "M": f"태음적 힘(M)이 {forces['M']:.1%}로 활성화되어 있습니다."
    }
    
    # Persona descriptions
    persona_descriptions = {
        "A1": f"태양적 페르소나(A1)가 {personas['A1']:.1%}로 활성화되어 있습니다.",
        "A2": f"소양적 페르소나(A2)가 {personas['A2']:.1%}로 활성화되어 있습니다.",
        "A3": f"소음적 페르소나(A3)가 {personas['A3']:.1%}로 활성화되어 있습니다."
    }
    
    # Overall assessment
    if analysis["overall_state"] == "Balanced":
        overall_text = "전반적으로 균형 잡힌 상태입니다. 각 힘이 조화롭게 작용하고 있어 안정적인 컨디션을 유지하고 있습니다."
    elif analysis["overall_state"] == "Unbalanced":
        overall_text = "일부 힘이 과도하게 활성화되어 있습니다. 휴식과 균형 회복이 필요한 상태입니다."
    else:
        overall_text = "보통 수준의 균형을 유지하고 있습니다. 약간의 조정을 통해 더 나은 상태로 발전할 수 있습니다."
    
    # Recommendations
    recommendations = _generate_korean_recommendations(analysis_result)
    
    return {
        "title": "MKM12 분석 결과",
        "summary": f"현재 {analysis['dominant_persona']} 페르소나가 가장 활성화되어 있습니다.",
        "forces": force_descriptions,
        "personas": persona_descriptions,
        "overall": overall_text,
        "recommendations": recommendations
    }


def _create_english_narrative(analysis_result: Dict[str, Any]) -> Dict[str, str]:
    """Create English narrative based on MKM12 analysis."""
    
    forces = analysis_result["forces"]
    personas = analysis_result["personas"]
    analysis = analysis_result["analysis"]
    
    # Force descriptions
    force_descriptions = {
        "K": f"Solar force (K) is activated at {forces['K']:.1%}.",
        "L": f"Lesser Yang force (L) is activated at {forces['L']:.1%}.",
        "S": f"Lesser Yin force (S) is activated at {forces['S']:.1%}.",
        "M": f"Greater Yin force (M) is activated at {forces['M']:.1%}."
    }
    
    # Persona descriptions
    persona_descriptions = {
        "A1": f"Solar persona (A1) is activated at {personas['A1']:.1%}.",
        "A2": f"Yang persona (A2) is activated at {personas['A2']:.1%}.",
        "A3": f"Yin persona (A3) is activated at {personas['A3']:.1%}."
    }
    
    # Overall assessment
    if analysis["overall_state"] == "Balanced":
        overall_text = "Overall, you are in a balanced state. All forces are working harmoniously, maintaining stable condition."
    elif analysis["overall_state"] == "Unbalanced":
        overall_text = "Some forces are overly activated. Rest and balance restoration are needed."
    else:
        overall_text = "Maintaining moderate balance. You can improve your condition with slight adjustments."
    
    # Recommendations
    recommendations = _generate_english_recommendations(analysis_result)
    
    return {
        "title": "MKM12 Analysis Results",
        "summary": f"Currently, {analysis['dominant_persona']} persona is most activated.",
        "forces": force_descriptions,
        "personas": persona_descriptions,
        "overall": overall_text,
        "recommendations": recommendations
    }


def _generate_korean_recommendations(analysis_result: Dict[str, Any]) -> List[str]:
    """Generate Korean recommendations based on MKM12 analysis."""
    
    forces = analysis_result["forces"]
    personas = analysis_result["personas"]
    analysis = analysis_result["analysis"]
    
    recommendations = []
    
    # Force-based recommendations
    if forces["K"] > 0.7:
        recommendations.append("태양적 힘이 높습니다. 에너지 소모가 클 수 있으니 적절한 휴식을 취하세요.")
    elif forces["K"] < 0.3:
        recommendations.append("태양적 힘이 낮습니다. 활발한 활동을 통해 에너지를 활성화해보세요.")
    
    if forces["L"] > 0.7:
        recommendations.append("소양적 힘이 높습니다. 안정성과 균형을 유지하는 데 집중하세요.")
    elif forces["L"] < 0.3:
        recommendations.append("소양적 힘이 낮습니다. 체계적인 계획과 실행을 통해 안정성을 높여보세요.")
    
    if forces["S"] > 0.7:
        recommendations.append("소음적 힘이 높습니다. 감정적 균형을 위해 명상이나 요가를 시도해보세요.")
    elif forces["S"] < 0.3:
        recommendations.append("소음적 힘이 낮습니다. 감정 표현과 소통을 통해 내면의 균형을 찾아보세요.")
    
    if forces["M"] > 0.7:
        recommendations.append("태음적 힘이 높습니다. 깊은 사고와 성찰을 통해 지혜를 활용하세요.")
    elif forces["M"] < 0.3:
        recommendations.append("태음적 힘이 낮습니다. 독서나 학습을 통해 지혜를 축적해보세요.")
    
    # Persona-based recommendations
    dominant = analysis["dominant_persona"]
    if dominant == "A1":
        recommendations.append("태양적 페르소나가 활성화되어 있습니다. 리더십과 창의성을 발휘할 좋은 기회입니다.")
    elif dominant == "A2":
        recommendations.append("소양적 페르소나가 활성화되어 있습니다. 팀워크와 협력을 통해 목표를 달성해보세요.")
    elif dominant == "A3":
        recommendations.append("소음적 페르소나가 활성화되어 있습니다. 직관과 감성을 활용한 문제 해결이 효과적일 것입니다.")
    
    # Balance recommendations
    if analysis["overall_state"] == "Unbalanced":
        recommendations.append("전체적인 균형을 위해 명상, 운동, 충분한 휴식을 권장합니다.")
    
    return recommendations


def _generate_english_recommendations(analysis_result: Dict[str, Any]) -> List[str]:
    """Generate English recommendations based on MKM12 analysis."""
    
    forces = analysis_result["forces"]
    personas = analysis_result["personas"]
    analysis = analysis_result["analysis"]
    
    recommendations = []
    
    # Force-based recommendations
    if forces["K"] > 0.7:
        recommendations.append("Solar force is high. Energy consumption may be high, so take appropriate rest.")
    elif forces["K"] < 0.3:
        recommendations.append("Solar force is low. Try to activate energy through active activities.")
    
    if forces["L"] > 0.7:
        recommendations.append("Lesser Yang force is high. Focus on maintaining stability and balance.")
    elif forces["L"] < 0.3:
        recommendations.append("Lesser Yang force is low. Try to increase stability through systematic planning and execution.")
    
    if forces["S"] > 0.7:
        recommendations.append("Lesser Yin force is high. Try meditation or yoga for emotional balance.")
    elif forces["S"] < 0.3:
        recommendations.append("Lesser Yin force is low. Find inner balance through emotional expression and communication.")
    
    if forces["M"] > 0.7:
        recommendations.append("Greater Yin force is high. Utilize wisdom through deep thinking and reflection.")
    elif forces["M"] < 0.3:
        recommendations.append("Greater Yin force is low. Accumulate wisdom through reading and learning.")
    
    # Persona-based recommendations
    dominant = analysis["dominant_persona"]
    if dominant == "A1":
        recommendations.append("Solar persona is activated. It's a good opportunity to demonstrate leadership and creativity.")
    elif dominant == "A2":
        recommendations.append("Yang persona is activated. Achieve goals through teamwork and collaboration.")
    elif dominant == "A3":
        recommendations.append("Yin persona is activated. Problem-solving using intuition and emotion will be effective.")
    
    # Balance recommendations
    if analysis["overall_state"] == "Unbalanced":
        recommendations.append("For overall balance, meditation, exercise, and adequate rest are recommended.")
    
    return recommendations


def validate_mkm12_data(forces: Sequence[float],
                        personas: Sequence[float]) -> Tuple[bool, List[str]]:
    """
    Validate MKM12 data for consistency and reasonableness.
    
    Args:
        forces: Force vector [K, L, S, M]
        personas: Persona activation vector [A1, A2, A3]
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Check force values
    if len(forces) != 4:
        errors.append("Forces must have exactly 4 values")
    
    for i, force in enumerate(forces):
        if not isinstance(force, (int, float)):
            errors.append(f"Force {i} must be a number")
        elif force < 0 or force > 1:
            errors.append(f"Force {i} must be between 0 and 1")
    
    # Check persona values
    if len(personas) != 3:
        errors.append("Personas must have exactly 3 values")
    
    for i, persona in enumerate(personas):
        if not isinstance(persona, (int, float)):
            errors.append(f"Persona {i} must be a number")
        elif persona < 0 or persona > 1:
            errors.append(f"Persona {i} must be between 0 and 1")
    
    # Check persona sum (should be close to 1.0)
    persona_sum = sum(personas)
    if abs(persona_sum - 1.0) > 0.1:
        errors.append(f"Persona sum should be close to 1.0, got {persona_sum:.3f}")
    
    return len(errors) == 0, errors


def export_analysis_report(analysis_result: Dict[str, Any],
                          output_format: str = "json",
                          file_path: Optional[str] = None) -> str:
    """
    Export MKM12 analysis report in various formats.
    
    Args:
        analysis_result: Result from analyze_persona()
        output_format: Output format (json, txt, csv)
        file_path: Optional file path for saving
        
    Returns:
        File path or content string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if output_format == "json":
        return _export_json_report(analysis_result, file_path, timestamp)
    elif output_format == "txt":
        return _export_text_report(analysis_result, file_path, timestamp)
    elif output_format == "csv":
        return _export_csv_report(analysis_result, file_path, timestamp)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def _export_json_report(analysis_result: Dict[str, Any],
                        file_path: Optional[str],
                        timestamp: str) -> str:
    """Export analysis report as JSON."""
    if file_path is None:
        file_path = f"mkm12_analysis_{timestamp}.json"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    return file_path


def _export_text_report(analysis_result: Dict[str, Any],
                        file_path: Optional[str],
                        timestamp: str) -> str:
    """Export analysis report as text."""
    if file_path is None:
        file_path = f"mkm12_analysis_{timestamp}.txt"
    
    content = f"MKM12 Analysis Report\n"
    content += f"Generated: {timestamp}\n"
    content += "=" * 50 + "\n\n"
    
    # Forces
    content += "FORCES:\n"
    for force_name, value in analysis_result["forces"].items():
        content += f"  {force_name}: {value:.3f}\n"
    
    content += "\nPERSONAS:\n"
    for persona_name, value in analysis_result["personas"].items():
        content += f"  {persona_name}: {value:.3f}\n"
    
    content += "\nANALYSIS:\n"
    for key, value in analysis_result["analysis"].items():
        content += f"  {key}: {value}\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path


def _export_csv_report(analysis_result: Dict[str, Any],
                       file_path: Optional[str],
                       timestamp: str) -> str:
    """Export analysis report as CSV."""
    if file_path is None:
        file_path = f"mkm12_analysis_{timestamp}.csv"
    
    content = "Type,Name,Value\n"
    
    # Forces
    for force_name, value in analysis_result["forces"].items():
        content += f"Force,{force_name},{value:.6f}\n"
    
    # Personas
    for persona_name, value in analysis_result["personas"].items():
        content += f"Persona,{persona_name},{value:.6f}\n"
    
    # Analysis
    for key, value in analysis_result["analysis"].items():
        content += f"Analysis,{key},{value}\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path
