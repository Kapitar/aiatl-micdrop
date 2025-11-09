# Speech Coach

Speech Coach is an AI-powered application that provides comprehensive analysis and feedback on speech performance. Users can upload or record videos of themselves speaking, receive detailed feedback across multiple dimensions, and interact with an AI coach to improve their presentation skills.

This project was submitted to AI ATL.

## Overview

Speech Coach analyzes video recordings to provide structured feedback on three main categories:

- **Non-Verbal Communication**: Eye contact, gestures, and posture
- **Delivery**: Clarity and enunciation, intonation, and eloquence (including filler word analysis)
- **Content**: Organization and flow, persuasiveness and impact, and clarity of message

The application also includes advanced features such as speech transcription, content improvement suggestions, and voice cloning to generate improved versions of speeches in the user's own voice.

## Features

### Video Analysis
Upload or record a video of yourself speaking and receive comprehensive feedback with:
- Effectiveness scores for each sub-category
- Timestamped feedback for specific moments
- Overall summary with strengths, areas for improvement, and prioritized actions

### Interactive Chat
Ask questions about your feedback in a conversational interface. The AI coach provides specific, actionable advice grounded in your analysis results.

### Speech Improvement
- Transcribe audio to text using advanced speech recognition
- Generate improved versions of your speech content
- Clone your voice and generate audio of the improved speech
- Complete workflow: transcribe, improve, clone, and generate in one call

### Video Replay with Timestamps
Watch your video alongside timestamped feedback, allowing you to jump to specific moments and see what feedback applies to each section.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI
- **Google Gemini** - AI model for video analysis and content improvement
- **ElevenLabs** - Speech transcription and voice cloning services
- **Pydantic** - Data validation and settings management
- **pydub** - Audio processing
- **Python 3.10+** - Programming language

### Frontend
- **Next.js 16** - React framework with App Router
- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS 4** - Utility-first CSS framework
- **React Markdown** - Markdown rendering for chat responses

## Project Structure

```
speech-coach/
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── routers/        # API route handlers
│   │   ├── services/       # Business logic and AI integration
│   │   ├── config.py       # Configuration management
│   │   └── models.py       # Pydantic data models
│   ├── prompts/            # AI prompt templates
│   ├── main.py             # FastAPI application entry point
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # Next.js frontend application
    ├── app/
    │   ├── page.tsx        # Home page (video upload/recording)
    │   ├── analysis/       # Analysis results page
    │   └── lib/
    │       └── api.ts      # API client functions
    ├── package.json        # Node.js dependencies
    └── tsconfig.json       # TypeScript configuration
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- FFmpeg (for video/audio processing)
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Google AI Studio API key (for Gemini)
- ElevenLabs API key (for speech features; paid plan required for voice cloning)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add:
# GOOGLE_AI_STUDIO_API_KEY=your_key_here
# ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000` with interactive documentation at `http://127.0.0.1:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Usage

1. **Upload or Record**: On the home page, either upload a video file or record one directly using your camera and microphone.

2. **Analysis**: After submitting your video, the system will analyze it and redirect you to the Replay page where you can watch your video.

3. **Review Feedback**: Navigate to the Dashboard tab to see detailed scores and feedback across all categories.

4. **Interactive Chat**: Use the Chat tab to ask specific questions about your performance and get personalized advice.

5. **Generate Improved Speech**: On the Dashboard, use the "Generate Ideal Speech" feature to get an improved version of your speech in your own voice.

## API Endpoints

### Analysis
- `POST /analyze/video` - Upload video for comprehensive feedback

### Chat
- `POST /chat/start` - Start a chat session with feedback JSON
- `POST /chat/message` - Send a message in an active chat session

### Speech Improvement
- `POST /speech/transcribe` - Transcribe audio to text
- `POST /speech/improve` - Transcribe and improve speech content
- `POST /speech/clone-and-improve` - Complete workflow with audio generation
- `POST /speech/clone-and-improve-detailed` - Same as above with detailed JSON response

For detailed API documentation, visit `http://127.0.0.1:8000/docs` when the backend is running.

## Development

### Backend Testing
```bash
# Structure sanity check
python test_structure.py

# Test transcription
python test_transcribe.py path/to/audio.mp3

# Test voice cloning
python test_voice_clone.py path/to/audio.mp3
```

### Frontend Development
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## Configuration

### Backend Configuration
- Environment variables are managed in `.env` (not committed to version control)
- Model settings and API keys are configured in `app/config.py`
- Prompt templates can be customized in `prompts/`

### Frontend Configuration
- API base URL is configured via `NEXT_PUBLIC_API_URL` environment variable (defaults to `http://localhost:8000`)
- TypeScript path aliases are configured in `tsconfig.json`

## Production Considerations

- Restrict CORS to known origins
- Add authentication and rate limiting
- Persist chat conversations in a database
- Implement proper logging and error handling
- Add retries and polling for file processing
- Validate and sanitize all user inputs
- Use environment-specific configuration files

## License

Proprietary - Internal use for the Speech Coach project unless stated otherwise.

## Submission

This project was submitted to AI ATL.
