const functions = require('firebase-functions');
const admin = require('firebase-admin');
const express = require('express');
const cors = require('cors');

// Firebase Admin 초기화
admin.initializeApp();

const app = express();

// CORS 설정
app.use(cors({ origin: true }));

// 루트 엔드포인트
app.get('/', (req, res) => {
  res.json({
    message: 'MKM Lab eno-health-helper API',
    version: '1.0.0',
    status: 'running',
    timestamp: new Date().toISOString()
  });
});

// 헬스 체크 엔드포인트
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    services: {
      fusion_analyzer: 'ready',
      rppg_analyzer: 'ready',
      voice_analyzer: 'ready',
      health_analyzer: 'ready'
    },
    timestamp: new Date().toISOString()
  });
});

// rPPG-음성 융합 분석
app.post('/api/analyze/fusion', (req, res) => {
  try {
    const { user_id } = req.body;
    
    console.log(`융합 분석 요청: ${user_id}`);
    
    // 모의 융합 분석 결과
    const result = {
      user_id: user_id || 'unknown',
      analysis_type: 'fusion',
      rppg_score: 85.5,
      voice_score: 78.2,
      fusion_score: 82.1,
      digital_temperament: '태양인',
      confidence: 0.89,
      recommendations: [
        '현재 스트레스 수준이 높습니다',
        '충분한 휴식이 필요합니다',
        '규칙적인 운동을 권장합니다'
      ]
    };
    
    res.json({
      success: true,
      data: result,
      timestamp: new Date().toISOString(),
      analysis_type: 'fusion'
    });
    
  } catch (error) {
    console.error('융합 분석 오류:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString(),
      analysis_type: 'fusion'
    });
  }
});

// Firebase Functions HTTP 트리거
exports.eno_health_api = functions.https.onRequest(app);
