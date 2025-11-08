from transcribe import transcribe_audio
from analyze import analyze_transcript
from processTranscript import improve_transcript

audio_file = "sample_audio.mp3"

# 1️⃣ Transcribe
transcript = transcribe_audio(audio_file)
print("\nTranscript preview:\n", transcript[:200])

# 2️⃣ Analyze
analysis_result = analyze_transcript(transcript)
print("\nAnalysis:\n", analysis_result)

# 3️⃣ Improve
improved_result = improve_transcript(transcript)
print("\nImproved transcript:\n", improved_result)