#!/usr/bin/env python3
"""
Test script to check token validation
"""

import requests

def test_token():
    """Test the admin token"""
    token = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
    base_url = "http://localhost:7000"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("🔐 Testing Admin Token")
    print("=" * 40)
    print(f"Token: {token}")
    print()
    
    # Test different endpoints
    endpoints = [
        "/health",
        "/auth/verify", 
        "/auth/tokens"
    ]
    
    for endpoint in endpoints:
        print(f"📡 Testing: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ Success: {response.json()}")
            else:
                print(f"  ❌ Error: {response.text}")
        except Exception as e:
            print(f"  ❌ Exception: {e}")
        print()

if __name__ == "__main__":
    test_token() 