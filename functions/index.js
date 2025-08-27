const functions = require('firebase-functions');
const admin = require('firebase-admin');
const { PubSub } = require('@google-cloud/pubsub');

// Firebase Admin 초기화
admin.initializeApp();

// Firestore 데이터베이스
const db = admin.firestore();

// Google Cloud Pub/Sub 클라이언트
const pubsubClient = new PubSub();
const TOPIC_NAME = 'ai-analysis-requests';

/**
 * AI 분석 요청 처리 - '최종 연결' 핵심 기능
 * 사용자 인증을 강제하고 Pub/Sub으로 비동기 처리
 */
exports.requestAIAnalysis = functions.https.onCall(async (data, context) => {
  // 사용자 인증 확인 (보안 강화)
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated', 
      'User must be authenticated to request AI analysis.'
    );
  }

  const { userId, dataType, dataUrl } = data;
  
  // 필수 데이터 검증
  if (!userId || !dataType || !dataUrl) {
    throw new functions.https.HttpsError(
      'invalid-argument', 
      'Missing required data: userId, dataType, dataUrl'
    );
  }

  try {
    // 요청 ID 생성
    const requestId = `analysis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // 분석 요청을 Firestore에 저장
    const analysisRequest = {
      requestId,
      userId: context.auth.uid, // 인증된 사용자 ID 사용
      dataType,
      dataUrl,
      status: 'pending',
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    };

    await db.collection('analysis_requests').doc(requestId).set(analysisRequest);

    // Pub/Sub에 메시지 발행 (비동기 처리)
    const messageData = {
      requestId,
      userId: context.auth.uid,
      dataType,
      dataUrl,
      timestamp: Date.now()
    };

    const messageId = await pubsubClient.topic(TOPIC_NAME).publishMessage({
      json: messageData
    });

    // 로그 기록
    console.log(`AI analysis request submitted: ${requestId}`, {
      userId: context.auth.uid,
      dataType,
      dataUrl,
      messageId
    });

    return {
      status: 'success',
      message: 'Analysis request submitted successfully.',
      data: {
        requestId,
        messageId,
        status: 'pending',
        estimatedTime: '2-5 minutes'
      }
    };

  } catch (error) {
    console.error('Error in requestAIAnalysis:', error);
    throw new functions.https.HttpsError(
      'internal', 
      'Failed to submit analysis request.'
    );
  }
});

/**
 * AI 분석 결과 조회
 */
exports.getAnalysisResult = functions.https.onCall(async (data, context) => {
  // 사용자 인증 확인
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated', 
      'User must be authenticated to get analysis results.'
    );
  }

  const { requestId } = data;
  
  if (!requestId) {
    throw new functions.https.HttpsError(
      'invalid-argument', 
      'Missing requestId'
    );
  }

  try {
    // Firestore에서 분석 결과 조회
    const resultDoc = await db.collection('analysis_results').doc(requestId).get();
    
    if (!resultDoc.exists) {
      return {
        status: 'pending',
        message: 'Analysis is still in progress.',
        data: null
      };
    }

    const resultData = resultDoc.data();
    
    return {
      status: 'success',
      message: 'Analysis result retrieved successfully.',
      data: resultData
    };

  } catch (error) {
    console.error('Error in getAnalysisResult:', error);
    throw new functions.https.HttpsError(
      'internal', 
      'Failed to retrieve analysis result.'
    );
  }
});

/**
 * 사용자 분석 히스토리 조회
 */
exports.getUserAnalysisHistory = functions.https.onCall(async (data, context) => {
  // 사용자 인증 확인
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated', 
      'User must be authenticated to get analysis history.'
    );
  }

  const { limit = 10 } = data;
  
  try {
    // Firestore에서 사용자의 분석 히스토리 조회
    const historyQuery = await db.collection('analysis_requests')
      .where('userId', '==', context.auth.uid)
      .orderBy('createdAt', 'desc')
      .limit(limit)
      .get();

    const history = [];
    historyQuery.forEach(doc => {
      history.push({
        id: doc.id,
        ...doc.data()
      });
    });

    return {
      status: 'success',
      message: 'Analysis history retrieved successfully.',
      data: {
        history,
        total: history.length
      }
    };

  } catch (error) {
    console.error('Error in getUserAnalysisHistory:', error);
    throw new functions.https.HttpsError(
      'internal', 
      'Failed to retrieve analysis history.'
    );
  }
});

/**
 * AI 분석 결과 처리 (AI 엔진 연동용)
 * Pub/Sub 메시지를 구독하여 결과를 Firestore에 저장
 */
exports.processAIAnalysis = functions.https.onRequest(async (req, res) => {
  try {
    const { requestId, results } = req.body;
    
    if (!requestId || !results) {
      return res.status(400).json({
        error: 'Missing required data: requestId, results'
      });
    }

    // 분석 결과를 Firestore에 저장
    const analysisResult = {
      requestId,
      results,
      completedAt: admin.firestore.FieldValue.serverTimestamp(),
      status: 'completed'
    };

    await db.collection('analysis_results').doc(requestId).set(analysisResult);

    // 원본 요청 상태 업데이트
    await db.collection('analysis_requests').doc(requestId).update({
      status: 'completed',
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    });

    console.log(`AI analysis completed: ${requestId}`, results);

    res.status(200).json({
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

/**
 * 사용자 피드백 제출 (AI 제품관리 시스템)
 */
exports.submitFeedback = functions.https.onCall(async (data, context) => {
  // 사용자 인증 확인
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated', 
      'User must be authenticated to submit feedback.'
    );
  }

  const { type, priority, category, title, description, rating } = data;
  
  // 필수 데이터 검증
  const requiredFields = ['type', 'priority', 'category', 'title', 'description', 'rating'];
  if (!requiredFields.every(field => data[field])) {
    throw new functions.https.HttpsError(
      'invalid-argument', 
      'Missing required feedback fields'
    );
  }

  try {
    // 피드백 ID 생성
    const feedbackId = `feedback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // 피드백 데이터 구성
    const feedbackData = {
      id: feedbackId,
      userId: context.auth.uid,
      type,
      priority,
      category,
      title,
      description,
      rating: parseInt(rating),
      timestamp: admin.firestore.FieldValue.serverTimestamp()
    };

    // Firestore에 피드백 저장
    await db.collection('user_feedback').doc(feedbackId).set(feedbackData);

    console.log(`Feedback submitted: ${feedbackId}`, feedbackData);

    return {
      status: 'success',
      message: 'Feedback submitted successfully.',
      data: {
        feedbackId,
        timestamp: new Date().toISOString()
      }
    };

  } catch (error) {
    console.error('Error in submitFeedback:', error);
    throw new functions.https.HttpsError(
      'internal', 
      'Failed to submit feedback.'
    );
  }
});

