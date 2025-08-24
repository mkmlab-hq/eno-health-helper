"""
MKM Lab eno-health-helper 통합 서비스 패키지

핵심 서비스들:
- AdvancedFusionAnalyzer: rPPG-음성 융합 분석
- EnhancedRPPGAnalyzer: 고급 rPPG 분석
- VoiceAnalyzer: 음성 분석
- HealthAnalyzer: 종합 건강 분석
"""

import importlib
from typing import Any

__all__ = [
	'AdvancedFusionAnalyzer',
	'EnhancedRPPGAnalyzer', 
	'VoiceAnalyzer',
	'HealthAnalyzer',
	'RPPGPipeline',
	'FaceMeshROIExtractor',
]

_module_map = {
	'AdvancedFusionAnalyzer': ('app.services.fusion_analyzer', 'AdvancedFusionAnalyzer'),
	'EnhancedRPPGAnalyzer': ('app.services.enhanced_rppg_analyzer', 'EnhancedRPPGAnalyzer'),
	'VoiceAnalyzer': ('app.services.voice_analyzer', 'VoiceAnalyzer'),
	'HealthAnalyzer': ('app.services.health_analyzer', 'HealthAnalyzer'),
	'RPPGPipeline': ('app.services.rppg_core.pipeline', 'RPPGPipeline'),
	'FaceMeshROIExtractor': ('app.services.rppg_core.face.mediapipe_face_roi', 'FaceMeshROIExtractor'),
}


def __getattr__(name: str) -> Any:
	if name in _module_map:
		module_name, attr = _module_map[name]
		mod = importlib.import_module(module_name)
		return getattr(mod, attr)
	raise AttributeError(f"module 'app.services' has no attribute '{name}'") 