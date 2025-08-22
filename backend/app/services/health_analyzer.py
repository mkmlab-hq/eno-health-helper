import sys
import os
from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime
import cv2
import librosa
from scipy import signal
from scipy.stats import linregress

# mkm-core-ai 경로 추가 시도
try:
    # 상대 경로로 mkm-core-ai 접근
    mkm_core_ai_path = os.path.join(os.path.dirname(__file__), '../../../mkm-core-ai')
    if os.path.exists(mkm_core_ai_path):
        sys.path.append(mkm_core_ai_path)
        MKM_CORE_AI_AVAILABLE = True
        print(f"✅ mkm-core-ai 경로 추가됨: {mkm_core_ai_path}")
    else:
        MKM_CORE_AI_AVAILABLE = False
        print(f"⚠️ mkm-core-ai 경로를 찾을 수 없음: {mkm_core_ai_path}")
except Exception as e:
    MKM_CORE_AI_AVAILABLE = False
    print(f"❌ mkm-core-ai 경로 추가 실패: {e}")

class HealthAnalyzer:
    """RPPG + Voice 통합 건강 분석 서비스 (실제 알고리즘 구현)"""
    
    def __init__(self):
        self.rppg_analyzer = None
        self.voice_analyzer = None
        self.analysis_method = "enhanced_backend"
        
        # mkm-core-ai 모듈 초기화 시도
        if MKM_CORE_AI_AVAILABLE:
            try:
                self._initialize_mkm_core_ai()
                self.analysis_method = "mkm-core-ai"
            except Exception as e:
                print(f"⚠️ mkm-core-ai 초기화 실패: {e}")
                self.analysis_method = "enhanced_backend"
    
    def _initialize_mkm_core_ai(self):
        """mkm-core-ai 모듈 초기화"""
        try:
            # RPPG 분석기 초기화
            from rppg.rppg_opensource_collector import RPPGAnalyzer
            self.rppg_analyzer = RPPGAnalyzer()
            print("✅ RPPG 분석기 초기화 성공")
        except ImportError as e:
            print(f"⚠️ RPPG 분석기 import 실패: {e}")
        
        try:
            # Voice 분석기 초기화
            from voice.voice_upgrade_complete_collector import VoiceAnalyzer
            self.voice_analyzer = VoiceAnalyzer()
            print("✅ Voice 분석기 초기화 성공")
        except ImportError as e:
            print(f"⚠️ Voice 분석기 import 실패: {e}")
    
    async def enhance_analysis(
        self,
        rppg_data: List[Dict],
        voice_data: List[Dict],
        rppg_result: Dict,
        voice_result: Dict
    ) -> Dict[str, Any]:
        """프론트엔드 분석 결과를 백엔드에서 추가 분석하여 향상"""
        
        try:
            # RPPG 데이터 추가 분석
            enhanced_rppg = self._enhance_rppg_analysis(rppg_data, rppg_result)
            
            # 음성 데이터 추가 분석
            enhanced_voice = self._enhance_voice_analysis(voice_data, voice_result)
            
            # 종합 건강 점수 계산
            overall_score = self._calculate_comprehensive_score(enhanced_rppg, enhanced_voice)
            
            # 결과 통합
            result = {
                "rppg": enhanced_rppg,
                "voice": enhanced_voice,
                "overall_score": overall_score,
                "analysis_method": self.analysis_method,
                "timestamp": datetime.utcnow().isoformat(),
                "data_quality": self._assess_data_quality(rppg_data, voice_data),
                "recommendations": self._generate_recommendations(enhanced_rppg, enhanced_voice)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 향상된 분석 중 오류 발생: {e}")
            return self._get_error_result(str(e))
    
    def _enhance_rppg_analysis(self, rppg_data: List[Dict], rppg_result: Dict) -> Dict[str, Any]:
        """RPPG 데이터 추가 분석"""
        try:
            if not rppg_data:
                return rppg_result
            
            # 원시 데이터에서 RPPG 신호 추출
            timestamps = [item['timestamp'] for item in rppg_data]
            red_values = [item['redValue'] for item in rppg_data]
            
            # 신호 전처리
            red_values = np.array(red_values)
            red_values = red_values - np.mean(red_values)  # DC 성분 제거
            
            # FFT를 통한 주파수 분석
            if len(red_values) > 10:
                fft = np.fft.fft(red_values)
                freqs = np.fft.fftfreq(len(red_values), 1/30)  # 30fps 가정
                
                # 심박수 관련 주파수 대역 (0.8-3.0 Hz, 48-180 bpm)
                heart_rate_mask = (freqs > 0.8) & (freqs < 3.0)
                heart_rate_power = np.abs(fft[heart_rate_mask])
                
                if len(heart_rate_power) > 0:
                    peak_freq_idx = np.argmax(heart_rate_power)
                    peak_freq = freqs[heart_rate_mask][peak_freq_idx]
                    estimated_hr = abs(peak_freq * 60)  # Hz to bpm
                    
                    # 기존 결과와 비교하여 신뢰도 향상
                    if 'heartRate' in rppg_result:
                        enhanced_hr = (rppg_result['heartRate'] + estimated_hr) / 2
                    else:
                        enhanced_hr = estimated_hr
                    
                    # HRV 계산 (간단한 방법)
                    hrv = self._calculate_simple_hrv(red_values)
                    
                    return {
                        **rppg_result,
                        "heart_rate": round(enhanced_hr, 1),
                        "hrv": round(hrv, 1),
                        "signal_quality": self._assess_rppg_signal_quality(red_values),
                        "analysis_confidence": min(0.95, 0.7 + len(rppg_data) / 100)
                    }
            
            return rppg_result
            
        except Exception as e:
            print(f"⚠️ RPPG 향상 분석 실패: {e}")
            return rppg_result
    
    def _enhance_voice_analysis(self, voice_data: List[Dict], voice_result: Dict) -> Dict[str, Any]:
        """음성 데이터 추가 분석"""
        try:
            if not voice_data:
                return voice_result
            
            # 음성 데이터 품질 평가
            voice_quality = self._assess_voice_quality(voice_data)
            
            # 기존 결과에 품질 정보 추가
            enhanced_result = {
                **voice_result,
                "recording_quality": voice_quality,
                "analysis_confidence": min(0.95, 0.6 + len(voice_data) / 10)
            }
            
            return enhanced_result
            
        except Exception as e:
            print(f"⚠️ Voice 향상 분석 실패: {e}")
            return voice_result
    
    def _calculate_simple_hrv(self, signal: np.ndarray) -> float:
        """간단한 HRV 계산"""
        try:
            if len(signal) < 20:
                return 50.0  # 기본값
            
            # 피크 검출
            peaks, _ = signal.find_peaks(signal, height=np.mean(signal), distance=5)
            
            if len(peaks) < 3:
                return 50.0
            
            # RR 간격 계산
            rr_intervals = np.diff(peaks)
            hrv = np.std(rr_intervals) * 1000 / 30  # 30fps 가정, ms 단위
            
            return max(20.0, min(100.0, hrv))  # 20-100ms 범위로 제한
            
        except Exception:
            return 50.0
    
    def _assess_rppg_signal_quality(self, signal: np.ndarray) -> str:
        """RPPG 신호 품질 평가"""
        try:
            if len(signal) < 10:
                return "poor"
            
            # 신호 대 잡음비 (SNR) 계산
            signal_power = np.var(signal)
            noise_power = np.var(np.diff(signal))
            
            if noise_power == 0:
                snr = float('inf')
            else:
                snr = 10 * np.log10(signal_power / noise_power)
            
            if snr > 20:
                return "excellent"
            elif snr > 15:
                return "good"
            elif snr > 10:
                return "fair"
            else:
                return "poor"
                
        except Exception:
            return "unknown"
    
    def _assess_voice_quality(self, voice_data: List[Dict]) -> str:
        """음성 데이터 품질 평가"""
        try:
            if len(voice_data) < 2:
                return "poor"
            
            # 녹음 시간 및 데이터 양 평가
            duration = len(voice_data) / 10  # 10fps 가정
            
            if duration >= 4.5:  # 5초 중 4.5초 이상
                return "excellent"
            elif duration >= 3.5:
                return "good"
            elif duration >= 2.5:
                return "fair"
            else:
                return "poor"
                
        except Exception:
            return "unknown"
    
    def _calculate_comprehensive_score(self, rppg_result: Dict, voice_result: Dict) -> int:
        """종합 건강 점수 계산"""
        try:
            score = 70  # 기본 점수
            
            # RPPG 점수 (40점)
            if 'heart_rate' in rppg_result:
                hr = rppg_result['heart_rate']
                if 60 <= hr <= 100:  # 정상 심박수
                    score += 20
                elif 50 <= hr <= 110:  # 허용 범위
                    score += 15
                else:
                    score += 10
            
            if 'hrv' in rppg_result:
                hrv = rppg_result['hrv']
                if hrv >= 50:  # 좋은 HRV
                    score += 20
                elif hrv >= 30:
                    score += 15
                else:
                    score += 10
            
            # 음성 점수 (30점)
            if 'recording_quality' in voice_result:
                quality = voice_result['recording_quality']
                if quality == 'excellent':
                    score += 30
                elif quality == 'good':
                    score += 25
                elif quality == 'fair':
                    score += 20
                else:
                    score += 15
            
            return min(100, max(0, score))
            
        except Exception:
            return 75  # 기본 점수
    
    def _assess_data_quality(self, rppg_data: List[Dict], voice_data: List[Dict]) -> Dict[str, str]:
        """전체 데이터 품질 평가"""
        return {
            "rppg_quality": self._assess_rppg_signal_quality([d['redValue'] for d in rppg_data]) if rppg_data else "unknown",
            "voice_quality": self._assess_voice_quality(voice_data) if voice_data else "unknown",
            "overall_quality": "good" if (len(rppg_data) >= 30 and len(voice_data) >= 3) else "poor"
        }
    
    def _generate_recommendations(self, rppg_result: Dict, voice_result: Dict) -> List[str]:
        """건강 개선 권장사항 생성"""
        recommendations = []
        
        try:
            # RPPG 기반 권장사항
            if 'heart_rate' in rppg_result:
                hr = rppg_result['heart_rate']
                if hr > 100:
                    recommendations.append("심박수가 높습니다. 스트레스 관리와 충분한 휴식을 권장합니다.")
                elif hr < 60:
                    recommendations.append("심박수가 낮습니다. 규칙적인 운동을 권장합니다.")
            
            if 'hrv' in rppg_result:
                hrv = rppg_result['hrv']
                if hrv < 30:
                    recommendations.append("HRV가 낮습니다. 명상이나 깊은 호흡 운동을 권장합니다.")
            
            # 음성 기반 권장사항
            if 'recording_quality' in voice_result:
                quality = voice_result['recording_quality']
                if quality == 'poor':
                    recommendations.append("음성 녹음 품질이 낮습니다. 조용한 환경에서 다시 측정해주세요.")
            
            # 기본 권장사항
            if not recommendations:
                recommendations.append("전반적으로 건강한 상태입니다. 현재의 생활습관을 유지하세요.")
            
        except Exception as e:
            recommendations.append("분석 중 오류가 발생했습니다. 다시 측정해주세요.")
        
        return recommendations
    
    async def analyze_health(self, video_data: bytes, audio_data: bytes) -> Dict[str, Any]:
        """파일 기반 건강 상태 통합 분석 (기존 메서드 유지)"""
        
        try:
            # RPPG 분석
            rppg_result = await self._analyze_rppg(video_data)
            
            # Voice 분석
            voice_result = await self._analyze_voice(audio_data)
            
            # 결과 통합
            result = {
                "rppg": rppg_result,
                "voice": voice_result,
                "analysis_method": self.analysis_method,
                "timestamp": datetime.utcnow().isoformat(),
                "quality_score": self._calculate_overall_quality(rppg_result, voice_result)
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 건강 분석 중 오류 발생: {e}")
            return self._get_error_result(str(e))
    
    async def _analyze_rppg(self, video_data: bytes) -> Dict[str, Any]:
        """RPPG 분석 실행"""
        try:
            if self.rppg_analyzer and self.analysis_method == "mkm-core-ai":
                # TODO: 실제 mkm-core-ai RPPG 분석 구현
                return self._get_mock_rppg_result()
            else:
                return self._get_mock_rppg_result()
                
        except Exception as e:
            print(f"⚠️ RPPG 분석 실패: {e}")
            return self._get_mock_rppg_result()
    
    async def _analyze_voice(self, audio_data: bytes) -> Dict[str, Any]:
        """Voice 분석 실행"""
        try:
            if self.voice_analyzer and self.analysis_method == "mkm-core-ai":
                # TODO: 실제 mkm-core-ai Voice 분석 구현
                return self._get_mock_voice_result()
            else:
                return self._get_mock_voice_result()
                
        except Exception as e:
            print(f"⚠️ Voice 분석 실패: {e}")
            return self._get_mock_voice_result()
    
    def _get_mock_rppg_result(self) -> Dict[str, Any]:
        """RPPG 모의 결과 (개발용) - 허위 데이터 생성 금지"""
        raise NotImplementedError("허위 데이터 생성은 금지되었습니다. 실제 RPPG 분석기를 구현해야 합니다.")
    
    def _get_mock_voice_result(self) -> Dict[str, Any]:
        """Voice 모의 결과 (개발용) - 허위 데이터 생성 금지"""
        raise NotImplementedError("허위 데이터 생성은 금지되었습니다. 실제 음성 분석기를 구현해야 합니다.")
    
    def _calculate_overall_quality(self, rppg_result: Dict, voice_result: Dict) -> float:
        """전체 품질 점수 계산"""
        try:
            rppg_quality = rppg_result.get("quality_score", 0)
            voice_quality = voice_result.get("quality_score", 0)
            
            # 가중 평균 (RPPG 60%, Voice 40%)
            overall_quality = (rppg_quality * 0.6) + (voice_quality * 0.4)
            
            return round(overall_quality, 1)
            
        except Exception:
            return 80.0  # 기본값
    
    def _get_error_result(self, error_message: str) -> Dict[str, Any]:
        """오류 발생 시 결과"""
        return {
            "rppg": {
                "error": "RPPG 분석 실패",
                "message": error_message,
                "status": "error"
            },
            "voice": {
                "error": "Voice 분석 실패",
                "message": error_message,
                "status": "error"
            },
            "analysis_method": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "quality_score": 0
        }
    
    def get_analysis_status(self) -> Dict[str, Any]:
        """분석 서비스 상태 확인"""
        return {
            "mkm_core_ai_available": MKM_CORE_AI_AVAILABLE,
            "analysis_method": self.analysis_method,
            "rppg_analyzer_ready": self.rppg_analyzer is not None,
            "voice_analyzer_ready": self.voice_analyzer is not None,
            "status": "ready" if self.analysis_method != "error" else "error"
        } 