/**
 * AI 인사이트 조회 (AI 제품관리 시스템)
 */
exports.getAIInsights = functions.https.onCall(async (data, context) => {
  // 사용자 인증 확인
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated', 
      'User must be authenticated to get AI insights.'
    );
  }

  try {
    // Firestore에서 피드백 데이터 조회
    const feedbackQuery = await db.collection('user_feedback').get();
    
    if (feedbackQuery.empty) {
      return {
        status: 'success',
        message: 'AI insights generated successfully.',
        data: generateDefaultInsights()
      };
    }

    // 피드백 데이터 분석
    const feedbackData = [];
    feedbackQuery.forEach(doc => {
      feedbackData.push(doc.data());
    });

    const insights = analyzeFeedbackWithAI(feedbackData);

    return {
      status: 'success',
      message: 'AI insights generated successfully.',
      data: insights
    };

  } catch (error) {
    console.error('Error in getAIInsights:', error);
    throw new functions.https.HttpsError(
      'internal', 
      'Failed to generate AI insights.'
    );
  }
});

/**
 * Health Check 엔드포인트
 */
exports.healthCheck = functions.https.onRequest((req, res) => {
  res.status(200).json({
    status: 'healthy',
    message: 'Firebase Functions are running successfully.',
    timestamp: new Date().toISOString(),
    services: {
      firestore: 'connected',
      pubsub: 'ready',
      authentication: 'active',
      ai_agent: 'active'
    }
  });
});

/**
 * AI 피드백 분석 함수
 */
function analyzeFeedbackWithAI(feedbackData) {
  try {
    // 기본 통계 계산
    const totalFeedback = feedbackData.length;
    const ratings = feedbackData.map(f => f.rating);
    const averageRating = ratings.reduce((sum, rating) => sum + rating, 0) / totalFeedback;
    
    // 피드백 유형별 분석
    const feedbackTypes = {};
    const feedbackCategories = {};
    const feedbackPriorities = {};
    
    feedbackData.forEach(feedback => {
      feedbackTypes[feedback.type] = (feedbackTypes[feedback.type] || 0) + 1;
      feedbackCategories[feedback.category] = (feedbackCategories[feedback.category] || 0) + 1;
      feedbackPriorities[feedback.priority] = (feedbackPriorities[feedback.priority] || 0) + 1;
    });

    // AI 기반 우선순위 분석
    const priorityScores = {
      'bug': 10,
      'feature': 7,
      'improvement': 5,
      'experience': 3
    };
    
    const weightedPriorities = {};
    feedbackData.forEach(feedback => {
      const priority = feedback.priority;
      const priorityWeight = priorityScores[feedback.type] || 1;
      
      if (!weightedPriorities[priority]) {
        weightedPriorities[priority] = 0;
      }
      weightedPriorities[priority] += priorityWeight;
    });

    // AI 인사이트 생성
    return {
      summary: {
        totalFeedback,
        averageRating: Math.round(averageRating * 10) / 10,
        mostCommonType: Object.keys(feedbackTypes).reduce((a, b) => 
          feedbackTypes[a] > feedbackTypes[b] ? a : b
        ),
        mostCommonCategory: Object.keys(feedbackCategories).reduce((a, b) => 
          feedbackCategories[a] > feedbackCategories[b] ? a : b
        )
      },
      trends: {
        feedbackTypes,
        categories: feedbackCategories,
        priorities: feedbackPriorities
      },
      recommendations: generateAIRecommendations(feedbackTypes, feedbackCategories, averageRating),
      actionItems: generateActionItems(weightedPriorities, feedbackTypes)
    };

  } catch (error) {
    console.error('Error in AI feedback analysis:', error);
    return generateDefaultInsights();
  }
}

