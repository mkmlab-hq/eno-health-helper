'use client';

import React, { useState } from 'react';
import Link from 'next/link';

interface SimpleExamination {
  voiceAnalysis: {
    jitter: number;
    shimmer: number;
    hnr: number;
    stability: number;
  };
  faceAnalysis: {
    heartRate: number;
    stressLevel: number;
    bloodPressure: string;
    hrv: number;
  };
  tongueAnalysis: {
    tongueColor: string;
    tongueCoating: string;
    tongueShape: string;
    moisture: string;
  };
}

interface AnonymizedPatient {
  id: string;
  ageGroup: string;
  gender: string;
  examinationResults: SimpleExamination;
  timestamp: string;
}

interface SOAPChart {
  patientId: string;
  date: string;
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
  medicalInfo: {
    medications: MedicationInfo[];
    muscleAnalysis: MuscleInfo[];
    exerciseRecommendations: ExerciseInfo[];
  };
}

interface MedicationInfo {
  name: string;
  category: string;
  description: string;
  sideEffects: string;
  interactions: string;
}

interface MuscleInfo {
  condition: string;
  possibleCauses: string[];
  physicalTests: string[];
  description: string;
}

interface ExerciseInfo {
  name: string;
  description: string;
  instructions: string[];
  frequency: string;
}

