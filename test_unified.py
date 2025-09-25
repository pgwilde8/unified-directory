#!/usr/bin/env python3
"""
Test script for unified directory platform
"""
import os
import sys
import requests
import time

def test_unified_system():
    """Test the unified system on port 9180"""
    base_url = "http://localhost:9180"
    
    print("🚀 Testing Unified Business Directory Platform")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint: OK")
            data = response.json()
            print(f"   Version: {data.get('version')}")
            print(f"   Port: {data.get('features', {}).get('port')}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint: OK")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Port: {data.get('port')}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test system info
    try:
        response = requests.get(f"{base_url}/info")
        if response.status_code == 200:
            print("✅ System info endpoint: OK")
            data = response.json()
            print(f"   System: {data.get('system')}")
            print(f"   Authentication: {data.get('authentication')}")
        else:
            print(f"❌ System info failed: {response.status_code}")
    except Exception as e:
        print(f"❌ System info error: {e}")
    
    # Test API docs
    try:
        response = requests.get(f"{base_url}/api/docs")
        if response.status_code == 200:
            print("✅ API docs: Accessible")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")
    
    print("-" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_unified_system()