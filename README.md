# Podcast Visualizer Backend

A powerful Flask-based API that transforms podcast content into engaging visual clips using AI-powered transcription and key moment extraction.

## 🚀 Features

- **Audio Podcast Processing**: Convert audio podcasts into visual clips with AI-generated content
- **Video Podcast Processing**: Extract key moments from video podcasts with synchronized captions
- **AI-Powered Analysis**: Uses Vertex AI Gemini 2.5 Flash for intelligent key moment detection
- **Automatic Transcription**: Local OpenAI Whisper integration for accurate speech-to-text
- **Smart Captioning**: Real-time synchronized captions with 4-word chunking
- **Cloud Storage**: Automatic upload to Cloudinary for easy distribution
- **Stock Video Integration**: Pexels API integration for visual enhancement (audio podcasts)

## 🏗️ Architecture

```
├── app.py                 # Flask application entry point
├── routes/
│   └── podcast_routes.py # API route definitions
├── controllers/
│   └── podcast_controller.py # Business logic
├── services/
│   └── cloudinary_service.py # Cloud storage integration
└── utils/
    ├── transcription.py   # Audio/video transcription
    ├── key_moment.py     # Audio podcast processing
    └── video_processing.py # Video podcast processing
```

## 📋 Prerequisites

- Python 3.9+
- FFmpeg (for video processing)
- Google Cloud Platform account (for Vertex AI)
- Cloudinary account (for file hosting)
- Pexels API key (for stock videos)

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/pankaj0695/podcast-visualizer-backend.git
   cd podcast-visualizer-backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

   Configure the following variables in `.env`:

   ```env
   # Google Cloud (Vertex AI)
   GOOGLE_CREDENTIALS_JSON_BASE64=your_base64_encoded_service_account_json
   GCP_PROJECT_ID=your_gcp_project_id
   LOCATION=us-central1
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## 📚 API Endpoints

### 1. Audio Podcast Key Moments

**POST** `/audio-podcast-key-moments`

Processes audio podcasts and creates visual clips with AI-generated content and stock videos.

**Request Body:**

```json
{
  "audio_url": "https://example.com/podcast.mp3"
}
```

**Response:**

```json
{
  "video_urls": [
    "https://res.cloudinary.com/your_cloud/video/upload/keymoment_1.mp4",
    "https://res.cloudinary.com/your_cloud/video/upload/keymoment_2.mp4"
  ]
}
```

**Process Flow:**

1. Downloads audio from provided URL
2. Transcribes using local OpenAI Whisper
3. Analyzes transcript with Vertex AI Gemini for key moments
4. Generates TTS audio for moment summaries
5. Fetches relevant stock videos from Pexels
6. Creates composite videos with captions
7. Uploads to Cloudinary and returns URLs

### 2. Video Podcast Key Moments

**POST** `/video-podcast-key-moments`

Extracts key moments from video podcasts with synchronized captions from the original transcript.

**Request Body:**

```json
{
  "video_url": "https://example.com/podcast.mp4"
}
```

**Response:**

```json
{
  "video_urls": [
    "https://res.cloudinary.com/your_cloud/video/upload/clip_1.mp4",
    "https://res.cloudinary.com/your_cloud/video/upload/clip_2.mp4"
  ]
}
```

**Process Flow:**

1. Downloads video from provided URL
2. Transcribes using local OpenAI Whisper with word timestamps
3. Analyzes transcript with Vertex AI Gemini for 30-second key moments
4. Extracts video clips for identified moments
5. Adds synchronized captions (4-word chunks) at the bottom
6. Uploads processed clips to Cloudinary

## 🧠 How It Works

### Transcription Engine

- Uses **OpenAI Whisper** locally for high-quality speech recognition
- Supports both audio and video files
- Provides word-level timestamps for precise synchronization

### AI Key Moment Detection

- **Vertex AI Gemini 2.5 Flash** analyzes transcript content
- Identifies 2-3 most engaging moments (25-35 seconds each)
- For audio: Generates keywords and first-person summaries
- For video: Provides titles and time ranges

### Caption Generation

- Real-time synchronized captions
- 4-word chunking for optimal readability
- Bottom positioning with semi-transparent background
- Matches speaker timing for natural flow

### Video Processing

- **MoviePy** for video manipulation
- **PIL** for caption image generation
- **FFmpeg** backend for encoding
- Automatic cleanup of temporary files

## 🔧 Configuration

### Vertex AI Setup

1. Create a Google Cloud Platform project
2. Enable Vertex AI API
3. Create a service account with Vertex AI permissions
4. Download service account JSON and encode as base64

### Cloudinary Setup

1. Sign up at [Cloudinary](https://cloudinary.com/)
2. Get your cloud name, API key, and secret from dashboard
3. Configure video upload settings for optimal delivery

### Pexels Integration

1. Get free API key from [Pexels](https://www.pexels.com/api/)
2. Used for fetching stock videos based on keywords
3. Supports portrait orientation for social media

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
