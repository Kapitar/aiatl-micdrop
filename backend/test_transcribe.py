#!/usr/bin/env python3
"""
Simple test to verify the speech transcription endpoint works correctly.
"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_transcribe(audio_file: str):
    """Test transcription endpoint"""
    print(f"Testing transcription with: {audio_file}")
    print("-" * 60)
    
    if not Path(audio_file).exists():
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    # Test with no language code (should auto-detect)
    print("\n1. Testing auto-detect (no language code)...")
    with open(audio_file, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/speech/transcribe",
            files={'audio': f}
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Transcription length: {len(result['original_transcription'])} chars")
        print(f"Preview: {result['original_transcription'][:150]}...")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(f"Error: {response.text}")
        return False
    
    # Test with explicit language code
    print("\n2. Testing with language code 'eng'...")
    with open(audio_file, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/speech/transcribe",
            files={'audio': f},
            data={'language_code': 'eng'}
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success! Transcription length: {len(result['original_transcription'])} chars")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(f"Error: {response.text}")
        return False
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60)
    return True

def test_health():
    """Test health endpoint"""
    print("Testing API health...")
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ API is healthy")
        return True
    else:
        print("❌ API is not responding")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Speech Transcription Test")
    print("="*60)
    print()
    
    # Check if server is running
    try:
        if not test_health():
            print("\n⚠️  Server is not running. Start it with:")
            print("  uvicorn main:app --reload")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server at", BASE_URL)
        print("\n⚠️  Start the server with:")
        print("  uvicorn main:app --reload")
        sys.exit(1)
    
    # Get audio file from command line or prompt
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        print("\nUsage: python test_transcribe.py <audio_file>")
        print("\nExample:")
        print("  python test_transcribe.py speech.mp3")
        print("\nOr provide audio file path now:")
        audio_file = input("Audio file path: ").strip()
    
    if audio_file:
        test_transcribe(audio_file)
    else:
        print("No audio file provided. Exiting.")
