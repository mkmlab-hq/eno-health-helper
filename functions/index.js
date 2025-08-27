const functions = require('firebase-functions');
const admin = require('firebase-admin');

// Firebase Admin 초기화
admin.initializeApp();

// Firestore 데이터베이스
const db = admin.firestore();

/**
 * AI 분석 요청 처리 - '최종 연결' 핵심 기능
 * 사용자 인증을 강제하고 비동기 처리
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
      userId: context.auth.uid,
      dataType,
      dataUrl,
      status: 'pending',
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    };

    await db.collection('analysis_requests').doc(requestId).set(analysisRequest);

    console.log(`AI analysis request submitted: ${requestId}`, {
      userId: context.auth.uid,
      dataType,
      dataUrl
    });

    return {
      status: 'success',
      message: 'Analysis request submitted successfully.',
      data: {
        requestId,
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
 * 사용자 피드백 제출 (AI 제품관리 시스템)
 */
exports.submitFeedback = functions.https.onCall(async (data, context) => {
  if (!context.auth) {
    throw new functions.https.HttpsError(
      'unauthenticated', 
      'User must be authenticated to submit feedback.'
    );
  }

  const { type, priority, category, title, description, rating } = data;
  
  const requiredFields = ['type', 'priority', 'category', 'title', 'description', 'rating'];
  if (!requiredFields.every(field => data[field])) {
    throw new functions.https.HttpsError(
      'invalid-argument', 
      'Missing required feedback fields'
    );
  }

  try {
    const feedbackId = `feedback_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
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