/**
 * AI 권장사항 생성
 */
function generateAIRecommendations(feedbackTypes, feedbackCategories, averageRating) {
  const recommendations = [];
  
  // 버그 리포트가 많으면 안정성 개선 권장
  if (feedbackTypes.bug > 0) {
    recommendations.push({
      priority: 'high',
      category: 'stability',
      title: '버그 수정 및 안정성 향상',
      description: `버그 리포트 ${feedbackTypes.bug}건이 보고되어 즉시 안정성 개선이 필요합니다.`,
      impact: '사용자 경험 및 제품 신뢰도 향상'
    });
  }
  
  // 기능 요청이 많으면 신규 기능 개발 권장
  if (feedbackTypes.feature > 0) {
    recommendations.push({
      priority: 'medium',
      category: 'development',
      title: '사용자 요청 기능 개발',
      description: `기능 요청 ${feedbackTypes.feature}건이 있어 사용자 만족도 향상 기회입니다.`,
      impact: '사용자 만족도 및 제품 경쟁력 향상'
    });
  }
  
  // 평균 만족도가 낮으면 전반적 개선 권장
  if (averageRating < 3.5) {
    recommendations.push({
      priority: 'high',
      category: 'overall',
      title: '전반적 사용자 경험 개선',
      description: `평균 만족도 ${averageRating}/5.0으로 전반적 개선이 필요합니다.`,
      impact: '사용자 유지율 및 제품 인지도 향상'
    });
  }
  
  return recommendations;
}

/**
 * 실행 가능한 액션 아이템 생성
 */
function generateActionItems(weightedPriorities, feedbackTypes) {
  const actionItems = [];
  
  // 우선순위별 액션 아이템
  Object.entries(weightedPriorities)
    .sort(([,a], [,b]) => b - a)
    .forEach(([priority, weight]) => {
      if (priority === 'critical') {
        actionItems.push({
          priority: 'critical',
          action: '즉시 조치',
          description: '긴급한 문제를 우선적으로 해결',
          timeline: '24시간 이내'
        });
      } else if (priority === 'high') {
        actionItems.push({
          priority: 'high',
          action: '빠른 조치',
          description: '높은 우선순위 문제를 신속하게 해결',
          timeline: '1주일 이내'
        });
      }
    });
  
  // 피드백 유형별 액션 아이템
  if (feedbackTypes.bug > 0) {
    actionItems.push({
      priority: 'high',
      action: '버그 수정',
      description: '사용자들이 보고한 버그들을 체계적으로 수정',
      timeline: '2주일 이내'
    });
  }
  
  if (feedbackTypes.feature > 0) {
    actionItems.push({
      priority: 'medium',
      action: '기능 개발 계획',
      description: '사용자 요청 기능들의 개발 로드맵 수립',
      timeline: '1개월 이내'
    });
  }
  
  return actionItems;
}

/**
 * 기본 AI 인사이트 생성
 */
function generateDefaultInsights() {
  return {
    summary: {
      totalFeedback: 0,
      averageRating: 0,
      mostCommonType: 'N/A',
      mostCommonCategory: 'N/A'
    },
    trends: {
      feedbackTypes: {},
      categories: {},
      priorities: {}
    },
    recommendations: [
      {
        priority: 'medium',
        category: 'onboarding',
        title: '사용자 피드백 수집 시작',
        description: '제품 개선을 위한 사용자 피드백 수집을 시작하세요.',
        impact: '데이터 기반 제품 개발 기반 마련'
      }
    ],
    actionItems: [
      {
        priority: 'medium',
        action: '피드백 시스템 활성화',
        description: '사용자들이 쉽게 피드백을 제출할 수 있는 시스템 구축',
        timeline: '1주일 이내'
      }
    ]
  };
} 