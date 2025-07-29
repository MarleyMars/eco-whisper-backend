#!/usr/bin/env python3
"""
Test script for Railway deployment
Run this after deploying to verify the API is working correctly
"""

import requests
import json
import sys

def test_health_check(base_url):
    """Test the health check endpoint"""
    try:
        response = requests.get(f"{base_url}/")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"Health check error: {e}")
        return False

def test_text_ask(base_url):
    """Test the text ask endpoint"""
    try:
        data = {
            'text': 'How much electricity did I use today?',
            'user_id': 'test_user_123'
        }
        response = requests.post(f"{base_url}/api/text_ask", data=data)
        print(f"Text ask status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"Text ask failed: {response.text}")
            return False
    except Exception as e:
        print(f"Text ask error: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <base_url>")
        print("Example: python test_deployment.py https://eco-whisper-backend.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    print(f"Testing deployment at: {base_url}")
    print("-" * 50)
    
    # Test health check
    print("1. Testing health check...")
    health_ok = test_health_check(base_url)
    print()
    
    # Test text ask
    print("2. Testing text ask endpoint...")
    text_ok = test_text_ask(base_url)
    print()
    
    # Summary
    print("=" * 50)
    print("DEPLOYMENT TEST RESULTS:")
    print(f"Health check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Text ask: {'✅ PASS' if text_ok else '❌ FAIL'}")
    
    if health_ok and text_ok:
        print("\n🎉 Deployment is working correctly!")
        print("You can now update your frontend API configuration.")
    else:
        print("\n⚠️  Some tests failed. Please check the deployment.")

if __name__ == "__main__":
    main()