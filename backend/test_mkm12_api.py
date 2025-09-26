#!/usr/bin/env python3
"""
MKM12 API Test Script

This script tests the MKM12 API endpoints to ensure they are working correctly.
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"
MKM12_BASE = f"{BASE_URL}/api/v1/mkm12"

def test_mkm12_status():
    """Test MKM12 API status endpoint."""
    print("🧪 Testing MKM12 API Status...")
    
    try:
        response = requests.get(f"{MKM12_BASE}/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {data['status']}")
            print(f"✅ Version: {data['version']}")
            print(f"✅ Capabilities: {len(data['capabilities'])} features")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False


def test_mkm12_health():
    """Test MKM12 API health endpoint."""
    print("\n🧪 Testing MKM12 API Health...")
    
    try:
        response = requests.get(f"{MKM12_BASE}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health: {data['status']}")
            print(f"✅ MKM12 Available: {data['mkm12_available']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def test_persona_analysis():
    """Test MKM12 persona analysis endpoint."""
    print("\n🧪 Testing MKM12 Persona Analysis...")
    
    # Sample biometric data
    biometric_data = {
        "heart_rate": 75.0,
        "heart_rate_variability": 45.0,
        "voice_amplitude": 0.7,
        "voice_frequency": 180.0,
        "breathing_rate": 16.0,
        "stress_level": 0.3
    }
    
    request_data = {
        "biometric_data": biometric_data,
        "temperature": 1.0,
        "user_id": "test_user_001"
    }
    
    try:
        response = requests.post(
            f"{MKM12_BASE}/analyze/persona",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print("✅ Persona analysis successful")
                print(f"✅ Forces: {data['forces']}")
                print(f"✅ Personas: {data['personas']}")
                print(f"✅ Dominant: {data['analysis']['dominant_persona']}")
                print(f"✅ Fingerprint: {data['digital_fingerprint'][:16]}...")
                return True
            else:
                print(f"❌ Analysis failed: {data['error']}")
                return False
        else:
            print(f"❌ Analysis request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False


def test_digital_fingerprint():
    """Test MKM12 digital fingerprint generation endpoint."""
    print("\n🧪 Testing MKM12 Digital Fingerprint Generation...")
    
    # Sample MKM12 data
    request_data = {
        "forces": [0.6, 0.7, 0.4, 0.3],
        "personas": [0.5, 0.3, 0.2],
        "user_id": "test_user_001"
    }
    
    try:
        response = requests.post(
            f"{MKM12_BASE}/generate/digital-fingerprint",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print("✅ Digital fingerprint generation successful")
                print(f"✅ Hash: {data['fingerprint_hash'][:16]}...")
                print(f"✅ Pattern length: {len(data['pattern_data'])}")
                print(f"✅ Metadata: {data['metadata']['version']}")
                return True
            else:
                print(f"❌ Generation failed: {data['error']}")
                return False
        else:
            print(f"❌ Generation request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False


def test_personalized_advice():
    """Test MKM12 personalized advice endpoint."""
    print("\n🧪 Testing MKM12 Personalized Advice...")
    
    # Sample MKM12 data
    request_data = {
        "forces": [0.6, 0.7, 0.4, 0.3],
        "personas": [0.5, 0.3, 0.2],
        "language": "ko",
        "context": "Daily wellness check"
    }
    
    try:
        response = requests.post(
            f"{MKM12_BASE}/get/personalized-advice",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print("✅ Personalized advice generation successful")
                print(f"✅ Title: {data['advice']['title']}")
                print(f"✅ Recommendations: {len(data['recommendations'])} items")
                print(f"✅ Assessment: {data['overall_assessment'][:50]}...")
                return True
            else:
                print(f"❌ Advice generation failed: {data['error']}")
                return False
        else:
            print(f"❌ Advice request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Advice generation error: {e}")
        return False


def test_mkm12_info():
    """Test MKM12 theory information endpoint."""
    print("\n🧪 Testing MKM12 Theory Information...")
    
    try:
        response = requests.get(f"{BASE_URL}/mkm12-info")
        if response.status_code == 200:
            data = response.json()
            print("✅ MKM12 theory information retrieved")
            print(f"✅ Theory: {data['theory']}")
            print(f"✅ Forces: {len(data['forces'])} types")
            print(f"✅ Modes: {len(data['modes'])} types")
            print(f"✅ API Endpoints: {len(data['api_endpoints'])} available")
            return True
        else:
            print(f"❌ Info retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Info retrieval error: {e}")
        return False


def test_error_handling():
    """Test MKM12 API error handling."""
    print("\n🧪 Testing MKM12 API Error Handling...")
    
    # Test with invalid data
    invalid_data = {
        "forces": [0.5, 0.6],  # Wrong number of forces
        "personas": [0.4, 0.3, 0.3]
    }
    
    try:
        response = requests.post(
            f"{MKM12_BASE}/generate/digital-fingerprint",
            json=invalid_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 422:  # Validation error
            print("✅ Invalid data properly rejected")
            return True
        else:
            print(f"❌ Expected validation error, got: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 MKM12 API Test Suite")
    print("=" * 50)
    print(f"Testing API at: {BASE_URL}")
    print("Make sure the backend server is running!")
    print()
    
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        test_mkm12_status,
        test_mkm12_health,
        test_persona_analysis,
        test_digital_fingerprint,
        test_personalized_advice,
        test_mkm12_info,
        test_error_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All MKM12 API tests passed! The API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
