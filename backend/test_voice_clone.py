#!/usr/bin/env python3
"""
Test voice cloning endpoint (requires paid ElevenLabs plan with IVC access)
"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_voice_cloning(audio_file: str, output_file: str = "improved_speech.mp3"):
    """Test the complete voice cloning workflow"""
    print(f"Testing voice cloning with: {audio_file}")
    print("-" * 60)
    
    if not Path(audio_file).exists():
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    print("\n⚠️  Note: This requires a paid ElevenLabs plan with IVC access")
    print("Processing: transcribe → improve → clone → generate...")
    print("This may take 30-60 seconds...\n")
    
    try:
        with open(audio_file, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/speech/clone-and-improve",
                files={'audio': f},
                data={
                    'improvement_focus': 'clarity and structure',
                    'language_code': 'eng'
                },
                timeout=120  # 2 minute timeout
            )
        
        if response.status_code == 200:
            # Save the improved audio
            with open(output_file, 'wb') as out:
                out.write(response.content)
            
            print(f"✅ Success!")
            print(f"Improved audio saved to: {output_file}")
            print(f"Audio size: {len(response.content):,} bytes")
            
            # Print headers with metadata
            if 'X-Original-Transcription' in response.headers:
                transcription = response.headers['X-Original-Transcription']
                print(f"\nOriginal transcription (preview):")
                print(f"  {transcription[:150]}...")
            
            if 'X-Audio-Size' in response.headers:
                print(f"Audio size from header: {response.headers['X-Audio-Size']} bytes")
            
            print(f"\n🎧 Play the improved audio:")
            print(f"  afplay {output_file}  # macOS")
            print(f"  # or open {output_file} in your media player")
            
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (this can take a while for voice cloning)")
        print("Try with a shorter audio file or increase timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_detailed_response(audio_file: str):
    """Test the detailed JSON response endpoint"""
    print(f"\nTesting detailed response with: {audio_file}")
    print("-" * 60)
    
    if not Path(audio_file).exists():
        print(f"❌ Audio file not found: {audio_file}")
        return False
    
    print("This returns JSON with transcription, improvements, and base64 audio...")
    print("Processing...\n")
    
    try:
        with open(audio_file, 'rb') as f:
            response = requests.post(
                f"{BASE_URL}/speech/clone-and-improve-detailed",
                files={'audio': f},
                data={
                    'improvement_focus': 'persuasiveness',
                    'language_code': 'eng'
                },
                timeout=120
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"\nOriginal transcription: {len(result['original_transcription'])} chars")
            print(f"Improved speech: {len(result['improved_content']['improved_speech'])} chars")
            print(f"Number of suggestions: {len(result['improved_content']['suggestions'])}")
            print(f"Audio generated: {result['audio_generated']}")
            print(f"Audio size: {result['audio_size']:,} bytes")
            
            print(f"\nFirst suggestion:")
            if result['improved_content']['suggestions']:
                print(f"  {result['improved_content']['suggestions'][0]}")
            
            print(f"\nSummary:")
            print(f"  {result['improved_content']['summary']}")
            
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

if __name__ == "__main__":
    print("="*60)
    print("Voice Cloning Test")
    print("="*60)
    print()
    
    # Check server
    if not check_server():
        print("❌ Server not running at", BASE_URL)
        print("\nStart the server with:")
        print("  uvicorn main:app --reload")
        sys.exit(1)
    
    print("✅ Server is running")
    print()
    
    # Get audio file
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        print("Usage: python test_voice_clone.py <audio_file> [output_file]")
        print("\nExample:")
        print("  python test_voice_clone.py speech.mp3")
        print("  python test_voice_clone.py speech.mp3 my_improved.mp3")
        print()
        print("Requirements:")
        print("  - Audio file with at least 30 seconds of speech")
        print("  - Paid ElevenLabs plan with IVC access")
        print()
        audio_file = input("Audio file path (or Enter to skip): ").strip()
        if not audio_file:
            print("No audio file provided. Exiting.")
            sys.exit(0)
    
    output_file = sys.argv[2] if len(sys.argv) > 2 else "improved_speech.mp3"
    
    # Run tests
    print("\n" + "="*60)
    print("Test 1: Voice Cloning (Audio File Output)")
    print("="*60)
    success1 = test_voice_cloning(audio_file, output_file)
    
    if success1:
        print("\n" + "="*60)
        print("Test 2: Detailed JSON Response (Optional)")
        print("="*60)
        response = input("\nRun detailed test? (y/N): ").strip().lower()
        if response == 'y':
            test_detailed_response(audio_file)
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)
