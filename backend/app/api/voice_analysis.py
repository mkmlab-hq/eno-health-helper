from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import numpy as np
import librosa
import io
import logging
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["Voice Analysis"])


class VoiceAnalyzer:
    """실제 음성 분석 알고리즘을 구현한 클래스"""
    
    def __init__(self):
        self.sample_rate = 22050  # 표준 샘플링 레이트
        self.frame_length = 2048
        self.hop_length = 512
        
    def analyze_voice(self, audio_data: bytes) -> Dict[str, Any]:
        """음성 파일 분석"""
        try:
            # 오디오 데이터를 numpy 배열로 변환
            audio, sr = librosa.load(io.BytesIO(audio_data), sr=self.sample_rate)
            
            logger.info(f"음성 분석 시작: {len(audio)/sr:.2f}초, {sr}Hz")
            
            # 기본 음성 특성 추출
            features = {}
            
            # F0 (기본 주파수) 추출
            features['f0'] = self.extract_f0(audio, sr)
            
            # Jitter (주파수 변동성) 계산
            features['jitter'] = self.calculate_jitter(features['f0'])
            
            # Shimmer (진폭 변동성) 계산
            features['shimmer'] = self.calculate_shimmer(audio, features['f0'], sr)
            
            # HNR (Harmonic-to-Noise Ratio) 계산
            features['hnr'] = self.calculate_hnr(audio, sr)
            
            # 음성 품질 평가
            features['voice_quality'] = self.assess_voice_quality(features)
            
            # 스트레스 레벨 추정
            features['stress_level'] = self.estimate_voice_stress(features)
            
            return features
            
        except Exception as e:
            logger.error(f"음성 분석 실패: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"음성 분석 중 오류 발생: {str(e)}"
            )
    
    def extract_f0(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """F0 (기본 주파수) 추출"""
        # Pyin 알고리즘을 사용하여 F0 추출
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio, 
            fmin=librosa.note_to_hz('C2'),  # 65.41 Hz
            fmax=librosa.note_to_hz('C7'),  # 2093 Hz
            sr=sr,
            frame_length=self.frame_length,
            hop_length=self.hop_length
        )
        
        # voiced 프레임만 선택
        voiced_f0 = f0[voiced_flag]
        
        if len(voiced_f0) == 0:
            raise ValueError("유효한 F0를 추출할 수 없습니다")
        
        return voiced_f0
    
    def calculate_jitter(self, f0: np.ndarray) -> float:
        """Jitter (주파수 변동성) 계산"""
        if len(f0) < 2:
            return 0.0
        
        # RAP (Relative Average Perturbation) 계산
        jitter_values = []
        for i in range(1, len(f0) - 1):
            if f0[i] > 0 and f0[i-1] > 0 and f0[i+1] > 0:
                # 연속된 3개 프레임의 F0 변동성
                jitter = abs(f0[i] - (f0[i-1] + f0[i+1]) / 2) / f0[i]
                jitter_values.append(jitter)
        
        if len(jitter_values) == 0:
            return 0.0
        
        # 평균 Jitter (백분율)
        return np.mean(jitter_values) * 100
    
    def calculate_shimmer(self, audio: np.ndarray, f0: np.ndarray, 
                         sr: int) -> float:
        """Shimmer (진폭 변동성) 계산"""
        if len(f0) == 0:
            return 0.0
        
        # F0 프레임에 해당하는 오디오 프레임 추출
        frame_length = self.frame_length
        hop_length = self.hop_length
        
        shimmer_values = []
        
        for i, freq in enumerate(f0):
            if freq > 0:
                # 해당 프레임의 시작과 끝 인덱스
                start_idx = i * hop_length
                end_idx = start_idx + frame_length
                
                if end_idx < len(audio):
                    frame = audio[start_idx:end_idx]
                    
                    # RMS (Root Mean Square) 계산
                    rms = np.sqrt(np.mean(frame ** 2))
                    
                    if rms > 0:
                        # 이전 프레임과의 진폭 변동성
                        if i > 0 and i < len(f0) - 1:
                            prev_start = (i-1) * hop_length
                            prev_end = prev_start + frame_length
                            
                            if prev_end < len(audio):
                                prev_frame = audio[prev_start:prev_end]
                                prev_rms = np.sqrt(np.mean(prev_frame ** 2))
                                
                                if prev_rms > 0:
                                    shimmer = abs(rms - prev_rms) / prev_rms
                                    shimmer_values.append(shimmer)
        
        if len(shimmer_values) == 0:
            return 0.0
        
        # 평균 Shimmer (백분율)
        return np.mean(shimmer_values) * 100
    
    def calculate_hnr(self, audio: np.ndarray, sr: int) -> float:
        """HNR (Harmonic-to-Noise Ratio) 계산"""
        # 스펙트럼 분석
        stft = librosa.stft(audio, n_fft=self.frame_length, 
                           hop_length=self.hop_length)
        
        # 전력 스펙트럼
        power_spectrum = np.abs(stft) ** 2
        
        # 평균 전력 스펙트럼
        mean_power = np.mean(power_spectrum, axis=1)
        
        # 하모닉 성분과 노이즈 성분 분리
        # 간단한 방법: 피크 주변의 전력과 전체 전력의 비율
        peaks = librosa.util.peak_pick(mean_power, pre_max=3, post_max=3, 
                                      pre_avg=3, post_avg=5, delta=0.5, wait=10)
        
        if len(peaks) == 0:
            return 0.0
        
        # 하모닉 전력 (피크 주변)
        harmonic_power = 0
        for peak in peaks:
            start_idx = max(0, peak - 2)
            end_idx = min(len(mean_power), peak + 3)
            harmonic_power += np.sum(mean_power[start_idx:end_idx])
        
        # 노이즈 전력 (전체 - 하모닉)
        total_power = np.sum(mean_power)
        noise_power = total_power - harmonic_power
        
        if noise_power <= 0:
            return 100.0  # 노이즈가 거의 없는 경우
        
        # HNR (dB)
        hnr = 10 * np.log10(harmonic_power / noise_power)
        return max(0.0, hnr)  # 음수 값 방지
    
    def assess_voice_quality(self, features: Dict[str, Any]) -> str:
        """음성 품질 평가"""
        f0 = features.get('f0', np.array([]))
        jitter = features.get('jitter', 0)
        shimmer = features.get('shimmer', 0)
        hnr = features.get('hnr', 0)
        
        if len(f0) == 0:
            return "측정 불가"
        
        # F0 안정성 평가
        f0_std = np.std(f0)
        f0_cv = f0_std / np.mean(f0) if np.mean(f0) > 0 else 0
        
        # 품질 점수 계산 (0-100)
        quality_score = 100
        
        # F0 변동성에 따른 감점
        if f0_cv > 0.1:  # 10% 이상 변동
            quality_score -= 30
        elif f0_cv > 0.05:  # 5% 이상 변동
            quality_score -= 15
        
        # Jitter에 따른 감점
        if jitter > 2.0:  # 2% 이상
            quality_score -= 25
        elif jitter > 1.0:  # 1% 이상
            quality_score -= 10
        
        # Shimmer에 따른 감점
        if shimmer > 5.0:  # 5% 이상
            quality_score -= 20
        elif shimmer > 2.0:  # 2% 이상
            quality_score -= 10
        
        # HNR에 따른 감점
        if hnr < 10:  # 10dB 미만
            quality_score -= 20
        elif hnr < 15:  # 15dB 미만
            quality_score -= 10
        
        # 품질 등급 분류
        if quality_score >= 80:
            return "우수"
        elif quality_score >= 60:
            return "양호"
        elif quality_score >= 40:
            return "보통"
        else:
            return "낮음"
    
    def estimate_voice_stress(self, features: Dict[str, Any]) -> str:
        """음성 기반 스트레스 레벨 추정"""
        jitter = features.get('jitter', 0)
        shimmer = features.get('shimmer', 0)
        hnr = features.get('hnr', 0)
        
        # 스트레스 점수 계산 (0-100)
        stress_score = 0
        
        # Jitter 기반 스트레스
        if jitter > 3.0:
            stress_score += 30
        elif jitter > 2.0:
            stress_score += 20
        elif jitter > 1.0:
            stress_score += 10
        
        # Shimmer 기반 스트레스
        if shimmer > 8.0:
            stress_score += 25
        elif shimmer > 5.0:
            stress_score += 15
        elif shimmer > 2.0:
            stress_score += 10
        
        # HNR 기반 스트레스
        if hnr < 8:
            stress_score += 25
        elif hnr < 12:
            stress_score += 15
        elif hnr < 15:
            stress_score += 10
        
        # 스트레스 레벨 분류
        if stress_score >= 60:
            return "높음"
        elif stress_score >= 40:
            return "보통"
        elif stress_score >= 20:
            return "낮음"
        else:
            return "매우 낮음"


