#!/usr/bin/env python3
"""
Health Check Script for Image Moderation API
Monitors all services and provides detailed status reports
"""

import requests
import time
import sys
import json
from typing import Dict, List, Tuple

# Configuration
API_BASE_URL = "http://localhost:7000"
FRONTEND_URL = "http://localhost:3000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
TIMEOUT = 10

class HealthChecker:
    def __init__(self):
        self.results = []
        self.all_healthy = True
    
    def check_api_health(self) -> Tuple[bool, str]:
        """Check API health endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    return True, f"API healthy (response: {response.elapsed.total_seconds():.2f}s)"
                else:
                    return False, f"API unhealthy: {data}"
            else:
                return False, f"API returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "API connection failed - service may be down"
        except requests.exceptions.Timeout:
            return False, "API timeout - service may be overloaded"
        except Exception as e:
            return False, f"API check failed: {str(e)}"
    
    def check_authentication(self) -> Tuple[bool, str]:
        """Check authentication system"""
        try:
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            response = requests.get(f"{API_BASE_URL}/auth/tokens", headers=headers, timeout=TIMEOUT)
            if response.status_code == 200:
                tokens = response.json()
                return True, f"Authentication working ({len(tokens)} tokens active)"
            else:
                return False, f"Authentication failed: status {response.status_code}"
        except Exception as e:
            return False, f"Authentication check failed: {str(e)}"
    
    def check_moderation_endpoint(self) -> Tuple[bool, str]:
        """Check if moderation endpoint is accessible"""
        try:
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            # Test without file (should return 422, not 500)
            response = requests.post(f"{API_BASE_URL}/moderate", headers=headers, timeout=TIMEOUT)
            if response.status_code == 422:
                return True, "Moderation endpoint accessible (validation working)"
            elif response.status_code == 401:
                return False, "Moderation endpoint: authentication failed"
            else:
                return False, f"Moderation endpoint unexpected response: {response.status_code}"
        except Exception as e:
            return False, f"Moderation endpoint check failed: {str(e)}"
    
    def check_frontend(self) -> Tuple[bool, str]:
        """Check frontend accessibility"""
        try:
            response = requests.get(FRONTEND_URL, timeout=TIMEOUT)
            if response.status_code == 200:
                if "Image Moderation" in response.text or "react" in response.text.lower():
                    return True, f"Frontend accessible (response: {response.elapsed.total_seconds():.2f}s)"
                else:
                    return False, "Frontend accessible but content unexpected"
            else:
                return False, f"Frontend returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Frontend connection failed - service may be down"
        except requests.exceptions.Timeout:
            return False, "Frontend timeout - service may be overloaded"
        except Exception as e:
            return False, f"Frontend check failed: {str(e)}"
    
    def check_ai_detection(self) -> Tuple[bool, str]:
        """Test AI detection with a simple image"""
        try:
            # Create a simple test image (1x1 pixel)
            from PIL import Image
            import io
            
            # Create a small blue image
            img = Image.new('RGB', (10, 10), color='blue')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            files = {"file": ("test.jpg", img_bytes, "image/jpeg")}
            
            response = requests.post(f"{API_BASE_URL}/moderate", 
                                   headers=headers, files=files, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                if "categories" in result and len(result["categories"]) >= 2:
                    nudity_conf = next((cat["confidence"] for cat in result["categories"] 
                                      if cat["category"] == "nudity"), None)
                    drugs_conf = next((cat["confidence"] for cat in result["categories"] 
                                     if cat["category"] == "drugs"), None)
                    
                    if nudity_conf is not None and drugs_conf is not None:
                        return True, f"AI detection working (nudity: {nudity_conf:.3f}, drugs: {drugs_conf:.3f})"
                    else:
                        return False, "AI detection: missing expected categories"
                else:
                    return False, f"AI detection: unexpected response format: {result}"
            else:
                return False, f"AI detection failed: status {response.status_code}"
        except ImportError:
            return False, "AI detection check skipped: Pillow not available"
        except Exception as e:
            return False, f"AI detection check failed: {str(e)}"
    
    def run_check(self, name: str, check_func) -> None:
        """Run a single health check"""
        print(f"🔍 Checking {name}...", end=" ")
        try:
            success, message = check_func()
            if success:
                print(f"✅ {message}")
                self.results.append({"name": name, "status": "healthy", "message": message})
            else:
                print(f"❌ {message}")
                self.results.append({"name": name, "status": "unhealthy", "message": message})
                self.all_healthy = False
        except Exception as e:
            error_msg = f"Check failed with error: {str(e)}"
            print(f"💥 {error_msg}")
            self.results.append({"name": name, "status": "error", "message": error_msg})
            self.all_healthy = False
    
    def run_all_checks(self) -> Dict:
        """Run all health checks"""
        print("🏥 Image Moderation API - Health Check")
        print("=" * 50)
        
        # Core system checks
        self.run_check("API Health", self.check_api_health)
        self.run_check("Authentication", self.check_authentication)
        self.run_check("Moderation Endpoint", self.check_moderation_endpoint)
        self.run_check("Frontend", self.check_frontend)
        self.run_check("AI Detection", self.check_ai_detection)
        
        print("\n" + "=" * 50)
        
        # Summary
        healthy_count = len([r for r in self.results if r["status"] == "healthy"])
        total_count = len(self.results)
        
        if self.all_healthy:
            print(f"🎉 All systems healthy! ({healthy_count}/{total_count})")
            print("\n🔗 Access URLs:")
            print(f"   • API: {API_BASE_URL}")
            print(f"   • Frontend: {FRONTEND_URL}")
            print(f"   • API Docs: {API_BASE_URL}/docs")
        else:
            print(f"⚠️  System issues detected ({healthy_count}/{total_count} healthy)")
            print("\n🔧 Failed checks:")
            for result in self.results:
                if result["status"] != "healthy":
                    print(f"   • {result['name']}: {result['message']}")
        
        return {
            "timestamp": time.time(),
            "all_healthy": self.all_healthy,
            "summary": f"{healthy_count}/{total_count} checks passed",
            "results": self.results
        }

def main():
    """Main health check execution"""
    checker = HealthChecker()
    
    # Check if we should output JSON
    json_output = "--json" in sys.argv
    
    try:
        result = checker.run_all_checks()
        
        if json_output:
            print(json.dumps(result, indent=2))
        
        # Exit with appropriate code
        sys.exit(0 if result["all_healthy"] else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚡ Health check interrupted")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Health check failed with error: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    main() 