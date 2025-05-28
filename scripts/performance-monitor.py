#!/usr/bin/env python3
"""
Performance Monitor for Image Moderation API
Tracks response times, throughput, and system performance
"""

import requests
import time
import statistics
import concurrent.futures
import sys
from typing import List, Dict
from PIL import Image
import io

# Configuration
API_BASE_URL = "http://localhost:7000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
TEST_ITERATIONS = 10
CONCURRENT_REQUESTS = 5

class PerformanceMonitor:
    def __init__(self):
        self.results = {
            "health_check": [],
            "auth_check": [],
            "moderation": [],
            "concurrent": []
        }
    
    def create_test_image(self, size=(100, 100), color='blue') -> io.BytesIO:
        """Create a test image for performance testing"""
        img = Image.new('RGB', size, color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        return img_bytes
    
    def test_health_endpoint(self) -> float:
        """Test health endpoint response time"""
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            end_time = time.time()
            if response.status_code == 200:
                return end_time - start_time
            else:
                return -1  # Error indicator
        except Exception:
            return -1
    
    def test_auth_endpoint(self) -> float:
        """Test authentication endpoint response time"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            response = requests.get(f"{API_BASE_URL}/auth/tokens", headers=headers, timeout=10)
            end_time = time.time()
            if response.status_code == 200:
                return end_time - start_time
            else:
                return -1
        except Exception:
            return -1
    
    def test_moderation_endpoint(self) -> float:
        """Test moderation endpoint response time with real image"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            img_data = self.create_test_image()
            files = {"file": ("test.jpg", img_data, "image/jpeg")}
            
            response = requests.post(f"{API_BASE_URL}/moderate", 
                                   headers=headers, files=files, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                return end_time - start_time
            else:
                return -1
        except Exception:
            return -1
    
    def test_concurrent_requests(self, num_requests=5) -> List[float]:
        """Test concurrent moderation requests"""
        def single_request():
            return self.test_moderation_endpoint()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(single_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return [r for r in results if r > 0]  # Filter out errors
    
    def run_performance_tests(self):
        """Run all performance tests"""
        print("🚀 Image Moderation API - Performance Monitor")
        print("=" * 60)
        
        # Test 1: Health Endpoint
        print(f"🔍 Testing health endpoint ({TEST_ITERATIONS} iterations)...")
        for i in range(TEST_ITERATIONS):
            result = self.test_health_endpoint()
            if result > 0:
                self.results["health_check"].append(result)
            print(f"   Iteration {i+1}: {result:.3f}s" if result > 0 else f"   Iteration {i+1}: ERROR")
        
        # Test 2: Authentication Endpoint
        print(f"\n🔐 Testing authentication endpoint ({TEST_ITERATIONS} iterations)...")
        for i in range(TEST_ITERATIONS):
            result = self.test_auth_endpoint()
            if result > 0:
                self.results["auth_check"].append(result)
            print(f"   Iteration {i+1}: {result:.3f}s" if result > 0 else f"   Iteration {i+1}: ERROR")
        
        # Test 3: Moderation Endpoint (AI Processing)
        print(f"\n🤖 Testing AI moderation endpoint ({TEST_ITERATIONS} iterations)...")
        for i in range(TEST_ITERATIONS):
            result = self.test_moderation_endpoint()
            if result > 0:
                self.results["moderation"].append(result)
            print(f"   Iteration {i+1}: {result:.3f}s" if result > 0 else f"   Iteration {i+1}: ERROR")
        
        # Test 4: Concurrent Requests
        print(f"\n⚡ Testing concurrent requests ({CONCURRENT_REQUESTS} simultaneous)...")
        concurrent_results = self.test_concurrent_requests(CONCURRENT_REQUESTS)
        self.results["concurrent"] = concurrent_results
        for i, result in enumerate(concurrent_results):
            print(f"   Request {i+1}: {result:.3f}s")
        
        # Display Results
        self.display_results()
    
    def calculate_stats(self, times: List[float]) -> Dict:
        """Calculate statistics for a list of response times"""
        if not times:
            return {"error": "No successful requests"}
        
        return {
            "count": len(times),
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "total_time": sum(times),
            "requests_per_second": len(times) / sum(times) if sum(times) > 0 else 0
        }
    
    def display_results(self):
        """Display performance test results"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE RESULTS")
        print("=" * 60)
        
        # Health Check Results
        health_stats = self.calculate_stats(self.results["health_check"])
        print("\n🔍 Health Endpoint:")
        if "error" not in health_stats:
            print(f"   • Requests: {health_stats['count']}")
            print(f"   • Average: {health_stats['mean']:.3f}s")
            print(f"   • Median:  {health_stats['median']:.3f}s")
            print(f"   • Min/Max: {health_stats['min']:.3f}s / {health_stats['max']:.3f}s")
            print(f"   • RPS:     {health_stats['requests_per_second']:.1f}")
        else:
            print("   ❌ All requests failed")
        
        # Authentication Results
        auth_stats = self.calculate_stats(self.results["auth_check"])
        print("\n🔐 Authentication Endpoint:")
        if "error" not in auth_stats:
            print(f"   • Requests: {auth_stats['count']}")
            print(f"   • Average: {auth_stats['mean']:.3f}s")
            print(f"   • Median:  {auth_stats['median']:.3f}s")
            print(f"   • Min/Max: {auth_stats['min']:.3f}s / {auth_stats['max']:.3f}s")
            print(f"   • RPS:     {auth_stats['requests_per_second']:.1f}")
        else:
            print("   ❌ All requests failed")
        
        # Moderation Results
        mod_stats = self.calculate_stats(self.results["moderation"])
        print("\n🤖 AI Moderation Endpoint:")
        if "error" not in mod_stats:
            print(f"   • Requests: {mod_stats['count']}")
            print(f"   • Average: {mod_stats['mean']:.3f}s")
            print(f"   • Median:  {mod_stats['median']:.3f}s")
            print(f"   • Min/Max: {mod_stats['min']:.3f}s / {mod_stats['max']:.3f}s")
            print(f"   • RPS:     {mod_stats['requests_per_second']:.1f}")
        else:
            print("   ❌ All requests failed")
        
        # Concurrent Results
        concurrent_stats = self.calculate_stats(self.results["concurrent"])
        print("\n⚡ Concurrent Requests:")
        if "error" not in concurrent_stats:
            print(f"   • Requests: {concurrent_stats['count']}/{CONCURRENT_REQUESTS}")
            print(f"   • Average: {concurrent_stats['mean']:.3f}s")
            print(f"   • Median:  {concurrent_stats['median']:.3f}s")
            print(f"   • Min/Max: {concurrent_stats['min']:.3f}s / {concurrent_stats['max']:.3f}s")
            print(f"   • Throughput: {len(self.results['concurrent']) / max(self.results['concurrent']):.1f} req/s")
        else:
            print("   ❌ All concurrent requests failed")
        
        # Overall Assessment
        print("\n🎯 PERFORMANCE ASSESSMENT:")
        
        if mod_stats.get("mean", 0) > 0:
            if mod_stats["mean"] < 2.0:
                print("   ✅ Excellent performance (< 2s per AI request)")
            elif mod_stats["mean"] < 5.0:
                print("   ✅ Good performance (< 5s per AI request)")
            elif mod_stats["mean"] < 10.0:
                print("   ⚠️  Acceptable performance (< 10s per AI request)")
            else:
                print("   ❌ Poor performance (> 10s per AI request)")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if health_stats.get("mean", 0) > 0.1:
            print("   • Consider adding caching for health checks")
        if mod_stats.get("mean", 0) > 5.0:
            print("   • AI processing is slow - consider model optimization")
        if len(self.results["concurrent"]) < CONCURRENT_REQUESTS * 0.8:
            print("   • High failure rate in concurrent requests - check resource limits")
        if concurrent_stats.get("mean", 0) > mod_stats.get("mean", 0) * 2:
            print("   • Concurrent performance degradation - consider scaling")
        
        print("\n" + "=" * 60)

def main():
    """Main performance monitoring execution"""
    try:
        monitor = PerformanceMonitor()
        monitor.run_performance_tests()
    except KeyboardInterrupt:
        print("\n\n⚡ Performance monitoring interrupted")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Performance monitoring failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 