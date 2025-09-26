#!/usr/bin/env python3
"""
간단한 HTTP 연결 테스트
서버 연결 상태를 확인합니다.
"""

import requests
import json

def test_server_connection():
    """서버 연결 테스트"""
    base_url = "http://127.0.0.1:8002"
    
    print("🔍 서버 연결 테스트 시작...")
    
    try:
        # 헬스체크 테스트
        print(f"📡 {base_url}/api/v1/health 연결 시도...")
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        
        print(f"✅ 응답 상태: {response.status_code}")
        print(f"📊 응답 내용: {response.text}")
        
        if response.status_code == 200:
            print("🎉 서버 연결 성공!")
            return True
        else:
            print(f"⚠️ 서버 응답 오류: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패: Connection refused")
        return False
    except requests.exceptions.Timeout:
        print("❌ 서버 응답 시간 초과")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        return False

if __name__ == "__main__":
    test_server_connection()
