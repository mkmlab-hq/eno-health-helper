#!/usr/bin/env python3
"""
간단한 HTTP 서버 - '최종 연결' API 테스트용 + AI 제품관리
Node.js 의존성 문제를 피하기 위해 Python으로 구현
"""

import json
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import redis
import threading
from collections import Counter
import statistics

# Redis 클라이언트
try:
    redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
    redis_status = "connected"
except:
    redis_client = None
    redis_status = "disconnected"

# 메모리 저장소 (실제로는 Firestore 사용)
analysis_requests = {}
analysis_results = {}
user_feedback = []

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def _set_headers(self, status_code=200):
        """CORS 헤더 설정"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization')
        self.end_headers()
    
    def do_OPTIONS(self):
        """CORS preflight 요청 처리"""
        self._set_headers(200)
    
    def do_GET(self):
        """GET 요청 처리"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/healthCheck':
            self._handle_health_check()
        elif parsed_path.path == '/aiInsights':
            self._handle_get_ai_insights()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                'error': 'Endpoint not found'
            }).encode())
    
    def do_POST(self):
        """POST 요청 처리"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/requestAIAnalysis':
            self._handle_ai_analysis_request()
        elif parsed_path.path == '/getAnalysisResult':
            self._handle_get_analysis_result()
        elif parsed_path.path == '/getUserAnalysisHistory':
            self._handle_get_user_history()
        elif parsed_path.path == '/processAIAnalysis':
            self._handle_process_ai_analysis()
        elif parsed_path.path == '/submitFeedback':
            self._handle_submit_feedback()
        elif parsed_path.path == '/getFeedbackAnalytics':
            self._handle_get_feedback_analytics()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                'error': 'Endpoint not found'
            }).encode())
    
    def _handle_health_check(self):
        """Health Check 엔드포인트"""
        self._set_headers(200)
        response = {
            'status': 'healthy',
            'message': 'Firebase Functions are running successfully.',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'services': {
                'firestore': 'simulated',
                'redis': redis_status,
                'authentication': 'simulated',
                'ai_agent': 'active'
            }
        }
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def _handle_ai_analysis_request(self):
        """AI 분석 요청 처리"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_id = data.get('userId')
            data_type = data.get('dataType')
            data_url = data.get('dataUrl')
            
            # 필수 데이터 검증
            if not all([user_id, data_type, data_url]):
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Missing required data: userId, dataType, dataUrl'
                }).encode())
                return
            
            # 요청 ID 생성
            request_id = f"analysis_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            
            # 분석 요청 정보를 메모리에 저장
            analysis_requests[request_id] = {
                'requestId': request_id,
                'userId': user_id,
                'dataType': data_type,
                'dataUrl': data_url,
                'status': 'pending',
                'createdAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'updatedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
            
            # Redis에 Pub/Sub 메시지 발행 (비동기 처리)
            if redis_client:
                message = {
                    'requestId': request_id,
                    'userId': user_id,
                    'dataType': data_type,
                    'dataUrl': data_url,
                    'timestamp': int(time.time())
                }
                redis_client.publish('ai-analysis-requests', json.dumps(message))
            
            # 로그 기록
            print(f"AI analysis request submitted: {request_id}", {
                'userId': user_id,
                'dataType': data_type,
                'dataUrl': data_url
            })
            
            self._set_headers(200)
            response = {
                'status': 'success',
                'message': 'Analysis request submitted successfully.',
                'data': {
                    'requestId': request_id,
                    'status': 'pending',
                    'estimatedTime': '2-5 minutes'
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"Error in requestAIAnalysis: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': 'Internal server error occurred.'
            }).encode())
    
    def _handle_get_analysis_result(self):
        """AI 분석 결과 조회"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            request_id = data.get('requestId')
            
            if not request_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Missing requestId'
                }).encode())
                return
            
            # 메모리에서 분석 결과 조회
            result = analysis_results.get(request_id)
            
            if not result:
                self._set_headers(200)
                response = {
                    'status': 'pending',
                    'message': 'Analysis is still in progress.',
                    'data': None
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                return
            
            self._set_headers(200)
            response = {
                'status': 'success',
                'message': 'Analysis result retrieved successfully.',
                'data': result
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"Error in getAnalysisResult: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': 'Internal server error occurred.'
            }).encode())
    
    def _handle_get_user_history(self):
        """사용자 분석 히스토리 조회"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_id = data.get('userId')
            limit = data.get('limit', 10)
            
            if not user_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Missing userId'
                }).encode())
                return
            
            # 메모리에서 사용자의 분석 히스토리 조회
            history = [
                request for request in analysis_requests.values()
                if request['userId'] == user_id
            ]
            
            # 생성 시간 기준으로 정렬하고 제한
            history.sort(key=lambda x: x['createdAt'], reverse=True)
            history = history[:limit]
            
            self._set_headers(200)
            response = {
                'status': 'success',
                'message': 'Analysis history retrieved successfully.',
                'data': {
                    'history': history,
                    'total': len(history)
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"Error in getUserAnalysisHistory: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': 'Internal server error occurred.'
            }).encode())
    
    def _handle_process_ai_analysis(self):
        """AI 분석 결과 처리 (AI 엔진 연동용)"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            request_id = data.get('requestId')
            results = data.get('results')
            
            if not all([request_id, results]):
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Missing required data: requestId, results'
                }).encode())
                return
            
            # 분석 결과를 메모리에 저장
            analysis_results[request_id] = {
                'requestId': request_id,
                'results': results,
                'completedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'status': 'completed'
            }
            
            # 원본 요청 상태 업데이트
            if request_id in analysis_requests:
                analysis_requests[request_id]['status'] = 'completed'
                analysis_requests[request_id]['updatedAt'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            
            print(f"AI analysis completed: {request_id}", results)
            
            self._set_headers(200)
            response = {
                'status': 'success',
                'message': 'Analysis result saved successfully.'
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"Error in processAIAnalysis: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': 'Internal server error occurred.'
            }).encode())

    def _handle_submit_feedback(self):
        """사용자 피드백 제출"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            feedback_data = json.loads(post_data.decode('utf-8'))
            
            # 필수 데이터 검증
            required_fields = ['type', 'priority', 'category', 'title', 'description', 'rating']
            if not all(field in feedback_data for field in required_fields):
                self._set_headers(400)
                self.wfile.write(json.dumps({
                    'error': 'Missing required feedback fields'
                }).encode())
                return
            
            # 피드백 ID 생성
            feedback_id = f"feedback_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            feedback_data['id'] = feedback_id
            feedback_data['timestamp'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            
            # 메모리에 피드백 저장
            user_feedback.append(feedback_data)
            
            # Redis에 피드백 저장 (실제로는 Firestore 사용)
            if redis_client:
                redis_client.set(f"feedback:{feedback_id}", json.dumps(feedback_data))
            
            print(f"Feedback submitted: {feedback_id}", feedback_data)
            
            self._set_headers(200)
            response = {
                'status': 'success',
                'message': 'Feedback submitted successfully.',
                'data': {
                    'feedbackId': feedback_id,
                    'timestamp': feedback_data['timestamp']
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"Error in submitFeedback: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': 'Internal server error occurred.'
            }).encode())

    def _handle_get_feedback_analytics(self):
        """피드백 분석 데이터 조회"""
        try:
            if not user_feedback:
                self._set_headers(200)
                response = {
                    'status': 'success',
                    'message': 'No feedback data available.',
                    'data': {
                        'totalFeedback': 0,
                        'analytics': {}
                    }
                }
                self.wfile.write(json.dumps(response, indent=2).encode())
                return
            
            # AI 에이전트가 피드백 분석
            analytics = self._analyze_feedback_with_ai()
            
            self._set_headers(200)
            response = {
                'status': 'success',
                'message': 'Feedback analytics generated successfully.',
                'data': {
                    'totalFeedback': len(user_feedback),
                    'analytics': analytics
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"Error in getFeedbackAnalytics: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': 'Internal server error occurred.'
            }).encode())

    def _handle_get_ai_insights(self):
        """AI 인사이트 조회"""
        try:
            if not user_feedback:
                insights = self._generate_default_insights()
            else:
                insights = self._analyze_feedback_with_ai()
            
            self._set_headers(200)
            response = {
                'status': 'success',
                'message': 'AI insights generated successfully.',
                'data': insights
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            print(f"Error in getAIInsights: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({
                'error': 'Internal server error occurred.'
            }).encode())

    def _analyze_feedback_with_ai(self):
        """AI 에이전트가 피드백을 분석하여 인사이트 생성"""
        try:
            # 기본 통계 계산
            total_feedback = len(user_feedback)
            ratings = [f['rating'] for f in user_feedback]
            average_rating = statistics.mean(ratings) if ratings else 0
            
            # 피드백 유형별 분석
            feedback_types = Counter([f['type'] for f in user_feedback])
            feedback_categories = Counter([f['category'] for f in user_feedback])
            feedback_priorities = Counter([f['priority'] for f in user_feedback])
            
            # AI 기반 우선순위 분석
            priority_scores = {
                'bug': 10,
                'feature': 7,
                'improvement': 5,
                'experience': 3
            }
            
            weighted_priorities = {}
            for feedback in user_feedback:
                feedback_type = feedback['type']
                priority = feedback['priority']
                priority_weight = priority_scores.get(feedback_type, 1)
                
                if priority not in weighted_priorities:
                    weighted_priorities[priority] = 0
                weighted_priorities[priority] += priority_weight
            
            # AI 인사이트 생성
            insights = {
                'summary': {
                    'totalFeedback': total_feedback,
                    'averageRating': round(average_rating, 1),
                    'mostCommonType': feedback_types.most_common(1)[0][0] if feedback_types else 'N/A',
                    'mostCommonCategory': feedback_categories.most_common(1)[0][0] if feedback_categories else 'N/A'
                },
                'trends': {
                    'feedbackTypes': dict(feedback_types),
                    'categories': dict(feedback_categories),
                    'priorities': dict(feedback_priorities)
                },
                'recommendations': self._generate_ai_recommendations(
                    feedback_types, feedback_categories, average_rating
                ),
                'actionItems': self._generate_action_items(weighted_priorities, feedback_types)
            }
            
            return insights
            
        except Exception as e:
            print(f"Error in AI feedback analysis: {e}")
            return self._generate_default_insights()

    def _generate_ai_recommendations(self, feedback_types, feedback_categories, average_rating):
        """AI 기반 제품 개선 권장사항 생성"""
        recommendations = []
        
        # 버그 리포트가 많으면 안정성 개선 권장
        if feedback_types.get('bug', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'stability',
                'title': '버그 수정 및 안정성 향상',
                'description': f'버그 리포트 {feedback_types["bug"]}건이 보고되어 즉시 안정성 개선이 필요합니다.',
                'impact': '사용자 경험 및 제품 신뢰도 향상'
            })
        
        # 기능 요청이 많으면 신규 기능 개발 권장
        if feedback_types.get('feature', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'development',
                'title': '사용자 요청 기능 개발',
                'description': f'기능 요청 {feedback_types["feature"]}건이 있어 사용자 만족도 향상 기회입니다.',
                'impact': '사용자 만족도 및 제품 경쟁력 향상'
            })
        
        # 평균 만족도가 낮으면 전반적 개선 권장
        if average_rating < 3.5:
            recommendations.append({
                'priority': 'high',
                'category': 'overall',
                'title': '전반적 사용자 경험 개선',
                'description': f'평균 만족도 {average_rating}/5.0으로 전반적 개선이 필요합니다.',
                'impact': '사용자 유지율 및 제품 인지도 향상'
            })
        
        # 카테고리별 개선 권장사항
        if feedback_categories.get('ui', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': 'ui',
                'title': '사용자 인터페이스 개선',
                'description': 'UI 관련 피드백이 있어 사용성 향상이 필요합니다.',
                'impact': '사용자 접근성 및 작업 효율성 향상'
            })
        
        return recommendations

    def _generate_action_items(self, weighted_priorities, feedback_types):
        """실행 가능한 액션 아이템 생성"""
        action_items = []
        
        # 우선순위별 액션 아이템
        for priority, weight in sorted(weighted_priorities.items(), key=lambda x: x[1], reverse=True):
            if priority == 'critical':
                action_items.append({
                    'priority': 'critical',
                    'action': '즉시 조치',
                    'description': '긴급한 문제를 우선적으로 해결',
                    'timeline': '24시간 이내'
                })
            elif priority == 'high':
                action_items.append({
                    'priority': 'high',
                    'action': '빠른 조치',
                    'description': '높은 우선순위 문제를 신속하게 해결',
                    'timeline': '1주일 이내'
                })
        
        # 피드백 유형별 액션 아이템
        if feedback_types.get('bug', 0) > 0:
            action_items.append({
                'priority': 'high',
                'action': '버그 수정',
                'description': '사용자들이 보고한 버그들을 체계적으로 수정',
                'timeline': '2주일 이내'
            })
        
        if feedback_types.get('feature', 0) > 0:
            action_items.append({
                'priority': 'medium',
                'action': '기능 개발 계획',
                'description': '사용자 요청 기능들의 개발 로드맵 수립',
                'timeline': '1개월 이내'
            })
        
        return action_items

    def _generate_default_insights(self):
        """기본 AI 인사이트 생성 (피드백 데이터가 없을 때)"""
        return {
            'summary': {
                'totalFeedback': 0,
                'averageRating': 0,
                'mostCommonType': 'N/A',
                'mostCommonCategory': 'N/A'
            },
            'trends': {
                'feedbackTypes': {},
                'categories': {},
                'priorities': {}
            },
            'recommendations': [
                {
                    'priority': 'medium',
                    'category': 'onboarding',
                    'title': '사용자 피드백 수집 시작',
                    'description': '제품 개선을 위한 사용자 피드백 수집을 시작하세요.',
                    'impact': '데이터 기반 제품 개발 기반 마련'
                }
            ],
            'actionItems': [
                {
                    'priority': 'medium',
                    'action': '피드백 시스템 활성화',
                    'description': '사용자들이 쉽게 피드백을 제출할 수 있는 시스템 구축',
                    'timeline': '1주일 이내'
                }
            ]
        }

def run_server(port=5001):
    """서버 실행"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"�� Firebase Functions 서버가 포트 {port}에서 실행 중입니다.")
    print(f"📡 Redis 연결 상태: {redis_status}")
    print(f"🔗 Health Check: http://localhost:{port}/healthCheck")
    print(f"🤖 AI 제품관리 시스템이 활성화되었습니다.")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server() 