@router.post("/analyze")
async def analyze_voice(audio: UploadFile = File(...)):
    """음성 분석 API 엔드포인트"""
    try:
        # 파일 형식 검증
        if not audio.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
            raise HTTPException(
                status_code=400, 
                detail="지원하지 않는 오디오 형식입니다. WAV, MP3, M4A, FLAC만 지원합니다."
            )
        
        # 파일 크기 검증 (최대 50MB)
        if audio.size > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=400, 
                detail="파일 크기가 너무 큽니다. 50MB 이하만 지원합니다."
            )
        
        # 오디오 데이터 읽기
        audio_data = await audio.read()
        
        if len(audio_data) == 0:
            raise HTTPException(
                status_code=400, 
                detail="오디오 파일이 비어있습니다."
            )
        
        logger.info(f"음성 분석 요청: {audio.filename}, {len(audio_data)} bytes")
        
        # 음성 분석 실행
        analyzer = VoiceAnalyzer()
        result = analyzer.analyze_voice(audio_data)
        
        # 최종 결과
        final_result = {
            "success": True,
            "filename": audio.filename,
            "f0_mean": float(np.mean(result['f0'])) if len(result['f0']) > 0 else 0,
            "f0_std": float(np.std(result['f0'])) if len(result['f0']) > 0 else 0,
            "jitter": round(result['jitter'], 2),
            "shimmer": round(result['shimmer'], 2),
            "hnr": round(result['hnr'], 2),
            "voice_quality": result['voice_quality'],
            "stress_level": result['stress_level'],
            "analysis_duration": len(result['f0']) * 0.023  # hop_length/sr
        }
        
        logger.info(f"음성 분석 완료: 품질 {result['voice_quality']}, "
                   f"스트레스 {result['stress_level']}")
        
        return JSONResponse(content=final_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"음성 분석 실패: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"음성 분석 중 오류 발생: {str(e)}"
        )


@router.get("/health")
async def voice_health_check():
    """음성 분석 서비스 상태 확인"""
    return {
        "service": "Voice Analysis", 
        "status": "healthy", 
        "version": "2.0.0",
        "features": [
            "실제 Librosa 기반 F0 추출",
            "Jitter 및 Shimmer 계산",
            "HNR (Harmonic-to-Noise Ratio) 분석",
            "음성 품질 평가",
            "스트레스 레벨 추정"
        ]
    }
