const express = require('express');
const Redis = require('ioredis');

const app = express();
const PORT = process.env.PORT || 5001;

// 미들웨어 설정
app.use(express.json());

// CORS 헤더 설정 (미들웨어 없이 직접 설정)
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.sendStatus(200);
  } else {
    next();
  }
});

// Redis 클라이언트 (로컬 에뮬레이터용)
const redis = new Redis({
  host: process.env.REDIS_HOST || 'redis',
  port: process.env.REDIS_PORT || 6379,
  retryDelayOnFailover: 100,
  maxRetriesPerRequest: 3
});

// Pub/Sub 토픽 이름
const TOPIC_NAME = 'ai-analysis-requests';

// 메모리 저장소 (실제로는 Firestore 사용)
const analysisRequests = new Map();
const analysisResults = new Map();

/**
 * Health Check 엔드포인트
 */
app.get('/healthCheck', (req, res) => {
  res.json({
    status: 'healthy',
    message: 'Firebase Functions are running successfully.',
    timestamp: new Date().toISOString(),
    services: {
      firestore: 'simulated',
      redis: 'connected',
      authentication: 'simulated'
    }
  });
});

/**
 * AI 분석 요청 처리
 */
app.post('/requestAIAnalysis', async (req, res) => {
  try {
    const { userId, dataType, dataUrl } = req.body;
    
    // 필수 데이터 검증
    if (!userId || !dataType || !dataUrl) {
      return res.status(400).json({
        error: 'Missing required data: userId, dataType, dataUrl'
      });
    }

    // 요청 ID 생성
    const requestId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // 분석 요청 정보를 메모리에 저장
    const analysisRequest = {
      requestId,
      userId,
      dataType,
      dataUrl,
      status: 'pending',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    analysisRequests.set(requestId, analysisRequest);

    // Redis에 Pub/Sub 메시지 발행 (비동기 처리)
    const message = {
      requestId,
      userId,
      dataType,
      dataUrl,
      timestamp: Date.now()
    };

    await redis.publish(TOPIC_NAME, JSON.stringify(message));

    // 로그 기록
    console.log(`AI analysis request submitted: ${requestId}`, {
      userId,
      dataType,
      dataUrl
    });

    res.json({
      status: 'success',
      message: 'Analysis request submitted successfully.',
      data: {
        requestId,
        status: 'pending',
        estimatedTime: '2-5 minutes'
      }
    });

  } catch (error) {
    console.error('Error in requestAIAnalysis:', error);
    res.status(500).json({
      error: 'Internal server error occurred.'
    });
  }
});

/**
 * AI 분석 결과 조회
 */
app.post('/getAnalysisResult', (req, res) => {
  try {
    const { requestId } = req.body;
    
    if (!requestId) {
      return res.status(400).json({
        error: 'Missing requestId'
      });
    }

    // 메모리에서 분석 결과 조회
    const result = analysisResults.get(requestId);
    
    if (!result) {
      return res.json({
        status: 'pending',
        message: 'Analysis is still in progress.',
        data: null
      });
    }

    res.json({
      status: 'success',
      message: 'Analysis result retrieved successfully.',
      data: result
    });

  } catch (error) {
    console.error('Error in getAnalysisResult:', error);
    res.status(500).json({
      error: 'Internal server error occurred.'
    });
  }
});

/**
 * 사용자 분석 히스토리 조회
 */
app.post('/getUserAnalysisHistory', (req, res) => {
  try {
    const { userId, limit = 10 } = req.body;
    
    if (!userId) {
      return res.status(400).json({
        error: 'Missing userId'
      });
    }

    // 메모리에서 사용자의 분석 히스토리 조회
    const history = Array.from(analysisRequests.values())
      .filter(request => request.userId === userId)
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, limit);

    res.json({
      status: 'success',
      message: 'Analysis history retrieved successfully.',
      data: {
        history,
        total: history.length
      }
    });

  } catch (error) {
    console.error('Error in getUserAnalysisHistory:', error);
    res.status(500).json({
      error: 'Internal server error occurred.'
    });
  }
});

/**
 * AI 분석 결과 처리 (AI 엔진 연동용)
 */
app.post('/processAIAnalysis', (req, res) => {
  try {
    const { requestId, results } = req.body;
    
    if (!requestId || !results) {
      return res.status(400).json({
        error: 'Missing required data: requestId, results'
      });
    }

    // 분석 결과를 메모리에 저장
    const analysisResult = {
      requestId,
      results,
      completedAt: new Date().toISOString(),
      status: 'completed'
    };

    analysisResults.set(requestId, analysisResult);

    // 원본 요청 상태 업데이트
    const originalRequest = analysisRequests.get(requestId);
    if (originalRequest) {
      originalRequest.status = 'completed';
      originalRequest.updatedAt = new Date().toISOString();
      analysisRequests.set(requestId, originalRequest);
    }

    console.log(`AI analysis completed: ${requestId}`, results);

    res.json({
      status: 'success',
      message: 'Analysis result saved successfully.'
    });

  } catch (error) {
    console.error('Error in processAIAnalysis:', error);
    res.status(500).json({
      error: 'Internal server error occurred.'
    });
  }
});

// 서버 시작
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 Firebase Functions 서버가 포트 ${PORT}에서 실행 중입니다.`);
  console.log(`📡 Redis 연결 상태: ${redis.status}`);
  console.log(`🔗 Health Check: http://localhost:${PORT}/healthCheck`);
}); 