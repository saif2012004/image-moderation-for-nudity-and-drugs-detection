#!/usr/bin/env python3
"""
Debug script to test the exact same API calls the frontend makes
"""

import requests

def debug_frontend_calls():
    """Test the exact API calls the frontend makes"""
    token = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
    base_url = "http://localhost:7000"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("🔍 Debugging Frontend API Calls")
    print("=" * 50)
    print(f"Token: {token}")
    print(f"Base URL: {base_url}")
    print()
    
    # Test 1: Health check (should work)
    print("1️⃣ Testing Health Check")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Success: {response.json()}")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    # Test 2: Fetch tokens (what frontend does on login)
    print("2️⃣ Testing Fetch Tokens (Frontend Login Check)")
    try:
        response = requests.get(f"{base_url}/auth/tokens", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            tokens = response.json()
            print(f"   ✅ Success: Found {len(tokens)} tokens")
            for t in tokens:
                admin_status = "(Admin)" if t.get('isAdmin') else "(User)"
                print(f"   - {t['token'][:16]}... {admin_status}")
        else:
            print(f"   ❌ Error: {response.text}")
            print(f"   This might be why frontend shows 'invalid token'")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    # Test 3: Create token (what frontend does when creating tokens)
    print("3️⃣ Testing Create Token")
    try:
        data = {"isAdmin": False}
        response = requests.post(f"{base_url}/auth/tokens", 
                               json=data, 
                               headers=headers,
                               params={"isAdmin": False})
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success: Created token {result['token'][:16]}...")
        else:
            print(f"   ❌ Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    # Test 4: CORS check
    print("4️⃣ Testing CORS Headers")
    try:
        response = requests.options(f"{base_url}/auth/tokens", headers=headers)
        print(f"   Status: {response.status_code}")
        print(f"   CORS Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()
    
    print("🎯 Diagnosis:")
    print("- If test 1 works: API is running")
    print("- If test 2 fails: Token validation issue")
    print("- If test 3 fails: Admin permission issue")
    print("- If test 4 fails: CORS issue")

if __name__ == "__main__":
    debug_frontend_calls() 