# Podcast Visualizer Backend

A powerful Flask-based API that transforms podcast content into engaging visual clips using AI-powered transcription and key moment extraction.

## 🚀 Features

- **Audio Podcast Processing**: Convert audio podcasts into visual clips with AI-generated content
- **AI Image Generation**: Create custom visuals using Vertex AI Imagen for unique podcast clips
- **Video Podcast Processing**: Extract key moments from video podcasts with synchronized captions
- **Abstract Summaries**: Generate structured markdown summaries with key insights
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
    ├── key_moment.py     # Audio podcast processing (stock videos)
    ├── ai_key_moment.py  # Audio podcast processing (AI images)
    ├── video_processing.py # Video podcast processing
    └── vertex_ai_helper.py # Vertex AI utilities
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

   # Cloudinary (File Storage)
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret

   # Pexels (Stock Videos)
   PEXELS_API_KEY=your_pexels_api_key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## 🎯 Quick Start

1. **Test with audio podcast key moments (stock videos):**

   ```bash
   curl -X POST http://localhost:5000/api/podcast/audio-podcast-key-moments \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/podcast.mp3"}'
   ```

2. **Test with AI-generated images:**

   ```bash
   curl -X POST http://localhost:5000/api/podcast/audio-podcast-ai-key-moments \
     -H "Content-Type: application/json" \
     -d '{"audio_url": "https://example.com/podcast.mp3"}'
   ```

3. **Generate abstract summary:**
   ```bash
   curl -X POST http://localhost:5000/api/podcast/abstract-summary \
     -H "Content-Type: application/json" \
     -d '{"podcast_url": "https://example.com/podcast.mp3"}'
   ```

## 📚 API Endpoints

### 1. Audio Podcast Key Moments

**POST** `/api/podcast/audio-podcast-key-moments`

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

### 2. Audio Podcast AI Key Moments

**POST** `/api/podcast/audio-podcast-ai-key-moments`

Processes audio podcasts and creates visual clips with AI-generated images instead of stock footage.

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
    "https://res.cloudinary.com/your_cloud/video/upload/ai_keymoment_1.mp4",
    "https://res.cloudinary.com/your_cloud/video/upload/ai_keymoment_2.mp4"
  ]
}
```

**Process Flow:**

1. Downloads audio from provided URL
2. Transcribes using local OpenAI Whisper
3. Analyzes transcript with Vertex AI Gemini for key moments and image prompts
4. Generates 5-6 AI images per moment using Vertex AI Imagen
5. Generates TTS audio for moment summaries
6. Creates video clips from AI-generated images with captions
7. Uploads to Cloudinary and returns URLs

**Features:**

- **AI-Generated Visuals**: Creates unique, contextually relevant images for each moment
- **Custom Image Prompts**: Generates 5-6 detailed prompts per key moment
- **High-Quality Images**: Uses Vertex AI Imagen 4.0 for professional-grade visuals
- **Portrait Format**: Optimized 9:16 aspect ratio for social media
- **Synchronized Captions**: Text overlays matching the spoken content

### 3. Video Podcast Key Moments

**POST** `/api/podcast/video-podcast-key-moments`

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

### 4. Abstract Summary

**POST** `/api/podcast/abstract-summary`

Generates a well-formatted markdown summary from any podcast (audio or video) with key points and takeaways.

**Request Body:**

```json
{
  "podcast_url": "https://example.com/podcast.mp3"
}
```

**Response:**

```json
{
  "summary": "## Overview\n\nI discussed the fundamental challenges facing modern AI development, particularly around ethical considerations and responsible deployment. My main argument centered on the importance of transparency in AI systems and how we can build trust through open communication.\n\n## Key Points\n\n- **Data Privacy**: I emphasized the critical need for protecting user data while enabling AI innovation\n- **Algorithmic Bias**: We explored how unconscious biases can creep into AI systems and methods to detect them\n- **Human Oversight**: I argued for maintaining human control in automated decision-making processes\n- **Transparency**: The importance of making AI systems explainable and understandable to end users\n\n## Main Takeaways\n\n- Organizations must prioritize ethical AI practices from the ground up\n- Building trust requires consistent transparency and open communication\n- Technical solutions alone aren't enough - we need policy and cultural changes\n- The future of AI depends on how well we balance innovation with responsibility"
}
```

**Process Flow:**

1. Auto-detects file type (audio/video) from URL
2. Downloads and transcribes using local OpenAI Whisper
3. Analyzes full transcript with Vertex AI Gemini 2.5 Flash
4. Generates structured markdown summary with overview, key points, and takeaways
5. Returns formatted summary maintaining speaker's voice and perspective

**Features:**

- **Markdown Formatting**: Clean, readable structure with headers and bullet points
- **Smart Detection**: Automatically handles both audio and video files
- **Speaker's Voice**: Maintains first-person perspective ("I discussed...")
- **Structured Content**: Overview, key points, and main takeaways sections
- **Key Insights**: Captures main arguments and actionable insights
- **Natural Flow**: Coherent narrative structure with clear organization

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
2. Enable Vertex AI API and Imagen API
3. Create a service account with Vertex AI permissions
4. Download service account JSON and encode as base64
5. Set the GCP_PROJECT_ID to your project ID

### Image Generation Setup

- Uses Vertex AI Imagen 4.0 for AI-generated images
- Requires access to Imagen preview models
- Configured for 9:16 aspect ratio (portrait mode)
- Supports custom safety filters and watermarking

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