export default function ChartDowmi() {
  const [currentView, setCurrentView] = useState<'examination' | 'doctor' | 'result'>('examination');
  const [examinationData, setExaminationData] = useState<SimpleExamination | null>(null);
  const [anonymizedPatient, setAnonymizedPatient] = useState<AnonymizedPatient | null>(null);
  const [doctorNotes, setDoctorNotes] = useState<string>('');
  const [soapChart, setSoapChart] = useState<SOAPChart | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  
  // 실제 검사용 refs (향후 구현)
  // const videoRef = useRef<HTMLVideoElement>(null);
  // const audioRecorderRef = useRef<MediaRecorder | null>(null);

  // 의학적 정보 데이터베이스
  const medicalInfoDB = {
    medications: {
      '졸피뎀': {
        name: '졸피뎀',
        category: '수면제',
        description: '불면증 치료용 수면제로 GABA 수용체에 작용하여 수면을 유도합니다.',
        sideEffects: '졸음, 어지러움, 기억력 저하, 의존성',
        interactions: '알코올과 함께 복용 시 호흡 억제 위험, 항우울제와 상호작용 가능'
      },
      '아스피린': {
        name: '아스피린',
        category: '해열진통제',
        description: '염증 억제, 해열, 진통 효과가 있는 비스테로이드성 항염제입니다.',
        sideEffects: '위장장애, 출혈 위험, 알레르기 반응',
        interactions: '와파린과 함께 복용 시 출혈 위험 증가'
      }
    },
    muscleAnalysis: {
      '요통': {
        condition: '요통',
        possibleCauses: ['요추 디스크', '근육 긴장', '좌골신경통', '척추관 협착'],
        physicalTests: ['SLR 테스트 (Straight Leg Raising)', 'Patrick 테스트', 'Schober 테스트'],
        description: '요추 부위의 통증으로 다양한 원인에 의해 발생할 수 있습니다.'
      },
      '목통증': {
        condition: '목통증',
        possibleCauses: ['경추 디스크', '목 근육 긴장', '자세 불량', '스트레스'],
        physicalTests: ['목 굴곡/신전 테스트', 'Spurling 테스트', '목 회전 테스트'],
        description: '경추 부위의 통증으로 주로 자세나 스트레스와 관련이 있습니다.'
      }
    },
    exerciseRecommendations: {
      '요통': {
        name: '요통 완화 운동',
        description: '요추 안정화와 근육 강화를 위한 운동',
        instructions: [
          '고양이 자세: 네발로 엎드려 척추를 천천히 굽혔다 펴기',
          '무릎 가슴 당기기: 누워서 무릎을 가슴 쪽으로 당기기',
          '브릿지: 누워서 엉덩이를 들어올리기',
          '플랭크: 팔꿈치와 발끝으로 몸을 지탱하기'
        ],
        frequency: '하루 2-3회, 각 동작 10-15회 반복'
      }
    }
  };

  const analysisSteps = [
    '검사 데이터 수집',
    '비식별화 처리',
    'AI 패턴 분석',
    '의학적 정보 매칭',
    'SOAP 차트 생성',
    '결과 통합 완료'
  ];

  // 간소화된 검사 시작
  const startExamination = async () => {
    try {
      // 실제 검사 진행상황 표시
      setIsAnalyzing(true);
      setAnalysisProgress(0);
      
      // 검사 단계별 진행
      const steps = [
        { name: '음성 분석', duration: 1000 },
        { name: '얼굴 분석', duration: 1000 },
        { name: '설진 분석', duration: 1000 },
        { name: '데이터 처리', duration: 1000 }
      ];
      
      let currentStep = 0;
      const totalSteps = steps.length;
      
      for (const step of steps) {
        // 단계별 진행률 업데이트
        setAnalysisProgress((currentStep / totalSteps) * 100);
        await new Promise(resolve => setTimeout(resolve, step.duration));
        currentStep++;
      }
      
      // 음성 분석 (실제 구현 시 API 호출)
      const voiceAnalysis = {
        jitter: 0.8 + Math.random() * 0.4,
        shimmer: 0.12 + Math.random() * 0.08,
        hnr: 15 + Math.random() * 10,
        stability: 0.85 + Math.random() * 0.1
      };

      // 얼굴 분석 (실제 구현 시 rPPG API 호출)
      const faceAnalysis = {
        heartRate: 65 + Math.random() * 20,
        stressLevel: 30 + Math.random() * 40,
        bloodPressure: `${120 + Math.random() * 20}/${80 + Math.random() * 10}`,
        hrv: 40 + Math.random() * 30
      };

      // 설진 분석 (실제 구현 시 이미지 분석 API 호출)
      const tongueAnalysis = {
        tongueColor: ['연한 분홍', '진한 분홍', '연한 빨강'][Math.floor(Math.random() * 3)],
        tongueCoating: ['얇은 백태', '두꺼운 백태', '황태', '무태'][Math.floor(Math.random() * 4)],
        tongueShape: ['정상', '비대', '얇음'][Math.floor(Math.random() * 3)],
        moisture: ['적절', '건조', '습윤'][Math.floor(Math.random() * 3)]
      };

      const examinationData: SimpleExamination = {
        voiceAnalysis,
        faceAnalysis,
        tongueAnalysis
      };

      setExaminationData(examinationData);
      
      // 비식별화 처리 (실제 구현 시 암호화)
      const anonymizedPatient: AnonymizedPatient = {
        id: `PAT_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`,
        ageGroup: '30-40',
        gender: 'M',
        examinationResults: examinationData,
        timestamp: new Date().toISOString()
      };

      setAnonymizedPatient(anonymizedPatient);
      setIsAnalyzing(false);
      setAnalysisProgress(100);
      setCurrentView('doctor');
      
    } catch (error) {
      console.error('검사 중 오류 발생:', error);
      setIsAnalyzing(false);
      setAnalysisProgress(0);
      alert('검사 중 오류가 발생했습니다. 다시 시도해주세요.');
    }
  };

  // AI 융합 및 SOAP 차트 생성
  const generateSOAPChart = () => {
    if (!examinationData || !doctorNotes) return;
    
    setIsAnalyzing(true);
    setAnalysisProgress(0);
    
    const interval = setInterval(() => {
      setAnalysisProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsAnalyzing(false);
          
          // SOAP 차트 생성
          const newSOAPChart: SOAPChart = {
            patientId: anonymizedPatient?.id || 'UNKNOWN',
            date: new Date().toISOString().split('T')[0],
            subjective: doctorNotes,
            objective: `음성: Jitter ${examinationData.voiceAnalysis.jitter.toFixed(2)}, Shimmer ${examinationData.voiceAnalysis.shimmer.toFixed(2)} | 얼굴: 심박수 ${examinationData.faceAnalysis.heartRate.toFixed(0)}bpm, 스트레스 ${examinationData.faceAnalysis.stressLevel.toFixed(0)}% | 설진: 설질 ${examinationData.tongueAnalysis.tongueColor}, 설태 ${examinationData.tongueAnalysis.tongueCoating}`,
            assessment: '음성 및 생체신호 분석 결과를 종합한 평가',
            plan: '개인화된 치료 계획 및 권장사항',
            medicalInfo: {
              medications: [medicalInfoDB.medications.졸피뎀],
              muscleAnalysis: [medicalInfoDB.muscleAnalysis.요통],
              exerciseRecommendations: [medicalInfoDB.exerciseRecommendations.요통]
            }
          };
          
          setSoapChart(newSOAPChart);
          setCurrentView('result');
          return 100;
        }
        return prev + 16.67;
      });
    }, 1000);
  };

  // 복사 가능한 결과 생성
  const generateCopyableResult = () => {
    if (!soapChart) return '';
    
    return `
환자 검사 결과 (비식별화):
환자 ID: ${soapChart.patientId}
날짜: ${soapChart.date}

=== 검사 데이터 ===
음성 분석:
- Jitter: ${examinationData?.voiceAnalysis.jitter.toFixed(2)}
- Shimmer: ${examinationData?.voiceAnalysis.shimmer.toFixed(2)}
- HNR: ${examinationData?.voiceAnalysis.hnr.toFixed(1)}
- 안정성: ${examinationData?.voiceAnalysis.stability.toFixed(2)}

얼굴 분석:
- 심박수: ${examinationData?.faceAnalysis.heartRate.toFixed(0)} bpm
- 스트레스 수준: ${examinationData?.faceAnalysis.stressLevel.toFixed(0)}%
- 혈압: ${examinationData?.faceAnalysis.bloodPressure}
- HRV: ${examinationData?.faceAnalysis.hrv.toFixed(1)}

설진 분석:
- 설질: ${examinationData?.tongueAnalysis.tongueColor}
- 설태: ${examinationData?.tongueAnalysis.tongueCoating}
- 설형: ${examinationData?.tongueAnalysis.tongueShape}
- 수분: ${examinationData?.tongueAnalysis.moisture}

=== SOAP 차트 ===
S (주관적): ${soapChart.subjective}
O (객관적): ${soapChart.objective}
A (평가): ${soapChart.assessment}
P (계획): ${soapChart.plan}

=== 의학적 정보 ===
약물 정보:
${soapChart.medicalInfo.medications.map(med => 
  `- ${med.name} (${med.category}): ${med.description}`
).join('\n')}

근육 분석:
${soapChart.medicalInfo.muscleAnalysis.map(muscle => 
  `- ${muscle.condition}: ${muscle.description}`
).join('\n')}

운동 권장사항:
${soapChart.medicalInfo.exerciseRecommendations.map(ex => 
  `- ${ex.name}: ${ex.description}\n  방법: ${ex.instructions.join(', ')}\n  빈도: ${ex.frequency}`
).join('\n')}

※ 이 결과를 개인 LLM (ChatGPT 등)에 복사하여 추가 분석을 요청하실 수 있습니다.
    `;
  };

  const copyToClipboard = async () => {
    const content = generateCopyableResult();
    if (!content.trim()) {
      alert('복사할 내용이 없습니다.');
      return;
    }
    
    try {
      await navigator.clipboard.writeText(content);
      alert('결과가 클립보드에 복사되었습니다!\n\n이제 ChatGPT나 다른 LLM에 붙여넣어 추가 분석을 요청하실 수 있습니다.');
    } catch (err) {
      console.error('복사 실패:', err);
      // 폴백: 텍스트 영역에 표시
      const textArea = document.createElement('textarea');
      textArea.value = content;
      document.body.appendChild(textArea);
      textArea.select();
      try {
        const success = document.execCommand('copy');
        if (success) {
          alert('결과가 클립보드에 복사되었습니다!');
        } else {
          throw new Error('execCommand failed');
        }
      } catch (fallbackErr) {
        console.error('폴백 복사 실패:', fallbackErr);
        alert('복사에 실패했습니다. 수동으로 복사해주세요.');
      }
      document.body.removeChild(textArea);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900">
      {/* 헤더 */}
      <header className="relative z-10 p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-eno-500 to-eno-400 rounded-2xl flex items-center justify-center shadow-neon-cyan">
              <div className="w-6 h-6 text-white neon-glow">📊</div>
            </div>
            <div>
              <h1 className="text-2xl font-orbitron font-bold text-white neon-text">
                AI 차트 도우미
              </h1>
              <p className="text-sm text-gray-300 font-noto">간호조무사 → 원장 AI 융합 SOAP 차트</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setCurrentView('examination')}
              className={`glass-button ${currentView === 'examination' ? 'bg-eno-400/20' : ''}`}
            >
              🩺 검사
            </button>
            <button
              onClick={() => setCurrentView('doctor')}
              className={`glass-button ${currentView === 'doctor' ? 'bg-eno-400/20' : ''}`}
            >
              👨‍⚕️ 원장
            </button>
            <button
              onClick={() => setCurrentView('result')}
              className={`glass-button ${currentView === 'result' ? 'bg-eno-400/20' : ''}`}
            >
              📋 결과
            </button>
            <Link 
              href="/"
              className="glass-button text-gray-300 hover:text-eno-400 transition-colors font-noto"
            >
              🏠 홈으로
            </Link>
          </div>
        </div>
      </header>

      <main className="relative z-10 px-6 pb-20">
        <div className="max-w-7xl mx-auto">
          {/* 히어로 섹션 */}
          <section className="text-center py-16">
            <h2 className="text-5xl md:text-6xl font-orbitron font-bold mb-6">
              <span className="neon-text">간호조무사 → 원장</span>
              <br/>
              <span className="text-eno-400">AI 융합 SOAP 차트</span>
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-12 font-noto leading-relaxed">
              간소화된 검사 → 원장 기록 → AI 융합 → SOAP 차트 생성<br/>
              <span className="text-eno-400 font-semibold">비식별 데이터로 AI 성장</span>과 의료진 지원을 동시에
            </p>
          </section>

          {/* 간호조무사 검사 화면 */}
          {currentView === 'examination' && (
            <div className="max-w-4xl mx-auto">
              <div className="glass-card p-8 rounded-2xl">
                <h3 className="text-2xl font-orbitron font-bold text-white mb-6 neon-text">
                  🩺 간소화된 검사 시스템
                </h3>
                
                <div className="space-y-6">
                  <div className="text-center">
                    <div className="text-6xl mb-4">📱</div>
                    <h4 className="text-xl font-semibold text-white mb-2">35초 간편 검사</h4>
                    <p className="text-gray-400 mb-6">
                      음성, 얼굴, 설진 분석을 통한 종합 건강 평가
                    </p>
                  </div>

                  <div className="grid md:grid-cols-3 gap-4">
                    <div className="p-4 bg-slate-800 rounded-lg text-center">
                      <div className="text-3xl mb-2">🎤</div>
                      <h5 className="font-semibold text-white mb-1">음성 분석</h5>
                      <p className="text-sm text-gray-400">Jitter, Shimmer, HNR</p>
                    </div>
                    <div className="p-4 bg-slate-800 rounded-lg text-center">
                      <div className="text-3xl mb-2">📷</div>
                      <h5 className="font-semibold text-white mb-1">얼굴 분석</h5>
                      <p className="text-sm text-gray-400">심박수, 스트레스, 혈압</p>
                    </div>
                    <div className="p-4 bg-slate-800 rounded-lg text-center">
                      <div className="text-3xl mb-2">👅</div>
                      <h5 className="font-semibold text-white mb-1">설진 분석</h5>
                      <p className="text-sm text-gray-400">설질, 설태, 수분</p>
                    </div>
                  </div>

                  <div className="text-center">
                    <button
                      onClick={startExamination}
                      disabled={isAnalyzing}
                      className="glass-button text-lg py-4 px-8 font-semibold neon-glow disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isAnalyzing ? '🔄 검사 진행중...' : '🚀 검사 시작하기'}
                    </button>
                  </div>

                  {isAnalyzing && (
                    <div className="p-6 bg-slate-800 rounded-lg">
                      <h4 className="text-lg font-semibold text-white mb-4">🔄 검사 진행중...</h4>
                      <div className="w-full bg-slate-700 rounded-full h-3 mb-4">
                        <div
                          className="bg-gradient-to-r from-eno-400 to-eno-600 h-3 rounded-full transition-all duration-1000"
                          style={{ width: `${analysisProgress}%` }}
                        />
                      </div>
                      <p className="text-center text-sm text-gray-300">
                        {analysisProgress.toFixed(0)}% 완료
                      </p>
                    </div>
                  )}

                  <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <h5 className="text-blue-400 font-semibold mb-2">💡 검사 후 자동 전송</h5>
                    <p className="text-gray-300 text-sm">
                      검사 완료 후 비식별화된 데이터가 자동으로 원장님께 전송됩니다.
                      개인정보는 완전히 보호되며, AI 성장을 위한 익명 데이터만 수집됩니다.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 원장 화면 */}
          {currentView === 'doctor' && (
            <div className="max-w-4xl mx-auto">
              <div className="glass-card p-8 rounded-2xl">
                <h3 className="text-2xl font-orbitron font-bold text-white mb-6 neon-text">
                  👨‍⚕️ 원장님 차트 통합
                </h3>
                
                <div className="space-y-6">
                  {/* 전송받은 검사 데이터 */}
                  {anonymizedPatient && (
                    <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                      <h4 className="text-green-400 font-semibold mb-3">📨 전송받은 검사 데이터</h4>
                      <div className="grid md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">환자 ID:</span>
                          <p className="text-white font-mono">{anonymizedPatient.id}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">연령대:</span>
                          <p className="text-white">{anonymizedPatient.ageGroup}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">성별:</span>
                          <p className="text-white">{anonymizedPatient.gender}</p>
                        </div>
                      </div>
                      
                      <div className="mt-4 grid md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">음성 안정성:</span>
                          <p className="text-white">{(examinationData?.voiceAnalysis.stability || 0).toFixed(2)}</p>
                        </div>
                        <div>
                          <span className="text-gray-400">심박수:</span>
                          <p className="text-white">{(examinationData?.faceAnalysis.heartRate || 0).toFixed(0)} bpm</p>
                        </div>
                        <div>
                          <span className="text-gray-400">설질:</span>
                          <p className="text-white">{examinationData?.tongueAnalysis.tongueColor}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* 기존 차트 기록 */}
                  <div>
                    <label htmlFor="doctor-notes" className="block text-gray-300 font-semibold mb-2">
                      📝 기존 환자 기록 (복사하여 붙여넣기)
                    </label>
                    <textarea
                      id="doctor-notes"
                      value={doctorNotes}
                      onChange={(e) => setDoctorNotes(e.target.value)}
                      className="w-full h-32 p-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:border-eno-400 focus:ring-2 focus:ring-eno-400/20"
                      placeholder="기존 차트에서 환자 기록을 복사하여 붙여넣어주세요..."
                    />
                  </div>

                  <div className="text-center">
                    <button
                      onClick={generateSOAPChart}
                      disabled={!doctorNotes.trim()}
                      className="glass-button text-lg py-4 px-8 font-semibold neon-glow disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      🔄 AI 융합 SOAP 차트 생성
                    </button>
                  </div>

                  {isAnalyzing && (
                    <div className="p-6 bg-slate-800 rounded-lg">
                      <h4 className="text-lg font-semibold text-white mb-4">🔄 AI 융합 분석 중...</h4>
                      <div className="w-full bg-slate-700 rounded-full h-3 mb-4">
                        <div
                          className="bg-gradient-to-r from-eno-400 to-eno-600 h-3 rounded-full transition-all duration-1000"
                          style={{ width: `${analysisProgress}%` }}
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        {analysisSteps.map((step, index) => (
                          <div
                            key={step}
                            className={`flex items-center space-x-2 text-sm p-2 rounded ${
                              index * 16.67 <= analysisProgress
                                ? 'bg-eno-400/20 text-eno-400' : 'text-gray-500'
                            }`}
                          >
                            <span className={`w-4 h-4 rounded-full flex items-center justify-center text-xs ${
                              index * 16.67 <= analysisProgress
                                ? 'bg-eno-400 text-white' : 'bg-slate-600'
                            }`}>
                              {index * 16.67 <= analysisProgress ? '✓' : index + 1}
                            </span>
                            <span>{step}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 결과 화면 */}
          {currentView === 'result' && soapChart && (
            <div className="max-w-4xl mx-auto">
              <div className="glass-card p-8 rounded-2xl">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-orbitron font-bold text-white neon-text">
                    📋 AI 융합 SOAP 차트
                  </h3>
                  <button
                    onClick={copyToClipboard}
                    className="glass-button px-4 py-2 text-sm"
                  >
                    📋 복사하기
                  </button>
                </div>

                <div className="space-y-6">
                  {/* SOAP 차트 */}
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                        <h4 className="text-red-400 font-semibold mb-2">S - Subjective (주관적 증상)</h4>
                        <p className="text-gray-300 text-sm">{soapChart.subjective}</p>
                      </div>
                      
                      <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                        <h4 className="text-blue-400 font-semibold mb-2">O - Objective (객관적 소견)</h4>
                        <p className="text-gray-300 text-sm">{soapChart.objective}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
                        <h4 className="text-yellow-400 font-semibold mb-2">A - Assessment (평가)</h4>
                        <p className="text-gray-300 text-sm">{soapChart.assessment}</p>
                      </div>
                      
                      <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                        <h4 className="text-green-400 font-semibold mb-2">P - Plan (계획)</h4>
                        <p className="text-gray-300 text-sm">{soapChart.plan}</p>
                      </div>
                    </div>
                  </div>

                  {/* 의학적 정보 */}
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-white">💊 의학적 정보</h4>
                    
                    <div className="grid md:grid-cols-3 gap-4">
                      <div className="p-4 bg-slate-800 rounded-lg">
                        <h5 className="text-eno-400 font-semibold mb-2">약물 정보</h5>
                        {soapChart.medicalInfo.medications.map((med) => (
                          <div key={med.name} className="text-sm text-gray-300 mb-2">
                            <div className="font-semibold">{med.name}</div>
                            <div className="text-xs text-gray-400">{med.description}</div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="p-4 bg-slate-800 rounded-lg">
                        <h5 className="text-eno-400 font-semibold mb-2">근육 분석</h5>
                        {soapChart.medicalInfo.muscleAnalysis.map((muscle) => (
                          <div key={muscle.condition} className="text-sm text-gray-300 mb-2">
                            <div className="font-semibold">{muscle.condition}</div>
                            <div className="text-xs text-gray-400">{muscle.description}</div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="p-4 bg-slate-800 rounded-lg">
                        <h5 className="text-eno-400 font-semibold mb-2">운동 권장</h5>
                        {soapChart.medicalInfo.exerciseRecommendations.map((ex) => (
                          <div key={ex.name} className="text-sm text-gray-300 mb-2">
                            <div className="font-semibold">{ex.name}</div>
                            <div className="text-xs text-gray-400">{ex.frequency}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                    <h5 className="text-blue-400 font-semibold mb-2">💡 활용 방법</h5>
                    <p className="text-gray-300 text-sm">
                      위의 "복사하기" 버튼을 클릭하여 결과를 클립보드에 복사한 후, 
                      개인 LLM (ChatGPT, Claude 등)에 붙여넣어 추가 분석을 요청하실 수 있습니다.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}