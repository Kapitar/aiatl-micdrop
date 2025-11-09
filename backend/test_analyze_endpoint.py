#!/usr/bin/env python3
"""
Test script to verify the /analyze/video endpoint handles optional audio parameter correctly.
"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_analyze_with_video_only():
    """Test analyzing video without audio file"""
    print("Testing /analyze/video endpoint...")
    print("-" * 60)
    
    # Check if server is running
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not responding")
            return False
        print("✅ Server is running\n")
    except:
        print("❌ Cannot connect to server. Start it with:")
        print("  cd backend && uvicorn main:app --reload")
        return False
    
    # Create a simple test video file if needed
    test_video = Path("test_video.mp4")
    if not test_video.exists():
        print("⚠️  No test video found. Please provide a video file.")
        video_path = input("Enter path to a video file (or press Enter to skip): ").strip()
        if not video_path:
            print("Skipping test.")
            return False
        test_video = Path(video_path)
    
    if not test_video.exists():
        print(f"❌ Video file not found: {test_video}")
        return False
    
    print(f"📹 Using video: {test_video}")
    print("Uploading video for analysis (this may take a minute)...\n")
    
    try:
        with open(test_video, 'rb') as f:
            # Test 1: Send only video file
            print("Test 1: Sending video only (no audio parameter)")
            response = requests.post(
                f"{BASE_URL}/analyze/video",
                files={'video': f},
                timeout=300  # 5 minute timeout for video processing
            )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Analysis completed.")
            print(f"\nResponse structure:")
            print(f"  - non_verbal: {list(result.get('non_verbal', {}).keys())}")
            print(f"  - delivery: {list(result.get('delivery', {}).keys())}")
            print(f"  - content: {list(result.get('content', {}).keys())}")
            print(f"  - overall_feedback: {list(result.get('overall_feedback', {}).keys())}")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Video processing can take several minutes.")
        print("   The video might be too long or complex.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_analyze_with_empty_audio():
    """Test that empty audio parameter doesn't cause errors"""
    print("\n" + "="*60)
    print("Test 2: Testing with empty audio parameter")
    print("="*60)
    
    test_video = Path("test_video.mp4")
    if not test_video.exists():
        print("⚠️  Skipping (no test video)")
        return True
    
    try:
        with open(test_video, 'rb') as f:
            # Send with empty audio string (this was causing the error)
            response = requests.post(
                f"{BASE_URL}/analyze/video",
                files={'video': f},
                data={'audio': ''},  # This should be handled gracefully
                timeout=300
            )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Empty audio parameter handled correctly.")
            return True
        else:
            print(f"Response: {response.text}")
            if "Expected UploadFile" in response.text:
                print("❌ Still getting UploadFile error with empty string")
                return False
            else:
                print("⚠️  Different error occurred")
                return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Analyze Endpoint Test")
    print("="*60)
    print()
    
    success1 = test_analyze_with_video_only()
    
    # Only run second test if first succeeded
    if success1:
        success2 = test_analyze_with_empty_audio()
    else:
        success2 = False
    
    print("\n" + "="*60)
    if success1 and success2:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("="*60)
